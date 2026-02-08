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
        from ..services.middleware_service import MiddlewareService
        return MiddlewareService.get_mo_list(self.env, equipment_code, status, limit, offset)

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

            # Update actual end date if provided
            if payload_data.get('date_end_actual'):
                mo_data.write({'date_end_actual': payload_data['date_end_actual']})

            # Auto-consume materials from BoM if enabled (default: True)
            auto_consume = payload_data.get('auto_consume', True)
            consumed_materials = []
            
            if auto_consume and mo.bom_id:
                consumed_materials = self._auto_consume_from_bom(mo, mo_data.equipment_id)

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
        
        if not mo.bom_id:
            return consumed_materials

        # Get BoM lines
        bom_lines = mo.bom_id.bom_line_ids
        
        for line in bom_lines:
            # Calculate quantity based on MO quantity
            quantity = (line.product_qty / mo.bom_id.product_qty) * mo.product_qty
            
            # Check if already recorded in SCADA consumption
            existing = self.env['scada.material.consumption'].search([
                ('manufacturing_order_id', '=', mo.id),
                ('material_id', '=', line.product_id.id),
            ], limit=1)
            
            if existing:
                # Already recorded, skip
                continue
            
            # Create SCADA material consumption record
            try:
                consumption = self.env['scada.material.consumption'].create({
                    'equipment_id': equipment.id if equipment else False,
                    'material_id': line.product_id.id,
                    'quantity': quantity,
                    'manufacturing_order_id': mo.id,
                    'timestamp': datetime.now(),
                    'status': 'recorded',
                    'source': 'auto_bom',  # Mark as auto-generated
                })
                
                consumed_materials.append({
                    'material_code': line.product_id.default_code or line.product_id.name,
                    'material_name': line.product_id.name,
                    'quantity': quantity,
                    'uom': line.product_uom_id.name,
                    'record_id': consumption.id,
                })
                
            except Exception as e:
                # Log error but continue with other materials
                import logging
                _logger = logging.getLogger(__name__)
                _logger.error(f'Error auto-consuming {line.product_id.name}: {str(e)}')
                continue
        
        return consumed_materials
