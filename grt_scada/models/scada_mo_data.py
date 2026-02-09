"""
SCADA Manufacturing Order Data Model
Model untuk data MO yang dikirim ke middleware
"""

from odoo import models, fields, api
from datetime import datetime


class ScadaMoData(models.Model):
    """Model untuk SCADA Manufacturing Order Data"""
    _name = 'scada.mo.data'
    _description = 'SCADA Manufacturing Order Data'
    _order = 'created_at desc'
    _inherit = 'scada.base'

    # Manufacturing Order Reference
    manufacturing_order_id = fields.Many2one(
        'mrp.production',
        string='Manufacturing Order',
        required=True,
        ondelete='cascade',
        help='Manufacturing order yang direferensikan'
    )
    mo_name = fields.Char(
        string='MO Name',
        related='manufacturing_order_id.name',
        readonly=True,
        store=True,
        help='Nama/nomor MO'
    )

    # Product & Quantity Info
    product_id = fields.Many2one(
        'product.product',
        string='Product',
        related='manufacturing_order_id.product_id',
        readonly=True,
        store=True,
        help='Product yang diproduksi'
    )
    product_qty = fields.Float(
        string='Quantity',
        digits=(12, 3),
        related='manufacturing_order_id.product_qty',
        readonly=True,
        store=True,
        help='Quantity untuk diproduksi'
    )
    qty_produced = fields.Float(
        string='Produced Qty',
        digits=(12, 3),
        compute='_compute_mo_actuals',
        readonly=True,
        help='Jumlah produk selesai (diambil dari MO finished moves)'
    )
    qty_consumed = fields.Float(
        string='Consumed Qty',
        digits=(12, 3),
        compute='_compute_mo_actuals',
        readonly=True,
        help='Jumlah material terpakai (diambil dari MO raw moves)'
    )

    # Equipment & Production Info
    equipment_id = fields.Many2one(
        'scada.equipment',
        string='Production Equipment',
        help='Equipment yang akan menjalankan MO'
    )
    production_line_id = fields.Many2one(
        'mrp.workcenter',
        string='Work Center',
        help='Work center untuk MO'
    )

    # Dates
    date_start_planned = fields.Datetime(
        string='Planned Start Date',
        related='manufacturing_order_id.date_planned_start',
        readonly=True,
        store=True,
        help='Tanggal mulai yang direncanakan'
    )
    date_end_planned = fields.Datetime(
        string='Planned End Date',
        related='manufacturing_order_id.date_planned_finished',
        readonly=True,
        store=True,
        help='Tanggal selesai yang direncanakan'
    )
    date_start_actual = fields.Datetime(
        string='Actual Start Date',
        help='Tanggal mulai sebenarnya (dari equipment)'
    )
    date_end_actual = fields.Datetime(
        string='Actual End Date',
        help='Tanggal selesai sebenarnya (dari equipment)'
    )

    # Status Info
    mo_status = fields.Selection(
        [
            ('draft', 'Draft'),
            ('confirmed', 'Confirmed'),
            ('planned', 'Planned'),
            ('progress', 'In Progress'),
            ('done', 'Done'),
            ('cancel', 'Cancelled'),
        ],
        string='MO Status',
        related='manufacturing_order_id.state',
        readonly=True,
        store=True,
        help='Status dari manufacturing order'
    )
    status_code = fields.Char(
        string='Status Code',
        compute='_compute_status_code',
        store=True,
        help='Kode status untuk middleware (PLC)'
    )

    # Data Export Info
    last_sent_to_middleware = fields.Datetime(
        string='Last Sent to Middleware',
        readonly=True,
        help='Waktu terakhir data dikirim ke middleware'
    )
    send_count = fields.Integer(
        string='Send Count',
        default=0,
        readonly=True,
        help='Berapa kali data sudah dikirim ke middleware'
    )

    # Raw Data untuk Middleware
    raw_data_json = fields.Text(
        string='Raw Data (JSON)',
        help='Raw data dalam format JSON untuk middleware'
    )

    notes = fields.Text(
        string='Notes',
        help='Catatan tambahan'
    )

    @api.depends('mo_status')
    def _compute_status_code(self):
        """Compute status code untuk middleware"""
        status_mapping = {
            'draft': '0',
            'confirmed': '1',
            'planned': '1',
            'progress': '2',
            'done': '3',
            'cancel': '9',
        }
        for record in self:
            record.status_code = status_mapping.get(record.mo_status, '0')

    @api.depends(
        'manufacturing_order_id',
        'manufacturing_order_id.move_finished_ids.quantity_done',
        'manufacturing_order_id.move_finished_ids.state',
        'manufacturing_order_id.move_raw_ids.quantity_done',
        'manufacturing_order_id.move_raw_ids.state'
    )
    def _compute_mo_actuals(self):
        for record in self:
            mo = record.manufacturing_order_id
            if not mo:
                record.qty_produced = 0.0
                record.qty_consumed = 0.0
                continue

            finished_qty = sum(
                move.quantity_done for move in mo.move_finished_ids
                if move.state != 'cancel'
            )
            consumed_qty = sum(
                move.quantity_done for move in mo.move_raw_ids
                if move.state != 'cancel'
            )

            record.qty_produced = finished_qty
            record.qty_consumed = consumed_qty

    def _prepare_data_for_middleware(self):
        """Prepare data format untuk middleware"""
        self.ensure_one()
        return {
            'mo_id': self.mo_name,
            'product_id': self.product_id.default_code or self.product_id.id,
            'product_name': self.product_id.name,
            'quantity': self.product_qty,
            'status': self.status_code,
            'status_text': self.mo_status,
            'date_start': self.date_start_planned.isoformat() if self.date_start_planned else None,
            'date_end': self.date_end_planned.isoformat() if self.date_end_planned else None,
            'equipment_id': self.equipment_id.equipment_code if self.equipment_id else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    def get_mo_data_for_equipment(self, equipment_id):
        """Get MO data untuk specific equipment"""
        return self.search([
            ('equipment_id', '=', equipment_id),
            ('mo_status', 'in', ['planned', 'progress']),
            ('sync_status', '!=', 'failed'),
        ])

    def mark_sent_to_middleware(self):
        """Mark data sebagai sudah dikirim ke middleware"""
        self.write({
            'last_sent_to_middleware': datetime.now(),
            'send_count': self.send_count + 1,
            'sync_status': 'synced',
        })

    @api.model
    def apply_material_consumption(self, consumption_data):
        """
        Apply material consumption langsung ke MO raw moves.

        Tidak membuat record scada.material.consumption.
        """
        try:
            from ..services.validation_service import ValidationService

            is_valid, error_msg = ValidationService.validate_material_consumption_data(
                self.env, consumption_data
            )
            if not is_valid:
                return {
                    'status': 'error',
                    'message': f'Validation failed: {error_msg}',
                }

            equipment = self.env['scada.equipment'].search([
                ('equipment_code', '=', consumption_data.get('equipment_id'))
            ], limit=1)
            if not equipment:
                return {
                    'status': 'error',
                    'message': f'Equipment not found: {consumption_data.get("equipment_id")}',
                }

            material = self._get_material_from_payload(consumption_data)
            if not material:
                return {
                    'status': 'error',
                    'message': 'Product not found or invalid product payload',
                }

            mo_record = self._get_mo_from_consumption_payload(consumption_data)
            if not mo_record:
                return {
                    'status': 'error',
                    'message': 'MO ID is required',
                }

            moves = self._find_raw_moves_for_material(mo_record, material)
            if not moves:
                return {
                    'status': 'error',
                    'message': 'No raw material move found for this product in MO',
                }

            quantity = float(consumption_data.get('quantity', 0))
            applied_qty, move_ids = self._apply_consumption_to_moves(
                moves, quantity, allow_overconsume=True
            )

            timestamp_value = consumption_data.get('timestamp') or datetime.now()
            if isinstance(timestamp_value, str):
                try:
                    timestamp_value = fields.Datetime.from_string(timestamp_value)
                except Exception:
                    timestamp_value = datetime.now()

            self._log_equipment_material_consumption(
                equipment=equipment,
                material=material,
                mo_record=mo_record,
                quantity=applied_qty,
                timestamp=timestamp_value,
            )

            return {
                'status': 'success',
                'message': 'Material consumption applied to MO moves',
                'mo_id': mo_record.name,
                'applied_qty': applied_qty,
                'move_ids': move_ids,
            }

        except Exception as e:
            return {
                'status': 'error',
                'message': f'Error: {str(e)}',
            }

    def _get_material_from_payload(self, consumption_data):
        material_id = consumption_data.get('material_id') or consumption_data.get('product_id')
        product_tmpl_id = consumption_data.get('product_tmpl_id')

        if material_id:
            try:
                material_id = int(material_id)
            except (TypeError, ValueError):
                return False
            material = self.env['product.product'].browse(material_id)
            return material if material.exists() else False

        if product_tmpl_id:
            try:
                product_tmpl_id = int(product_tmpl_id)
            except (TypeError, ValueError):
                return False
            template = self.env['product.template'].browse(product_tmpl_id)
            if not template.exists() or not template.product_variant_id:
                return False
            return template.product_variant_id

        return False

    def _get_mo_from_consumption_payload(self, consumption_data):
        mo_value = consumption_data.get('mo_id') or consumption_data.get('manufacturing_order_id')
        if not mo_value:
            return False

        try:
            if isinstance(mo_value, int) or str(mo_value).isdigit():
                mo_record = self.env['mrp.production'].browse(int(mo_value))
            else:
                mo_record = self.env['mrp.production'].search([
                    ('name', '=', str(mo_value))
                ], limit=1)
        except Exception:
            return False

        return mo_record if mo_record and mo_record.exists() else False

    def _find_raw_moves_for_material(self, mo_record, material):
        return mo_record.move_raw_ids.filtered(
            lambda move: move.product_id.id == material.id and move.state not in ['done', 'cancel']
        )

    def _apply_consumption_to_moves(self, moves, quantity, allow_overconsume=True):
        qty_remaining = quantity
        move_ids = []

        for move in moves:
            if qty_remaining <= 0:
                break
            planned = move.product_uom_qty or 0.0
            done = move.quantity_done or 0.0
            remaining = max(planned - done, 0.0)
            if remaining == 0.0 and not allow_overconsume:
                add_qty = 0.0
            else:
                add_qty = qty_remaining if remaining == 0.0 else min(qty_remaining, remaining)
            if add_qty <= 0.0:
                continue
            move.quantity_done = done + add_qty
            qty_remaining -= add_qty
            move_ids.append(move.id)

        applied_qty = quantity - qty_remaining
        return applied_qty, move_ids

    def _log_equipment_material_consumption(self, equipment, material, mo_record, quantity, timestamp):
        if not equipment:
            return

        consumption_bom = 0.0
        if mo_record and mo_record.bom_id and mo_record.bom_id.product_qty:
            bom_line = mo_record.bom_id.bom_line_ids.filtered(
                lambda line: line.product_id.id == material.id
            )[:1]
            if bom_line:
                consumption_bom = (
                    bom_line.product_qty / mo_record.bom_id.product_qty
                ) * mo_record.product_qty

        self.env['scada.equipment.material'].create({
            'equipment_id': equipment.id,
            'product_id': material.id,
            'manufacturing_order_id': mo_record.id if mo_record else False,
            'consumption_actual': quantity,
            'consumption_bom': consumption_bom,
            'timestamp': timestamp,
            'active': True,
        })

    @api.model
    def create_from_mo(self, mo_id, equipment_id=None):
        """Create SCADA MO Data dari Manufacturing Order"""
        mo = self.env['mrp.production'].browse(mo_id)
        if not mo:
            return None

        scada_mo = self.create({
            'manufacturing_order_id': mo.id,
            'equipment_id': equipment_id,
        })
        return scada_mo

    # ===== XML-RPC Compatible Methods =====

    @api.model
    def get_mo_list_for_equipment(self, equipment_code, status=None, limit=50, offset=0):
        """
        Get MO list untuk specific equipment via XML-RPC
        
        Args:
            equipment_code: Equipment code
            status: Optional status filter ('planned', 'progress', 'done')
            limit: Max records (default 50)
            offset: Offset for pagination (default 0)
            
        Returns:
            Dict dengan MO list
            
        XML-RPC Usage:
            models.execute_kw(db, uid, pwd, 'scada.mo.data',
                             'get_mo_list_for_equipment', ['PLC01'],
                             {'status': 'planned', 'limit': 50})
        """
        equipment = self.env['scada.equipment'].search([
            ('equipment_code', '=', equipment_code)
        ], limit=1)

        if not equipment:
            return {
                'status': 'error',
                'message': f'Equipment "{equipment_code}" not found',
                'count': 0,
                'data': [],
            }

        domain = [('equipment_id', '=', equipment.id)]
        if status:
            domain.append(('mo_status', '=', status))

        records = self.search(domain, limit=limit, offset=offset, order='date_start_planned asc, id asc')
        data = []

        for record in records:
            data.append({
                'mo_id': record.mo_name,
                'product': record.product_id.display_name if record.product_id else None,
                'quantity': record.product_qty,
                'produced_qty': record.qty_produced,
                'consumed_qty': record.qty_consumed,
                'status': record.mo_status,
                'schedule_start': record.date_start_planned.isoformat() if record.date_start_planned else None,
                'schedule_end': record.date_end_planned.isoformat() if record.date_end_planned else None,
            })

        return {
            'status': 'success',
            'count': len(data),
            'data': data,
        }

    @api.model
    def acknowledge_mo(self, mo_record_id, payload_data):
        """
        Acknowledge Manufacturing Order from equipment
        
        Args:
            mo_record_id: MO Data record ID
            payload_data: Dict dengan acknowledge data
            
        Returns:
            Dict dengan result
        """
        try:
            mo_data = self.browse(mo_record_id)
            if not mo_data.exists():
                return {
                    'status': 'error',
                    'message': f'MO record {mo_record_id} not found',
                }

            # Update acknowledgment timestamp
            mo_data.write({
                'last_sent_to_middleware': datetime.now(),
                'send_count': mo_data.send_count + 1,
            })

            return {
                'status': 'success',
                'message': 'MO acknowledged successfully',
                'mo_id': mo_data.id,
            }

        except Exception as e:
            return {
                'status': 'error',
                'message': f'Error: {str(e)}',
            }

    @api.model
    def update_mo_status(self, mo_record_id, payload_data):
        """
        Update MO status from equipment
        
        Args:
            mo_record_id: MO Data record ID
            payload_data: Dict dengan status update
            
        Returns:
            Dict dengan result
        """
        try:
            mo_data = self.browse(mo_record_id)
            if not mo_data.exists():
                return {
                    'status': 'error',
                    'message': f'MO record {mo_record_id} not found',
                }

            # Update actual dates if provided
            update_data = {}
            if payload_data.get('date_start_actual'):
                update_data['date_start_actual'] = payload_data['date_start_actual']
            if payload_data.get('date_end_actual'):
                update_data['date_end_actual'] = payload_data['date_end_actual']

            if update_data:
                mo_data.write(update_data)

            return {
                'status': 'success',
                'message': 'MO status updated successfully',
                'mo_id': mo_data.id,
            }

        except Exception as e:
            return {
                'status': 'error',
                'message': f'Error: {str(e)}',
            }

    @api.model
    def mark_mo_done(self, mo_record_id, payload_data):
        """
        Mark MO as done from equipment
        
        Auto-populates material consumption from BoM if not recorded yet
        
        Args:
            mo_record_id: MO Data record ID
            payload_data: Dict dengan done data
                - equipment_id: Equipment code
                - mo_id: Manufacturing Order name (required)
                - finished_qty: Finished goods quantity (required)
                - date_end_actual: Actual completion datetime
                - auto_consume: True to auto-populate from BoM (default: True)
                - message: Optional completion message
            
        Returns:
            Dict dengan result
        """
        try:
            mo_data = self.browse(mo_record_id)
            if not mo_data.exists():
                return {
                    'status': 'error',
                    'message': f'MO record {mo_record_id} not found',
                }

            mo = mo_data.manufacturing_order_id
            if not mo:
                return {
                    'status': 'error',
                    'message': 'Manufacturing order is missing',
                }

            equipment = mo_data.equipment_id
            payload_equipment = payload_data.get('equipment_id')
            if not equipment and payload_equipment:
                equipment = self.env['scada.equipment'].search([
                    ('equipment_code', '=', payload_equipment)
                ], limit=1)
                if equipment:
                    mo_data.write({'equipment_id': equipment.id})

            mo_name = payload_data.get('mo_id')
            if not mo_name:
                return {
                    'status': 'error',
                    'message': 'mo_id is required',
                }
            if str(mo_name) != str(mo.name):
                return {
                    'status': 'error',
                    'message': f'mo_id mismatch: {mo_name}',
                }

            finished_qty = payload_data.get('finished_qty')
            if finished_qty is None:
                return {
                    'status': 'error',
                    'message': 'finished_qty is required',
                }
            try:
                finished_qty = float(finished_qty)
            except (TypeError, ValueError):
                return {
                    'status': 'error',
                    'message': 'finished_qty must be a number',
                }
            if finished_qty <= 0:
                return {
                    'status': 'error',
                    'message': 'finished_qty must be > 0',
                }

            finished_moves = mo.move_finished_ids.filtered(
                lambda move: move.product_id.id == mo.product_id.id and move.state not in ['done', 'cancel']
            )
            if not finished_moves:
                return {
                    'status': 'error',
                    'message': 'No finished product move found for this MO',
                }

            if hasattr(mo, 'qty_producing'):
                mo.qty_producing = finished_qty

            finished_moves[0].quantity_done = finished_qty

            # Update actual end date if provided
            if payload_data.get('date_end_actual'):
                mo_data.write({'date_end_actual': payload_data['date_end_actual']})

            # Auto-consume materials from BoM if enabled (default: True)
            auto_consume = payload_data.get('auto_consume', True)
            consumed_materials = []
            
            if auto_consume and mo.bom_id:
                consumed_materials = self._auto_consume_from_bom(mo, equipment)

            # Mark MO as done
            if mo.state not in ['done', 'cancel']:
                mo.sudo().button_mark_done()

            return {
                'status': 'success',
                'message': 'Manufacturing order marked as done',
                'mo_id': mo.name,
                'auto_consumed': len(consumed_materials),
                'materials': consumed_materials,
            }

        except Exception as e:
            return {
                'status': 'error',
                'message': f'Error: {str(e)}',
            }

    def _auto_consume_from_bom(self, mo, equipment):
        """
        Auto-populate material consumption from BoM
        
        Args:
            mo: Manufacturing Order record
            equipment: SCADA Equipment record
            
        Returns:
            List of created material consumption records
        """
        consumed_materials = []

        if not equipment:
            import logging
            _logger = logging.getLogger(__name__)
            _logger.warning('Auto-consume skipped: equipment is missing for MO %s', mo.name)
            return consumed_materials
        
        if not mo.bom_id:
            return consumed_materials

        # Get BoM lines
        bom_lines = mo.bom_id.bom_line_ids
        
        for line in bom_lines:
            # Calculate quantity based on MO quantity
            quantity = (line.product_qty / mo.bom_id.product_qty) * mo.product_qty
            
            try:
                moves = self._find_raw_moves_for_material(mo, line.product_id)
                applied_qty, move_ids = self._apply_consumption_to_moves(
                    moves, quantity, allow_overconsume=False
                )
                self._log_equipment_material_consumption(
                    equipment=equipment,
                    material=line.product_id,
                    mo_record=mo,
                    quantity=applied_qty,
                    timestamp=datetime.now(),
                )
                consumed_materials.append({
                    'material_code': line.product_id.default_code or line.product_id.name,
                    'material_name': line.product_id.name,
                    'quantity': applied_qty,
                    'uom': line.product_uom_id.name,
                    'move_ids': move_ids,
                })
                
            except Exception as e:
                # Log error but continue with other materials
                import logging
                _logger = logging.getLogger(__name__)
                _logger.error(f'Error auto-consuming {line.product_id.name}: {str(e)}')
                continue
        
        return consumed_materials
