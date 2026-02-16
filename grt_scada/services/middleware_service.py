"""
Middleware Service
Business logic untuk komunikasi dengan middleware dan JSON-RPC endpoints

Simplified untuk JSON-RPC - semua static methods dihapus
Fokus pada instance methods untuk business logic
"""

import logging
import json
from datetime import datetime

from odoo import fields

_logger = logging.getLogger(__name__)


class MiddlewareService:
    """Service untuk manage komunikasi dengan middleware"""

    def __init__(self, env):
        self.env = env

    # ===== Instance Methods (Business Logic) =====

    def send_mo_list_to_middleware(self, equipment_code, data_format='json'):
        """
        Get MO list dan send ke middleware via API call

        Args:
            equipment_code: Equipment code
            data_format: Format data (json, xml, csv)
        """
        try:
            # Get equipment
            equipment = self.env['scada.equipment'].search([
                ('equipment_code', '=', equipment_code)
            ], limit=1)

            if not equipment:
                _logger.error(f'Equipment {equipment_code} not found')
                return False

            mo_list = self._get_mo_list_for_equipment(equipment, status=None)
            if not mo_list:
                _logger.info(f'No MO data for {equipment_code}')
                return True

            # Send to middleware (stub implementation)
            result = self._send_to_middleware(
                equipment=equipment,
                endpoint='mo-list',
                data=mo_list,
                format=data_format
            )

            if result:
                _logger.info(f'Sent {len(mo_list)} MO records to {equipment_code}')

            return result

        except Exception as e:
            _logger.error(f'Error sending MO list: {str(e)}')
            return False

    def process_material_consumption(self, consumption_data):
        """
        Process material consumption data dari middleware

        Args:
            consumption_data: Dict dengan material consumption info
        """
        try:
            result = self.apply_material_consumption(consumption_data)
            if result.get('status') == 'success':
                return result
            raise ValueError(result.get('message') or 'Unknown error')
        except Exception as e:
            _logger.error(f'Error processing material consumption: {str(e)}')
            raise

    def get_mo_list_for_equipment(self, equipment_code, status=None, limit=50, offset=0):
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

        data = self._get_mo_list_for_equipment(
            equipment, status=status, limit=limit, offset=offset
        )

        return {
            'status': 'success',
            'count': len(data),
            'data': data,
        }

    def apply_material_consumption(self, consumption_data):
        """
        Apply material consumption to MO raw moves.
        
        Untuk MO yang belum di-mark done:
        - update_mode='add': Menambahkan ke existing consumption (default)
        - update_mode='replace': Mengganti existing consumption dengan nilai baru
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

            equipment = self._get_equipment(consumption_data.get('equipment_id'))
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

            mo_record = self._get_mo_from_payload(consumption_data)
            if not mo_record:
                return {
                    'status': 'error',
                    'message': 'MO ID is required',
                }
            
            # Check MO state: hanya bisa update jika MO belum di-mark done
            if mo_record.state in ['done', 'cancel']:
                return {
                    'status': 'error',
                    'message': f'Cannot update consumption for MO in {mo_record.state} state',
                }

            moves = self._find_raw_moves_for_material(mo_record, material)
            if not moves:
                return {
                    'status': 'error',
                    'message': 'No raw material move found for this product in MO',
                }

            quantity = float(consumption_data.get('quantity', 0))
            update_mode = consumption_data.get('update_mode', 'add').lower()
            
            # Apply consumption dengan mode yang dipilih
            if update_mode == 'replace':
                applied_qty, move_ids = self._apply_consumption_to_moves_replace(
                    moves, quantity, allow_overconsume=True
                )
                action_desc = 'replaced'
            else:
                applied_qty, move_ids = self._apply_consumption_to_moves(
                    moves, quantity, allow_overconsume=True
                )
                action_desc = 'added'

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
                'message': f'Material consumption {action_desc} to MO moves',
                'mo_id': mo_record.name,
                'mo_state': mo_record.state,
                'applied_qty': applied_qty,
                'move_ids': move_ids,
                'update_mode': update_mode,
                'can_update_again': mo_record.state not in ['done', 'cancel'],
            }

        except Exception as e:
            return {
                'status': 'error',
                'message': f'Error: {str(e)}',
            }

    def _send_to_middleware(self, equipment, endpoint, data, format='json'):
        """
        Send data ke middleware

        Stub implementation - integrate dengan actual middleware
        """
        try:
            if not equipment.ip_address or not equipment.port:
                _logger.warning(f'Equipment {equipment.name} tidak memiliki connection info')
                return False

            # TODO: Implement actual HTTP call ke middleware
            # url = f'http://{equipment.ip_address}:{equipment.port}/{endpoint}'
            # response = requests.post(url, json=data)

            _logger.info(
                f'[STUB] Would send to {equipment.ip_address}:{equipment.port}/{endpoint}'
            )
            return True

        except Exception as e:
            _logger.error(f'Error sending to middleware: {str(e)}')
            return False

    def retry_failed_syncs(self):
        """Retry semua failed syncs"""
        try:
            _logger.info('No sync retry needed for mrp.production based MO data')
            return 0

        except Exception as e:
            _logger.error(f'Error retrying failed syncs: {str(e)}')
            return 0

    def sync_equipment_status(self):
        """Sync status dari semua equipment"""
        try:
            equipment_list = self.env['scada.equipment'].search([
                ('is_active', '=', True)
            ])

            for equipment in equipment_list:
                # Test connection
                equipment.test_connection()

            return True

        except Exception as e:
            _logger.error(f'Error syncing equipment status: {str(e)}')
            return False

    def update_mo_status(self, mo_record, payload_data):
        update_data = {}
        if payload_data.get('date_start_actual'):
            update_data['date_start'] = payload_data['date_start_actual']
        if payload_data.get('date_end_actual'):
            update_data['date_finished'] = payload_data['date_end_actual']

        if update_data:
            mo_record.write(update_data)

        return {
            'status': 'success',
            'message': 'MO status updated successfully',
            'mo_id': mo_record.name,
        }

    def mark_mo_done(self, mo_record, payload_data):
        equipment = self._get_equipment(payload_data.get('equipment_id'))

        mo_name = payload_data.get('mo_id')
        if mo_name and str(mo_name) != str(mo_record.name):
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

        finished_moves = mo_record.move_finished_ids.filtered(
            lambda move: move.product_id.id == mo_record.product_id.id and move.state not in ['done', 'cancel']
        )
        if not finished_moves:
            return {
                'status': 'error',
                'message': 'No finished product move found for this MO',
            }

        if hasattr(mo_record, 'qty_producing'):
            mo_record.qty_producing = finished_qty

        finished_moves[0].quantity_done = finished_qty

        if payload_data.get('date_end_actual'):
            mo_record.write({'date_finished': payload_data['date_end_actual']})

        auto_consume = payload_data.get('auto_consume', False)
        consumed_materials = []
        if auto_consume and mo_record.bom_id and equipment:
            # Smart auto-consume: hanya jika consumption belum ada dari middleware atau manual input
            consumed_materials = self._auto_consume_from_bom_smart(mo_record, equipment)

        if mo_record.state not in ['done', 'cancel']:
            mo_record.sudo().button_mark_done()

        return {
            'status': 'success',
            'message': 'Manufacturing order marked as done',
            'mo_id': mo_record.name,
            'auto_consumed': len(consumed_materials),
            'materials': consumed_materials,
        }

    def _extract_equipment_details(self, equipment):
        """Helper: Extract full equipment details object"""
        if not equipment:
            return None
        return {
            'id': equipment.id,
            'code': equipment.equipment_code,
            'name': equipment.name,
            'equipment_type': equipment.equipment_type,
            'manufacturer': equipment.manufacturer,
            'model_number': equipment.model_number,
            'serial_number': equipment.serial_number,
            'ip_address': equipment.ip_address,
            'port': equipment.port,
            'protocol': equipment.protocol,
            'is_active': equipment.is_active,
            'connection_status': equipment.connection_status,
            'sync_status': equipment.sync_status,
            'last_connected': equipment.last_connected.isoformat() if equipment.last_connected else None,
        }

    def _get_equipment(self, equipment_code):
        if not equipment_code:
            return False
        return self.env['scada.equipment'].search([
            ('equipment_code', '=', equipment_code)
        ], limit=1)

    def _get_mo_list_for_equipment(self, equipment, status=None, limit=50, offset=0):
        domain = []
        if equipment:
            domain.append(('scada_equipment_id', '=', equipment.id))
        if status:
            domain.append(('state', '=', status))

        mos = self.env['mrp.production'].search(
            domain,
            limit=limit,
            offset=offset,
            order='date_planned_start asc, id asc'
        )

        data = []
        for mo in mos:
            produced_qty = sum(
                move.quantity_done for move in mo.move_finished_ids
                if move.state != 'cancel'
            )
            consumed_qty = sum(
                move.quantity_done for move in mo.move_raw_ids
                if move.state != 'cancel'
            )
            mo_equipment = getattr(mo, 'scada_equipment_id', False)
            equipment_data = self._extract_equipment_details(mo_equipment)
            data.append({
                'mo_id': mo.name,
                'product': mo.product_id.display_name if mo.product_id else None,
                'quantity': mo.product_qty,
                'produced_qty': produced_qty,
                'consumed_qty': consumed_qty,
                'status': mo.state,
                'schedule_start': mo.date_planned_start.isoformat() if mo.date_planned_start else None,
                'schedule_end': mo.date_planned_finished.isoformat() if mo.date_planned_finished else None,
                'equipment': equipment_data,
            })

        return data

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

    def _get_mo_from_payload(self, consumption_data):
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

    def _apply_consumption_to_moves_replace(self, moves, quantity, allow_overconsume=True):
        """
        Apply consumption dengan REPLACE mode: set quantity_done ke value baru, bukan ADD
        
        Berguna untuk update multiple times dari middleware tanpa accumulating.
        Contoh:
        - First update: silo101 = 100 kg → quantity_done = 100
        - Second update: silo101 = 120 kg → quantity_done = 120 (replace, bukan 100+120)
        """
        qty_remaining = quantity
        move_ids = []

        # Clear existing done qty so replace mode does not accumulate
        for move in moves:
            move.quantity_done = 0.0

        move_count = len(moves)
        for idx, move in enumerate(moves):
            if qty_remaining <= 0:
                break
            
            planned = move.product_uom_qty or 0.0
            
            # REPLACE mode: jangan gunakan existing done, langsung set ke value baru.
            # Jika overconsume diizinkan, move terakhir bisa menampung sisa qty
            # agar input middleware tidak terpotong ke planned qty.
            if planned == 0.0 and not allow_overconsume:
                add_qty = 0.0
            else:
                if allow_overconsume and idx == (move_count - 1):
                    add_qty = qty_remaining
                else:
                    add_qty = qty_remaining if planned == 0.0 else min(qty_remaining, planned)
            
            if add_qty <= 0.0:
                continue
            
            # Set (replace) bukan add
            move.quantity_done = add_qty
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

    def _auto_consume_from_bom(self, mo_record, equipment):
        consumed_materials = []
        if not equipment or not mo_record.bom_id:
            return consumed_materials

        for line in mo_record.bom_id.bom_line_ids:
            quantity = (line.product_qty / mo_record.bom_id.product_qty) * mo_record.product_qty
            try:
                moves = self._find_raw_moves_for_material(mo_record, line.product_id)
                applied_qty, move_ids = self._apply_consumption_to_moves(
                    moves, quantity, allow_overconsume=False
                )
                self._log_equipment_material_consumption(
                    equipment=equipment,
                    material=line.product_id,
                    mo_record=mo_record,
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
                _logger.error(f'Error auto-consuming {line.product_id.name}: {str(e)}')
                continue

        return consumed_materials

    def _auto_consume_from_bom_smart(self, mo_record, equipment):
        """
        Smart auto-consume yang hanya consume jika consumption belum ada dari middleware/manual.
        
        Logic:
        - Untuk setiap material di BoM:
          - Check apakah move.quantity_done sudah > 0 (ada update dari middleware atau manual)
          - Jika sudah > 0, skip (jangan override)
          - Jika 0, auto-calculate dan apply
        """
        consumed_materials = []
        if not equipment or not mo_record.bom_id:
            return consumed_materials

        for line in mo_record.bom_id.bom_line_ids:
            quantity = (line.product_qty / mo_record.bom_id.product_qty) * mo_record.product_qty
            try:
                moves = self._find_raw_moves_for_material(mo_record, line.product_id)
                
                # Smart check: apakah consumption sudah ada?
                existing_consumption = sum(move.quantity_done for move in moves if move.state not in ['done', 'cancel'])
                
                if existing_consumption > 0:
                    # Consumption sudah ada dari middleware/manual, skip
                    _logger.info(
                        f'Skipping auto-consume for {line.product_id.name}: '
                        f'Already has consumption {existing_consumption}'
                    )
                    consumed_materials.append({
                        'material_code': line.product_id.default_code or line.product_id.name,
                        'material_name': line.product_id.name,
                        'quantity': existing_consumption,
                        'uom': line.product_uom_id.name,
                        'move_ids': [m.id for m in moves if m.quantity_done > 0],
                        'source': 'skipped_existing',
                    })
                    continue
                
                # Consumption belum ada, auto-calculate dari BoM
                applied_qty, move_ids = self._apply_consumption_to_moves(
                    moves, quantity, allow_overconsume=False
                )
                
                if applied_qty > 0:
                    self._log_equipment_material_consumption(
                        equipment=equipment,
                        material=line.product_id,
                        mo_record=mo_record,
                        quantity=applied_qty,
                        timestamp=datetime.now(),
                    )
                    consumed_materials.append({
                        'material_code': line.product_id.default_code or line.product_id.name,
                        'material_name': line.product_id.name,
                        'quantity': applied_qty,
                        'uom': line.product_uom_id.name,
                        'move_ids': move_ids,
                        'source': 'auto_calculated',
                    })
            except Exception as e:
                _logger.error(f'Error smart auto-consuming {line.product_id.name}: {str(e)}')
                continue

        return consumed_materials

    def update_mo_with_consumptions(self, update_data):
        """
        Update MO dengan quantity dan consumption berdasarkan equipment code SCADA
        
        Args:
            update_data: Dict dengan format:
            {
                'mo_id': 'WH/MO/00001',
                'quantity': 2000,
                'silo101': 825,
                'silo102': 600,
                ...
            }
        
        Returns:
            Dict dengan status dan detail hasil update
        """
        try:
            # Validasi mo_id
            mo_name = update_data.get('mo_id')
            if not mo_name:
                return {
                    'status': 'error',
                    'message': 'mo_id is required',
                }
            
            # Cari MO
            mo_record = self.env['mrp.production'].search([
                ('name', '=', str(mo_name))
            ], limit=1)
            
            if not mo_record:
                return {
                    'status': 'error',
                    'message': f'Manufacturing Order "{mo_name}" not found',
                }
            
            # Update quantity jika ada
            quantity = update_data.get('quantity')
            if quantity is not None:
                try:
                    quantity = float(quantity)
                    if quantity > 0:
                        mo_record.write({'product_qty': quantity})
                        _logger.info(f'Updated MO {mo_name} quantity to {quantity}')
                except (TypeError, ValueError) as e:
                    return {
                        'status': 'error',
                        'message': f'Invalid quantity value: {quantity}',
                    }
            
            # Process consumption per equipment code
            consumed_items = []
            errors = []
            
            _logger.info(f'Processing consumption for MO {mo_name}: {list(update_data.items())}')
            
            for key, value in update_data.items():
                # Skip non-equipment keys
                if key in ['mo_id', 'quantity']:
                    continue
                
                # Asumsikan key adalah equipment_code (misal: silo101, silo102)
                equipment_code = key
                
                try:
                    consumption_qty = float(value)
                except (TypeError, ValueError):
                    errors.append(f'{equipment_code}: Invalid quantity value "{value}"')
                    continue
                
                if consumption_qty <= 0:
                    _logger.debug(f'Skipping {equipment_code}: qty <= 0')
                    continue
                
                _logger.info(f'Processing {equipment_code}: {consumption_qty} kg')
                
                # Cari equipment berdasarkan code
                equipment = self.env['scada.equipment'].search([
                    ('equipment_code', '=', equipment_code)
                ], limit=1)
                
                if not equipment:
                    msg = f'{equipment_code}: Equipment not found'
                    _logger.warning(msg)
                    errors.append(msg)
                    continue
                
                _logger.info(f'Found equipment: {equipment.name} (ID: {equipment.id})')
                
                # Cari raw material move yang berelasi dengan equipment ini
                all_moves = mo_record.move_raw_ids
                _logger.info(f'Total raw moves in MO: {len(all_moves)}')
                
                matching_moves = all_moves.filtered(
                    lambda m: m.scada_equipment_id.id == equipment.id
                    and m.state != 'cancel'
                )
                
                _logger.info(f'Matching moves for {equipment_code}: {len(matching_moves)} (equipment_id={equipment.id})')
                for m in matching_moves:
                    _logger.info(f'  - Move {m.id}: {m.product_id.name} (qty_done={m.quantity_done}, state={m.state})')
                
                if not matching_moves:
                    msg = f'{equipment_code}: No raw material move found for this equipment'
                    _logger.warning(msg)
                    errors.append(msg)
                    continue
                
                # Apply consumption (REPLACE mode: setiap update mengganti nilai lama)
                _logger.info(f'Applying consumption {consumption_qty} to {len(matching_moves)} moves')
                applied_qty, move_ids = self._apply_consumption_to_moves_replace(
                    matching_moves, consumption_qty, allow_overconsume=True
                )
                _logger.info(f'Applied {applied_qty} to moves {move_ids}')
                
                # Log consumption untuk setiap material yang di-consume
                for move in matching_moves:
                    if move.id in move_ids:
                        _logger.info(f'Logging consumption for move {move.id}: {move.quantity_done}')
                        self._log_equipment_material_consumption(
                            equipment=equipment,
                            material=move.product_id,
                            mo_record=mo_record,
                            quantity=move.quantity_done,
                            timestamp=datetime.now(),
                        )
                
                consumed_items.append({
                    'equipment_code': equipment_code,
                    'equipment_name': equipment.name,
                    'applied_qty': applied_qty,
                    'move_ids': move_ids,
                    'products': [move.product_id.display_name for move in matching_moves if move.id in move_ids],
                })
            
            result = {
                'status': 'success',
                'message': 'MO updated successfully',
                'mo_id': mo_record.name,
                'mo_state': mo_record.state,
                'consumed_items': consumed_items,
            }
            
            if quantity is not None:
                result['updated_quantity'] = quantity
            
            if errors:
                result['errors'] = errors
                result['message'] = 'MO updated with some errors'
            
            return result
            
        except Exception as e:
            _logger.error(f'Error updating MO with consumptions: {str(e)}')
            return {
                'status': 'error',
                'message': f'Error: {str(e)}',
            }

