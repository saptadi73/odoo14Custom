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

        auto_consume = payload_data.get('auto_consume', True)
        consumed_materials = []
        if auto_consume and mo_record.bom_id and equipment:
            consumed_materials = self._auto_consume_from_bom(mo_record, equipment)

        if mo_record.state not in ['done', 'cancel']:
            mo_record.sudo().button_mark_done()

        return {
            'status': 'success',
            'message': 'Manufacturing order marked as done',
            'mo_id': mo_record.name,
            'auto_consumed': len(consumed_materials),
            'materials': consumed_materials,
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
            data.append({
                'mo_id': mo.name,
                'product': mo.product_id.display_name if mo.product_id else None,
                'quantity': mo.product_qty,
                'produced_qty': produced_qty,
                'consumed_qty': consumed_qty,
                'status': mo.state,
                'schedule_start': mo.date_planned_start.isoformat() if mo.date_planned_start else None,
                'schedule_end': mo.date_planned_finished.isoformat() if mo.date_planned_finished else None,
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

