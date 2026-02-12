# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)

class ScadaMODetailedController(http.Controller):

    def _get_equipment_details(self, equipment):
        """Helper: Extract full equipment details"""
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

    @http.route('/api/scada/mo-list-detailed', type='json', auth='user', methods=['POST'])
    def get_mo_list_detailed(self, **kwargs):
        """Get detailed list of MOs with components, consumption, and equipment info (JSON-RPC)."""
        try:
            payload = request.jsonrequest or {}
            params = payload.get('params') if isinstance(payload, dict) else {}
            if not isinstance(params, dict):
                params = {}

            limit = params.get('limit', 10)
            offset = params.get('offset', 0)
            try:
                limit = int(limit)
            except (ValueError, TypeError):
                limit = 10
            try:
                offset = int(offset)
            except (ValueError, TypeError):
                offset = 0

            domain = [('state', 'in', ['confirmed', 'progress', 'to_close'])]
            mos = request.env['mrp.production'].search(
                domain,
                limit=limit,
                offset=offset,
                order='date_planned_start asc, id desc'
            )

            data = []
            for mo in mos:
                bom_components = []
                if mo.bom_id:
                    for line in mo.bom_id.bom_line_ids:
                        bom_components.append({
                            'product_tmpl_id': line.product_id.product_tmpl_id.id if line.product_id else None,
                            'product_id': line.product_id.id if line.product_id else None,
                            'product_name': line.product_id.display_name if line.product_id else None,
                            'quantity': line.product_qty,
                            'uom': line.product_uom_id.name if line.product_uom_id else None,
                        })

                consumption_map = {}
                mo_equipment = getattr(mo, 'scada_equipment_id', False)
                for move in mo.move_raw_ids:
                    product = move.product_id
                    tmpl_id = product.product_tmpl_id.id if product else None
                    component_equipment = move.scada_equipment_id or mo_equipment
                    key = (tmpl_id, product.id if product else None)
                    if key not in consumption_map:
                        consumption_map[key] = {
                            'product_tmpl_id': tmpl_id,
                            'product_id': product.id if product else None,
                            'product_name': product.display_name if product else None,
                            'to_consume': 0.0,
                            'reserved': 0.0,
                            'consumed': 0.0,
                            'uom': move.product_uom.name if move.product_uom else None,
                            'equipment': self._get_equipment_details(component_equipment),
                        }
                    consumption_map[key]['to_consume'] += move.product_uom_qty
                    consumption_map[key]['reserved'] += move.reserved_availability
                    consumption_map[key]['consumed'] += move.quantity_done

                components_consumption = list(consumption_map.values())
                produced_qty = sum(
                    move.quantity_done for move in mo.move_finished_ids
                    if move.state != 'cancel'
                )

                data.append({
                    'mo_id': mo.name,
                    'reference': mo.origin or None,
                    'state': mo.state,
                    'schedule_start': mo.date_planned_start.isoformat() if mo.date_planned_start else None,
                    'schedule_end': mo.date_planned_finished.isoformat() if mo.date_planned_finished else None,
                    'equipment': self._get_equipment_details(mo_equipment),
                    'product_tmpl_id': mo.product_id.product_tmpl_id.id if mo.product_id else None,
                    'product_id': mo.product_id.id if mo.product_id else None,
                    'product_name': mo.product_id.display_name if mo.product_id else None,
                    'quantity': mo.product_qty,
                    'produced_qty': produced_qty,
                    'uom': mo.product_uom_id.name if mo.product_uom_id else None,
                    'bom_id': mo.bom_id.id if mo.bom_id else None,
                    'bom_code': mo.bom_id.code if mo.bom_id else None,
                    'bom_components': bom_components,
                    'components_consumption': components_consumption,
                })

            return {
                'status': 'success',
                'count': len(data),
                'data': data,
            }
        except Exception as e:
            _logger.error(f'Error getting detailed MO list: {str(e)}')
            return {'status': 'error', 'message': str(e)}