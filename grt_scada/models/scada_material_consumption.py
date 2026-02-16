"""
SCADA Material Consumption Model
Model untuk tracking konsumsi material dari equipment/PLC
"""

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime


class ScadaMaterialConsumption(models.Model):
    """Model untuk SCADA Material Consumption Records"""
    _name = 'scada.material.consumption'
    _description = 'SCADA Material Consumption'
    _order = 'timestamp desc'
    _inherit = 'scada.base'

    # Basic Info
    equipment_id = fields.Many2one(
        'scada.equipment',
        string='Equipment',
        required=True,
        ondelete='restrict',
        help='Equipment yang mengkonsumsi material'
    )
    material_id = fields.Many2one(
        'product.product',
        string='Material',
        required=True,
        domain=[('type', '!=', 'service')],
        help='Material yang dikonsumsi'
    )
    quantity = fields.Float(
        string='Quantity Consumed',
        required=True,
        digits=(12, 3),
        help='Jumlah material yang dikonsumsi'
    )
    unit_of_measure = fields.Many2one(
        'uom.uom',
        string='Unit of Measure',
        related='material_id.uom_id',
        readonly=True,
        help='Unit dari material'
    )

    # Production Info
    manufacturing_order_id = fields.Many2one(
        'mrp.production',
        string='Manufacturing Order',
        help='Production order yang terkait (optional)'
    )
    production_line_id = fields.Many2one(
        'mrp.workcenter',
        string='Work Center',
        related='equipment_id.production_line_id',
        readonly=True,
        help='Work center dari equipment'
    )

    # Timestamp
    timestamp = fields.Datetime(
        string='Consumption Time',
        required=True,
        default=fields.Datetime.now,
        help='Waktu konsumsi material terjadi'
    )
    date_received = fields.Date(
        string='Date Received',
        compute='_compute_date_received',
        store=True,
        help='Tanggal data diterima'
    )

    # Data Source
    api_request_id = fields.Char(
        string='API Request ID',
        help='ID dari API request yang mengirim data ini'
    )
    batch_number = fields.Char(
        string='Batch Number',
        help='Nomor batch dari middleware'
    )
    source = fields.Selection(
        [
            ('manual', 'Manual Entry'),
            ('api', 'API/Middleware'),
            ('auto_bom', 'Auto from BoM'),
        ],
        string='Data Source',
        default='manual',
        required=True,
        help='Sumber data consumption (manual, API, atau auto-generate dari BoM)'
    )

    # Status & Tracking
    status = fields.Selection(
        [
            ('draft', 'Draft'),
            ('recorded', 'Recorded'),
            ('validated', 'Validated'),
            ('posted', 'Posted'),
            ('cancelled', 'Cancelled'),
        ],
        string='Status',
        default='draft',
        help='Status record konsumsi'
    )
    is_stock_moved = fields.Boolean(
        string='Stock Moved',
        default=False,
        help='Apakah stock sudah di-move di Odoo'
    )
    move_id = fields.Many2one(
        'stock.move',
        string='Stock Move',
        help='Stock move yang terkait'
    )

    # Notes
    notes = fields.Text(
        string='Notes',
        help='Catatan tambahan tentang konsumsi'
    )

    @api.depends('timestamp')
    def _compute_date_received(self):
        """Compute tanggal dari timestamp"""
        for record in self:
            if record.timestamp:
                record.date_received = record.timestamp.date()

    @api.constrains('quantity')
    def _check_quantity(self):
        """Validate quantity"""
        for record in self:
            if record.quantity <= 0:
                raise ValidationError("Quantity harus lebih dari 0")

    @api.constrains('timestamp')
    def _check_timestamp_not_future(self):
        """Validate timestamp tidak di masa depan"""
        for record in self:
            if record.timestamp > datetime.now():
                raise ValidationError(
                    "Timestamp tidak boleh di masa depan"
                )

    def action_validate(self):
        """Validate dan siapkan untuk dipost ke stock"""
        for record in self:
            if record.status != 'recorded':
                raise ValidationError(
                    f"Hanya status 'Recorded' yang bisa divalidasi. "
                    f"Status current: {record.status}"
                )
            record.status = 'validated'

    def update_consumed(self, new_quantity):
        """
        Update nilai consumed untuk record yang masih dalam status draft/recorded.
        Method ini memungkinkan update quantity tanpa akumulasi sebelum di-mark done.
        
        Args:
            new_quantity: Nilai kuantitas baru yang ingin di-set
            
        Returns:
            Bool - True jika berhasil
        """
        for record in self:
            # Hanya boleh update jika belum di-post ke stock atau di-cancel
            if record.status not in ['draft', 'recorded', 'validated']:
                raise ValidationError(
                    f"Tidak bisa update consumed pada status '{record.status}'. "
                    f"Hanya bisa di-update pada status draft/recorded/validated."
                )
            
            if new_quantity <= 0:
                raise ValidationError("Quantity harus lebih dari 0")
            
            # Update quantity value (not accumulate)
            record.quantity = new_quantity
            
            # Re-apply consumption to moves dengan nilai baru
            if record.move_id:
                moves = self._find_raw_moves_for_material(
                    record.manufacturing_order_id,
                    record.material_id
                )
                if moves:
                    self._apply_consumption_to_moves(record, moves)
        
        return True

    def action_post_to_stock(self):
        """Post consumption ke stock module"""
        # TODO: Create stock move untuk recording di inventory
        self.write({
            'status': 'posted',
            'is_stock_moved': True,
        })

    def action_cancel(self):
        """Cancel record"""
        self.write({
            'status': 'cancelled',
        })

    def retry_sync(self):
        """Retry sinkronisasi jika ada error"""
        self.write({
            'sync_status': 'pending',
            'error_message': False,
        })

    # ===== XML-RPC Compatible Methods =====

    @api.model
    def create_from_api(self, consumption_data):
        """
        Create material consumption dari API payload
        
        Args:
            consumption_data: Dict dengan material consumption info
            
        Returns:
            Dict dengan result status dan record_id
        """
        try:
            # Validate data
            from ..services.validation_service import ValidationService
            is_valid, error_msg = ValidationService.validate_material_consumption_data(
                self.env, consumption_data
            )
            if not is_valid:
                return {
                    'status': 'error',
                    'message': f'Validation failed: {error_msg}',
                    'record_id': None,
                }

            # Find equipment
            equipment = self.env['scada.equipment'].search([
                ('equipment_code', '=', consumption_data.get('equipment_id'))
            ], limit=1)
            if not equipment:
                return {
                    'status': 'error',
                    'message': f'Equipment not found: {consumption_data.get("equipment_id")}',
                    'record_id': None,
                }

            # Find material
            material_id = consumption_data.get('material_id') or consumption_data.get('product_id')
            product_tmpl_id = consumption_data.get('product_tmpl_id')
            material = None

            if material_id:
                try:
                    material_id = int(material_id)
                except (TypeError, ValueError):
                    return {
                        'status': 'error',
                        'message': 'Product ID must be a number',
                        'record_id': None,
                    }
                material = self.env['product.product'].browse(material_id)
                if not material.exists():
                    return {
                        'status': 'error',
                        'message': f'Product not found: {material_id}',
                        'record_id': None,
                    }
            elif product_tmpl_id:
                try:
                    product_tmpl_id = int(product_tmpl_id)
                except (TypeError, ValueError):
                    return {
                        'status': 'error',
                        'message': 'Product Template ID must be a number',
                        'record_id': None,
                    }
                template = self.env['product.template'].browse(product_tmpl_id)
                if not template.exists():
                    return {
                        'status': 'error',
                        'message': f'Product Template not found: {product_tmpl_id}',
                        'record_id': None,
                    }
                if not template.product_variant_id:
                    return {
                        'status': 'error',
                        'message': f'Product Template has no variant: {product_tmpl_id}',
                        'record_id': None,
                    }
                material = template.product_variant_id
            else:
                return {
                    'status': 'error',
                    'message': 'Product ID or Product Template ID is required',
                    'record_id': None,
                }

            # Find manufacturing order (required)
            mo_record = self._get_mo_from_payload(consumption_data)
            if not mo_record:
                return {
                    'status': 'error',
                    'message': 'MO ID is required',
                    'record_id': None,
                }

            moves = self._find_raw_moves_for_material(mo_record, material)
            if not moves:
                return {
                    'status': 'error',
                    'message': 'No raw material move found for this product in MO',
                    'record_id': None,
                }

            # Create record
            record = self.create({
                'equipment_id': equipment.id,
                'material_id': material.id,
                'quantity': float(consumption_data.get('quantity', 0)),
                'timestamp': consumption_data.get('timestamp', datetime.now()),
                'manufacturing_order_id': mo_record.id if mo_record else False,
                'batch_number': consumption_data.get('batch_number'),
                'api_request_id': consumption_data.get('api_request_id'),
                'status': 'recorded',
                'source': 'api',  # Mark as from API
            })

            self._apply_consumption_to_moves(record, moves)

            # Store equipment-material consumption for OEE/analytics
            self._log_equipment_material_consumption(
                equipment=equipment,
                material=material,
                mo_record=mo_record,
                quantity=record.quantity,
                timestamp=record.timestamp
            )

            # Auto-validate if configured
            if hasattr(equipment, 'production_line_id') and equipment.production_line_id:
                if getattr(equipment.production_line_id, 'auto_validate_consumption', False):
                    record.action_validate()

            return {
                'status': 'success',
                'message': 'Material consumption recorded successfully',
                'record_id': record.id,
                'external_id': str(record.id),
            }

        except Exception as e:
            import logging
            _logger = logging.getLogger(__name__)
            _logger.error(f'Error creating material consumption: {str(e)}')
            return {
                'status': 'error',
                'message': f'Error: {str(e)}',
                'record_id': None,
            }

    def _get_mo_from_payload(self, consumption_data):
        """Get manufacturing order from payload if provided."""
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

    def _log_equipment_material_consumption(self, equipment, material, mo_record, quantity, timestamp):
        """Create equipment-material consumption record for analytics."""
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

    def _find_raw_moves_for_material(self, mo_record, material):
        return mo_record.move_raw_ids.filtered(
            lambda move: move.product_id.id == material.id and move.state not in ['done', 'cancel']
        )

    def _apply_consumption_to_moves(self, record, moves):
        """
        Apply consumption quantity to stock moves.
        REPLACE the quantity_done value, tidak accumulate/tambah.
        """
        qty_to_consume = record.quantity
        planned_total = 0.0
        used_qty = 0.0
        move_id = False

        for move in moves:
            if used_qty >= qty_to_consume:
                break
            
            planned = move.product_uom_qty or 0.0
            planned_total += planned
        
        # Distribute consumption across moves proportionally
        qty_remaining = qty_to_consume
        
        for move in moves:
            if qty_remaining <= 0:
                break
            
            planned = move.product_uom_qty or 0.0
            
            # Calculate how much to allocate to this move
            if planned_total > 0:
                allocation = (planned / planned_total) * qty_to_consume
            else:
                allocation = qty_to_consume
            
            # SET quantity_done to the allocated amount (replace, not add)
            move.quantity_done = allocation
            qty_remaining -= allocation
            
            if not move_id:
                move_id = move.id

        record.write({
            'move_id': move_id,
            'is_stock_moved': True,
            'status': 'posted',
        })

    @api.model
    def validate_payload(self, payload_data):
        """
        Validate material consumption payload sebelum create
        
        Args:
            payload_data: Dict payload untuk divalidasi
            
        Returns:
            Dict dengan validation result
            
        XML-RPC Usage:
            payload = {
                'equipment_id': 'PLC01',
                'product_id': 123,
                'quantity': 10.5,
                'timestamp': '2025-02-06T10:30:00'
            }
            models.execute_kw(db, uid, pwd, 'scada.material.consumption',
                             'validate_payload', [payload])
        """
        # Import service
        from ..services.validation_service import ValidationService
        
        is_valid, error_msg = ValidationService.validate_material_consumption_data(
            self.env, payload_data
        )
        
        if is_valid:
            return {
                'status': 'success',
                'message': 'Validation passed',
                'data': payload_data,
            }
        else:
            return {
                'status': 'error',
                'message': f'Validation failed: {error_msg}',
                'data': payload_data,
            }

    @api.model
    def get_by_id(self, record_id, fields=None):
        """
        Get material consumption record by ID via XML-RPC
        
        Args:
            record_id: Record ID
            fields: List of fields to return (optional)
            
        Returns:
            Record data dict
            
        XML-RPC Usage:
            models.execute_kw(db, uid, pwd, 'scada.material.consumption',
                             'get_by_id', [123], {'fields': ['id', 'equipment_id', 'product_id']})
        """
        record = self.browse(record_id)
        if not record.exists():
            return {
                'status': 'error',
                'message': f'Record {record_id} not found',
                'data': None,
            }
        
        if fields is None:
            fields = ['id', 'equipment_id', 'product_id', 'quantity', 
                     'timestamp', 'status', 'sync_status']
        
        result_data = {}
        for field_name in fields:
            if field_name == 'product_id':
                result_data[field_name] = record.material_id.id
                continue

            if hasattr(record, field_name):
                field_value = getattr(record, field_name)
                # Handle relational fields
                if hasattr(field_value, 'id'):
                    result_data[field_name] = field_value.id
                elif hasattr(field_value, 'isoformat'):  # Datetime
                    result_data[field_name] = field_value.isoformat()
                else:
                    result_data[field_name] = field_value
        
        return {
            'status': 'success',
            'data': result_data,
        }
