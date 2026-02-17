"""
SCADA Main Controller - JSON-RPC API
Simple JSON-RPC endpoints optimized for Vue.js frontend

Authentication: Odoo Session (JSON-RPC)
"""

from odoo import http
from odoo.http import request
import logging
import json
from datetime import datetime, timedelta
from ..services.product_service import ProductService
from ..services.mo_weight_service import MoWeightService
from ..services.bom_service import BomService

_logger = logging.getLogger(__name__)


class ScadaJsonRpcController(http.Controller):
    """SCADA JSON-RPC Controller untuk Vue.js Frontend"""

    def _get_json_payload(self):
        payload = request.jsonrequest or {}
        if isinstance(payload, dict):
            params = payload.get('params')
            if isinstance(params, dict):
                return params
        return payload

    def _parse_bool_param(self, value, default=None):
        if value is None:
            return default
        value_lower = value.strip().lower()
        if value_lower in ['true', '1', 'yes']:
            return True
        if value_lower in ['false', '0', 'no']:
            return False
        if value_lower == 'all':
            return None
        return default

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

    def _authenticate_session(self, login, password, dbname=None):
        db = dbname or request.session.db or request.env.cr.dbname
        uid = request.session.authenticate(db, login, password)
        if not uid:
            return {
                'status': 'error',
                'message': 'Invalid credentials',
            }
        return {
            'status': 'success',
            'uid': uid,
            'session_id': request.session.sid,
            'db': db,
            'login': login,
        }

    # ===== HEALTH & SYSTEM =====

    @http.route('/api/scada/health', type='json', auth='public', methods=['GET'])
    def health_check(self, **kwargs):
        """Health check endpoint"""
        try:
            return {
                'status': 'ok',
                'message': 'SCADA Module is running',
                'timestamp': datetime.now().isoformat(),
            }
        except Exception as e:
            _logger.error(f'Health check error: {str(e)}')
            return {
                'status': 'error',
                'message': str(e),
            }

    @http.route('/api/scada/authenticate', type='json', auth='public', methods=['POST'])
    def authenticate(self, **kwargs):
        """
        Authenticate session untuk middleware.
        """
        try:
            data = self._get_json_payload()
            login = data.get('login')
            password = data.get('password')
            dbname = data.get('db')
            if not login or not password:
                return {
                    'status': 'error',
                    'message': 'login and password are required',
                }
            return self._authenticate_session(login, password, dbname)
        except Exception as e:
            _logger.error(f'Auth error: {str(e)}')
            return {'status': 'error', 'message': str(e)}

    @http.route('/api/scada/version', type='json', auth='public', methods=['GET'])
    def get_version(self, **kwargs):
        """Get SCADA module version"""
        try:
            module = request.env['ir.module.module'].search([
                ('name', '=', 'grt_scada')
            ], limit=1)

            if module:
                return {
                    'status': 'success',
                    'version': module.latest_version or '1.0.0',
                    'name': 'SCADA for Odoo',
                }
            return {'status': 'error', 'message': 'Module not found'}
        except Exception as e:
            _logger.error(f'Version check error: {str(e)}')
            return {'status': 'error', 'message': str(e)}

    # ===== MATERIAL CONSUMPTION =====

    @http.route('/api/scada/material-consumption', type='json', auth='user', methods=['POST'])
    def create_material_consumption(self, **kwargs):
        """
        Apply material consumption directly to MO
        
        Untuk MO yang belum di-mark done, consumption bisa di-update multiple times.
        
        POST /api/scada/material-consumption
        Auth: Session cookie
        
        Body:
        {
            "equipment_id": "PLC01",
            "product_id": 123,
            "quantity": 10.5,
            "mo_id": "MO/2025/001",
            "update_mode": "add",  // atau "replace" (optional, default: "add")
            "timestamp": "2025-02-06T10:30:00"
        }
        
        update_mode:
        - "add" (default): Menambahkan ke existing consumption (accumulating)
          First update: 100 kg → quantity_done = 100
          Second update: 50 kg → quantity_done = 150
        
        - "replace": Mengganti existing consumption dengan value baru
          First update: 100 kg → quantity_done = 100
          Second update: 120 kg → quantity_done = 120 (replace, bukan 220)
        """
        try:
            data = self._get_json_payload()
            from ..services.middleware_service import MiddlewareService
            service = MiddlewareService(request.env)
            result = service.apply_material_consumption(data)
            return result
        except Exception as e:
            _logger.error(f'Error creating material consumption: {str(e)}')
            return {'status': 'error', 'message': str(e)}

    @http.route('/api/scada/material-consumption/<int:record_id>', type='json', auth='user', methods=['GET'])
    def get_material_consumption(self, record_id, **kwargs):
        """Deprecated: material consumption records are not stored."""
        try:
            return {
                'status': 'error',
                'message': 'Material consumption records are not stored; use MO components consumption report instead.',
            }
        except Exception as e:
            _logger.error(f'Error getting material consumption: {str(e)}')
            return {'status': 'error', 'message': str(e)}

    @http.route('/api/scada/material-consumption/validate', type='json', auth='user', methods=['POST'])
    def validate_material_consumption(self, **kwargs):
        """Validate material consumption payload"""
        try:
            data = self._get_json_payload()
            from ..services.validation_service import ValidationService
            is_valid, error_msg = ValidationService.validate_material_consumption_data(
                request.env, data
            )
            if is_valid:
                return {'status': 'success', 'message': 'Validation passed', 'data': data}
            return {'status': 'error', 'message': f'Validation failed: {error_msg}', 'data': data}
        except Exception as e:
            _logger.error(f'Error validating material consumption: {str(e)}')
            return {'status': 'error', 'message': str(e)}

    # ===== MANUFACTURING ORDERS =====

    @http.route('/api/scada/mo-list', type='json', auth='user', methods=['GET'])
    def get_mo_list(self, **kwargs):
        """Get MO list for equipment"""
        try:
            equipment_code = request.httprequest.args.get('equipment_id')
            mo_status = request.httprequest.args.get('status')
            limit = int(request.httprequest.args.get('limit', 50))
            offset = int(request.httprequest.args.get('offset', 0))

            from ..services.middleware_service import MiddlewareService
            service = MiddlewareService(request.env)
            result = service.get_mo_list_for_equipment(
                equipment_code, status=mo_status, limit=limit, offset=offset
            )
            return result
        except Exception as e:
            _logger.error(f'Error getting MO list: {str(e)}')
            return {'status': 'error', 'message': str(e)}

    @http.route('/api/scada/mo-list-confirmed', type='json', auth='user', methods=['POST'])
    def get_mo_list_confirmed(self, **kwargs):
        """Get confirmed MO list with equipment info (JSON-RPC)."""
        try:
            payload = request.jsonrequest or {}
            params = payload.get('params') if isinstance(payload, dict) else {}
            if not isinstance(params, dict):
                params = {}

            limit = int(params.get('limit', 50))
            offset = int(params.get('offset', 0))

            mos = request.env['mrp.production'].search(
                [('state', '=', 'confirmed')],
                limit=limit,
                offset=offset,
                order='date_planned_start asc, id asc'
            )

            data = []
            for mo in mos:
                mo_equipment = getattr(mo, 'scada_equipment_id', False)
                data.append({
                    'mo_id': mo.name,
                    'reference': mo.origin or None,
                    'schedule': mo.date_planned_start.isoformat() if mo.date_planned_start else None,
                    'schedule_end': mo.date_planned_finished.isoformat() if mo.date_planned_finished else None,
                    'product': mo.product_id.display_name if mo.product_id else None,
                    'quantity': mo.product_qty,
                    'state': mo.state,
                    'equipment': self._get_equipment_details(mo_equipment),
                })

            return {
                'status': 'success',
                'count': len(data),
                'data': data,
            }
        except Exception as e:
            _logger.error(f'Error getting confirmed MO list: {str(e)}')
            return {'status': 'error', 'message': str(e)}

    @http.route('/api/scada/mo-detail', type='json', auth='user', methods=['POST'])
    def get_mo_detail(self, **kwargs):
        """Get MO detail with BoM and component consumption (JSON-RPC)."""
        try:
            payload = request.jsonrequest or {}
            params = payload.get('params') if isinstance(payload, dict) else {}
            if not isinstance(params, dict):
                params = {}

            mo_value = params.get('mo_id') or params.get('manufacturing_order_id')
            if not mo_value:
                return {'status': 'error', 'message': 'mo_id is required'}

            if isinstance(mo_value, int) or str(mo_value).isdigit():
                mo = request.env['mrp.production'].browse(int(mo_value))
            else:
                mo = request.env['mrp.production'].search([
                    ('name', '=', str(mo_value))
                ], limit=1)

            if not mo or not mo.exists():
                return {'status': 'error', 'message': f'MO not found: {mo_value}'}

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

            return {
                'status': 'success',
                'data': {
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
                }
            }
        except Exception as e:
            _logger.error(f'Error getting MO detail: {str(e)}')
            return {'status': 'error', 'message': str(e)}

    @http.route('/api/scada/mo/<int:mo_id>/acknowledge', type='json', auth='user', methods=['POST'])
    def acknowledge_mo(self, mo_id, **kwargs):
        """Acknowledge MO"""
        try:
            data = self._get_json_payload()
            mo = request.env['mrp.production'].browse(mo_id)
            if not mo or not mo.exists():
                return {'status': 'error', 'message': f'MO not found: {mo_id}'}
            return {
                'status': 'success',
                'message': 'MO acknowledged successfully',
                'mo_id': mo.name,
            }
        except Exception as e:
            _logger.error(f'Error acknowledging MO: {str(e)}')
            return {'status': 'error', 'message': str(e)}

    @http.route('/api/scada/mo/<int:mo_id>/update-status', type='json', auth='user', methods=['POST'])
    def update_mo_status(self, mo_id, **kwargs):
        """Update MO status"""
        try:
            data = self._get_json_payload()
            mo = request.env['mrp.production'].browse(mo_id)
            if not mo or not mo.exists():
                return {'status': 'error', 'message': f'MO not found: {mo_id}'}

            from ..services.middleware_service import MiddlewareService
            service = MiddlewareService(request.env)
            return service.update_mo_status(mo, data)
        except Exception as e:
            _logger.error(f'Error updating MO status: {str(e)}')
            return {'status': 'error', 'message': str(e)}

    @http.route('/api/scada/mo/<int:mo_id>/mark-done', type='json', auth='user', methods=['POST'])
    def mark_mo_done(self, mo_id, **kwargs):
        """Mark MO as done"""
        try:
            data = self._get_json_payload()
            mo = request.env['mrp.production'].browse(mo_id)
            if not mo or not mo.exists():
                return {'status': 'error', 'message': f'MO not found: {mo_id}'}

            from ..services.middleware_service import MiddlewareService
            service = MiddlewareService(request.env)
            return service.mark_mo_done(mo, data)
        except Exception as e:
            _logger.error(f'Error marking MO done: {str(e)}')
            return {'status': 'error', 'message': str(e)}

    @http.route('/api/scada/mo/mark-done', type='json', auth='user', methods=['POST'])
    def mark_mo_done_by_payload(self, **kwargs):
        """Mark MO as done using mo_id from payload."""
        try:
            data = self._get_json_payload()
            mo_name = data.get('mo_id')
            if not mo_name:
                return {'status': 'error', 'message': 'mo_id is required'}

            mo = request.env['mrp.production'].search([
                ('name', '=', str(mo_name))
            ], limit=1)
            if not mo:
                return {'status': 'error', 'message': f'MO not found: {mo_name}'}

            from ..services.middleware_service import MiddlewareService
            service = MiddlewareService(request.env)
            return service.mark_mo_done(mo, data)
        except Exception as e:
            _logger.error(f'Error marking MO done (payload): {str(e)}')
            return {'status': 'error', 'message': str(e)}

    @http.route('/api/scada/mo/cancel', type='json', auth='user', methods=['POST'])
    def cancel_mo_by_payload(self, **kwargs):
        """Cancel MO using mo_id from payload."""
        try:
            data = self._get_json_payload()
            mo_name = data.get('mo_id')
            if not mo_name:
                return {'status': 'error', 'message': 'mo_id is required'}

            mo = request.env['mrp.production'].search([
                ('name', '=', str(mo_name))
            ], limit=1)
            if not mo:
                return {'status': 'error', 'message': f'MO not found: {mo_name}'}

            from ..services.middleware_service import MiddlewareService
            service = MiddlewareService(request.env)
            return service.cancel_mo(mo, data)
        except Exception as e:
            _logger.error(f'Error cancelling MO (payload): {str(e)}')
            return {'status': 'error', 'message': str(e)}

    @http.route('/api/scada/mo/update-with-consumptions', type='json', auth='user', methods=['POST'])
    def update_mo_with_consumptions(self, **kwargs):
        """
        Update MO dengan quantity dan consumption berdasarkan equipment code SCADA
        
        POST /api/scada/mo/update-with-consumptions
        Auth: Session cookie
        
        Body:
        {
            "mo_id": "WH/MO/00001",
            "quantity": 2000,
            "silo101": 825,
            "silo102": 600,
            "silo103": 375,
            ...
        }
        
        Response:
        {
            "status": "success",
            "message": "MO updated successfully",
            "mo_id": "WH/MO/00001",
            "mo_state": "confirmed",
            "updated_quantity": 2000,
            "consumed_items": [
                {
                    "equipment_code": "silo101",
                    "equipment_name": "SILO A",
                    "applied_qty": 825.0,
                    "move_ids": [123],
                    "products": ["Pollard Angsa"]
                },
                ...
            ],
            "errors": []
        }
        """
        try:
            data = self._get_json_payload()
            
            if not data.get('mo_id'):
                return {
                    'status': 'error',
                    'message': 'mo_id is required',
                }
            
            from ..services.middleware_service import MiddlewareService
            service = MiddlewareService(request.env)
            result = service.update_mo_with_consumptions(data)
            return result
            
        except Exception as e:
            _logger.error(f'Error updating MO with consumptions: {str(e)}')
            return {
                'status': 'error',
                'message': str(e),
            }

    @http.route('/api/scada/mo-weight', type='json', auth='user', methods=['POST'])
    def create_mo_weight(self, **kwargs):
        """
        Create MO weight record

        Body:
        {
            "mo_id": "MO/2025/001",
            "weight_actual": 1200.5,
            "timestamp": "2025-02-06T10:30:00",
            "notes": "Weighing after production"
        }
        """
        try:
            data = self._get_json_payload()
            service = MoWeightService(request.env)
            return service.create_mo_weight(data)
        except Exception as e:
            _logger.error(f'Error creating MO weight: {str(e)}')
            return {'status': 'error', 'message': str(e)}

    @http.route('/api/scada/mo-weight', type='json', auth='user', methods=['GET'])
    def get_mo_weights(self, **kwargs):
        """
        Get MO weight records

        Query params:
            mo_id: MO name or ID (optional)
            limit: jumlah data (default 50)
            offset: offset data (default 0)
        """
        try:
            mo_id = request.httprequest.args.get('mo_id')
            limit = int(request.httprequest.args.get('limit', 50))
            offset = int(request.httprequest.args.get('offset', 0))

            service = MoWeightService(request.env)
            return service.get_mo_weights(mo_value=mo_id, limit=limit, offset=offset)
        except Exception as e:
            _logger.error(f'Error getting MO weights: {str(e)}')
            return {'status': 'error', 'message': str(e)}

    # ===== OEE =====

    @http.route('/api/scada/oee-detail', type='json', auth='user', methods=['POST'])
    def get_oee_detail(self, **kwargs):
        """
        Get OEE detail data for frontend.

        Params (JSON-RPC params):
            - oee_id (optional): specific OEE record id
            - mo_id (optional): MO name or ID
            - equipment_code (optional): filter by equipment code
            - date_from (optional): YYYY-MM-DD
            - date_to (optional): YYYY-MM-DD
            - limit (optional): default 50
            - offset (optional): default 0
        """
        try:
            data = self._get_json_payload()
            limit = int(data.get('limit', 50))
            offset = int(data.get('offset', 0))

            oee_model = request.env['scada.equipment.oee']
            domain = []

            oee_id = data.get('oee_id')
            if oee_id:
                domain.append(('id', '=', int(oee_id)))

            mo_value = data.get('mo_id')
            if mo_value:
                mo_id = None
                if isinstance(mo_value, int) or str(mo_value).isdigit():
                    mo_id = int(mo_value)
                else:
                    mo = request.env['mrp.production'].search([
                        ('name', '=', str(mo_value))
                    ], limit=1)
                    if mo:
                        mo_id = mo.id
                if mo_id:
                    domain.append(('manufacturing_order_id', '=', mo_id))
                else:
                    return {
                        'status': 'error',
                        'message': f'MO not found: {mo_value}',
                    }

            equipment_code = data.get('equipment_code')
            if equipment_code:
                equipment = request.env['scada.equipment'].search([
                    ('equipment_code', '=', str(equipment_code))
                ], limit=1)
                if not equipment:
                    return {
                        'status': 'error',
                        'message': f'Equipment not found: {equipment_code}',
                    }
                domain.append(('equipment_id', '=', equipment.id))

            date_from = data.get('date_from')
            if date_from:
                domain.append(('date_done', '>=', f'{date_from} 00:00:00'))
            date_to = data.get('date_to')
            if date_to:
                domain.append(('date_done', '<=', f'{date_to} 23:59:59'))

            records = oee_model.search(
                domain,
                order='date_done desc, id desc',
                limit=limit,
                offset=offset
            )

            result_data = []
            for rec in records:
                lines = []
                for line in rec.line_ids:
                    lines.append({
                        'equipment_id': line.equipment_id.id if line.equipment_id else None,
                        'equipment_code': line.equipment_code,
                        'equipment_name': line.equipment_name,
                        'to_consume': line.qty_to_consume,
                        'actual_consumed': line.qty_consumed,
                        'variance': line.variance_qty,
                        'consumption_ratio': line.consumption_ratio,
                        'material_count': line.material_count,
                    })

                result_data.append({
                    'oee_id': rec.id,
                    'date_done': rec.date_done.isoformat() if rec.date_done else None,
                    'mo_id': rec.manufacturing_order_id.name if rec.manufacturing_order_id else None,
                    'mo_record_id': rec.manufacturing_order_id.id if rec.manufacturing_order_id else None,
                    'equipment': self._get_equipment_details(rec.equipment_id),
                    'product_id': rec.product_id.id if rec.product_id else None,
                    'product_name': rec.product_id.display_name if rec.product_id else None,
                    'qty_planned': rec.qty_planned,
                    'qty_finished': rec.qty_finished,
                    'variance_finished': rec.variance_finished,
                    'yield_percent': rec.yield_percent,
                    'qty_bom_consumption': rec.qty_bom_consumption,
                    'qty_actual_consumption': rec.qty_actual_consumption,
                    'variance_consumption': rec.variance_consumption,
                    'consumption_ratio': rec.consumption_ratio,
                    'lines': lines,
                })

            return {
                'status': 'success',
                'count': len(result_data),
                'data': result_data,
            }
        except Exception as e:
            _logger.error(f'Error getting OEE detail: {str(e)}')
            return {'status': 'error', 'message': str(e)}

    @http.route('/api/scada/oee-equipment-avg', type='json', auth='user', methods=['POST'])
    def get_oee_equipment_avg(self, **kwargs):
        """
        Get average OEE report by SCADA equipment list.

        Params (JSON-RPC params):
            - equipment_code (optional)
            - equipment_type (optional)
            - is_active (optional): true/false
            - date_from (optional): YYYY-MM-DD
            - date_to (optional): YYYY-MM-DD
            - limit (optional): default 100
            - offset (optional): default 0
        """
        try:
            data = self._get_json_payload()
            limit = int(data.get('limit', 100))
            offset = int(data.get('offset', 0))

            equipment_domain = []
            if data.get('equipment_code'):
                equipment_domain.append(('equipment_code', '=', str(data.get('equipment_code'))))
            if data.get('equipment_type'):
                equipment_domain.append(('equipment_type', '=', str(data.get('equipment_type'))))
            is_active = data.get('is_active')
            if is_active is not None:
                if isinstance(is_active, bool):
                    equipment_domain.append(('is_active', '=', is_active))
                elif isinstance(is_active, str):
                    parsed_active = self._parse_bool_param(is_active, default=None)
                    if parsed_active is not None:
                        equipment_domain.append(('is_active', '=', parsed_active))

            equipment_model = request.env['scada.equipment']
            equipments = equipment_model.search(
                equipment_domain,
                order='name asc, id asc',
                limit=limit,
                offset=offset
            )

            if not equipments:
                return {
                    'status': 'success',
                    'count': 0,
                    'data': [],
                }

            equipment_ids = equipments.ids

            oee_domain = [('equipment_id', 'in', equipment_ids)]
            line_domain = [('equipment_id', 'in', equipment_ids)]

            date_from = data.get('date_from')
            if date_from:
                oee_domain.append(('date_done', '>=', f'{date_from} 00:00:00'))
                line_domain.append(('oee_id.date_done', '>=', f'{date_from} 00:00:00'))

            date_to = data.get('date_to')
            if date_to:
                oee_domain.append(('date_done', '<=', f'{date_to} 23:59:59'))
                line_domain.append(('oee_id.date_done', '<=', f'{date_to} 23:59:59'))

            oee_groups = request.env['scada.equipment.oee'].read_group(
                oee_domain,
                [
                    'equipment_id',
                    'qty_planned:avg',
                    'qty_finished:avg',
                    'variance_finished:avg',
                    'yield_percent:avg',
                    'qty_bom_consumption:avg',
                    'qty_actual_consumption:avg',
                    'variance_consumption:avg',
                    'consumption_ratio:avg',
                    'date_done:max',
                ],
                ['equipment_id'],
                lazy=False
            )

            line_groups = request.env['scada.equipment.oee.line'].read_group(
                line_domain,
                [
                    'equipment_id',
                    'qty_to_consume:avg',
                    'qty_consumed:avg',
                    'variance_qty:avg',
                    'consumption_ratio:avg',
                    'material_count:avg',
                ],
                ['equipment_id'],
                lazy=False
            )

            oee_map = {
                group['equipment_id'][0]: group
                for group in oee_groups if group.get('equipment_id')
            }
            line_map = {
                group['equipment_id'][0]: group
                for group in line_groups if group.get('equipment_id')
            }

            result_data = []
            for equipment in equipments:
                oee_stat = oee_map.get(equipment.id, {})
                line_stat = line_map.get(equipment.id, {})

                result_data.append({
                    'equipment': self._get_equipment_details(equipment),
                    'oee_records_count': oee_stat.get('__count', 0),
                    'avg_summary': {
                        'qty_planned': oee_stat.get('qty_planned_avg', 0.0),
                        'qty_finished': oee_stat.get('qty_finished_avg', 0.0),
                        'variance_finished': oee_stat.get('variance_finished_avg', 0.0),
                        'yield_percent': oee_stat.get('yield_percent_avg', 0.0),
                        'qty_bom_consumption': oee_stat.get('qty_bom_consumption_avg', 0.0),
                        'qty_actual_consumption': oee_stat.get('qty_actual_consumption_avg', 0.0),
                        'variance_consumption': oee_stat.get('variance_consumption_avg', 0.0),
                        'consumption_ratio': oee_stat.get('consumption_ratio_avg', 0.0),
                    },
                    'avg_consumption_detail': {
                        'to_consume': line_stat.get('qty_to_consume_avg', 0.0),
                        'actual_consumed': line_stat.get('qty_consumed_avg', 0.0),
                        'variance': line_stat.get('variance_qty_avg', 0.0),
                        'consumption_ratio': line_stat.get('consumption_ratio_avg', 0.0),
                        'material_count': line_stat.get('material_count_avg', 0.0),
                    },
                    'last_oee_date': oee_stat.get('date_done_max'),
                })

            return {
                'status': 'success',
                'count': len(result_data),
                'data': result_data,
            }
        except Exception as e:
            _logger.error(f'Error getting OEE equipment average: {str(e)}')
            return {'status': 'error', 'message': str(e)}

    # ===== EQUIPMENT =====

    @http.route('/api/scada/equipment/<equipment_code>', type='json', auth='user', methods=['GET'])
    def get_equipment_status(self, equipment_code, **kwargs):
        """Get equipment status"""
        try:
            result = request.env['scada.equipment'].get_equipment_status(equipment_code)
            return result
        except Exception as e:
            _logger.error(f'Error getting equipment status: {str(e)}')
            return {'status': 'error', 'message': str(e)}

    @http.route('/api/scada/equipment-failure', type='json', auth='user', methods=['POST'])
    def create_equipment_failure(self, **kwargs):
        """Create equipment failure report."""
        try:
            data = self._get_json_payload()
            equipment_code = data.get('equipment_code')
            description = data.get('description')
            date_value = data.get('date')

            if not equipment_code:
                return {'status': 'error', 'message': 'equipment_code is required'}
            if not description:
                return {'status': 'error', 'message': 'description is required'}

            equipment = request.env['scada.equipment'].search([
                ('equipment_code', '=', equipment_code),
            ], limit=1)
            if not equipment:
                return {'status': 'error', 'message': f'Equipment "{equipment_code}" not found'}

            failure_date = datetime.now()
            if date_value:
                try:
                    cleaned = str(date_value).strip().replace('T', ' ')
                    if len(cleaned) == 16:
                        cleaned = f'{cleaned}:00'
                    failure_date = datetime.fromisoformat(cleaned)
                except Exception:
                    return {
                        'status': 'error',
                        'message': 'Invalid date format. Use YYYY-MM-DD HH:MM:SS or YYYY-MM-DDTHH:MM',
                    }

            failure = request.env['scada.equipment.failure'].create({
                'equipment_id': equipment.id,
                'description': description,
                'date': failure_date,
            })
            return {
                'status': 'success',
                'message': 'Equipment failure report created',
                'data': {
                    'id': failure.id,
                    'equipment_id': equipment.id,
                    'equipment_code': equipment.equipment_code,
                    'equipment_name': equipment.name,
                    'description': failure.description,
                    'date': failure.date.isoformat() if failure.date else None,
                },
            }
        except Exception as e:
            _logger.error(f'Error creating equipment failure report: {str(e)}')
            return {'status': 'error', 'message': str(e)}

    @http.route('/api/scada/equipment-failure', type='json', auth='user', methods=['GET'])
    def get_equipment_failures(self, **kwargs):
        """Get equipment failure report list."""
        try:
            equipment_code = request.httprequest.args.get('equipment_code')
            limit = int(request.httprequest.args.get('limit', 50))
            offset = int(request.httprequest.args.get('offset', 0))

            domain = []
            if equipment_code:
                domain.append(('equipment_code', '=', equipment_code))

            failures = request.env['scada.equipment.failure'].search(
                domain,
                order='date desc, id desc',
                limit=limit,
                offset=offset,
            )

            data = []
            for failure in failures:
                data.append({
                    'id': failure.id,
                    'equipment_id': failure.equipment_id.id if failure.equipment_id else None,
                    'equipment_code': failure.equipment_code,
                    'equipment_name': failure.equipment_id.name if failure.equipment_id else None,
                    'description': failure.description,
                    'date': failure.date.isoformat() if failure.date else None,
                    'reported_by': failure.reported_by.name if failure.reported_by else None,
                })

            return {'status': 'success', 'count': len(data), 'data': data}
        except Exception as e:
            _logger.error(f'Error getting equipment failure reports: {str(e)}')
            return {'status': 'error', 'message': str(e)}

    @http.route('/api/scada/equipment-failure-report', type='json', auth='user', methods=['POST'])
    def get_equipment_failure_report(self, **kwargs):
        """Get frontend-ready equipment failure report (detail + summary)."""
        try:
            data = self._get_json_payload()

            equipment_code = data.get('equipment_code')
            date_from = data.get('date_from')
            date_to = data.get('date_to')
            period = (data.get('period') or '').strip().lower()
            limit = int(data.get('limit', 100))
            offset = int(data.get('offset', 0))

            domain = []
            if equipment_code:
                domain.append(('equipment_code', '=', str(equipment_code)))

            # Predefined period filter. date_from/date_to tetap bisa override jika dikirim.
            if period:
                now = datetime.now()
                start_dt = None
                end_dt = None

                if period == 'today':
                    start_dt = now.replace(hour=0, minute=0, second=0, microsecond=0)
                    end_dt = now.replace(hour=23, minute=59, second=59, microsecond=0)
                elif period == 'yesterday':
                    y = now - timedelta(days=1)
                    start_dt = y.replace(hour=0, minute=0, second=0, microsecond=0)
                    end_dt = y.replace(hour=23, minute=59, second=59, microsecond=0)
                elif period == 'this_week':
                    week_start = now - timedelta(days=now.weekday())
                    start_dt = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
                    end_dt = now.replace(hour=23, minute=59, second=59, microsecond=0)
                elif period == 'last_7_days':
                    start_dt = (now - timedelta(days=6)).replace(hour=0, minute=0, second=0, microsecond=0)
                    end_dt = now.replace(hour=23, minute=59, second=59, microsecond=0)
                elif period == 'this_month':
                    start_dt = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                    end_dt = now.replace(hour=23, minute=59, second=59, microsecond=0)
                elif period == 'last_month':
                    first_this_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                    last_prev_month = first_this_month - timedelta(seconds=1)
                    start_dt = last_prev_month.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                    end_dt = last_prev_month.replace(hour=23, minute=59, second=59, microsecond=0)
                elif period == 'this_year':
                    start_dt = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
                    end_dt = now.replace(hour=23, minute=59, second=59, microsecond=0)
                else:
                    return {
                        'status': 'error',
                        'message': (
                            'Invalid period value. '
                            'Supported: today, yesterday, this_week, last_7_days, '
                            'this_month, last_month, this_year'
                        ),
                    }

                if not date_from:
                    date_from = start_dt.strftime('%Y-%m-%d %H:%M:%S')
                if not date_to:
                    date_to = end_dt.strftime('%Y-%m-%d %H:%M:%S')

            if date_from:
                cleaned_from = str(date_from).strip().replace('T', ' ')
                if len(cleaned_from) == 10:
                    cleaned_from = f'{cleaned_from} 00:00:00'
                elif len(cleaned_from) == 16:
                    cleaned_from = f'{cleaned_from}:00'
                domain.append(('date', '>=', cleaned_from))

            if date_to:
                cleaned_to = str(date_to).strip().replace('T', ' ')
                if len(cleaned_to) == 10:
                    cleaned_to = f'{cleaned_to} 23:59:59'
                elif len(cleaned_to) == 16:
                    cleaned_to = f'{cleaned_to}:59'
                domain.append(('date', '<=', cleaned_to))

            failures = request.env['scada.equipment.failure'].search(
                domain,
                order='date desc, id desc',
                limit=limit,
                offset=offset,
            )

            data_rows = []
            for failure in failures:
                data_rows.append({
                    'id': failure.id,
                    'equipment_id': failure.equipment_id.id if failure.equipment_id else None,
                    'equipment_code': failure.equipment_code,
                    'equipment_name': failure.equipment_id.name if failure.equipment_id else None,
                    'description': failure.description,
                    'date': failure.date.isoformat() if failure.date else None,
                    'reported_by': failure.reported_by.name if failure.reported_by else None,
                })

            grouped = request.env['scada.equipment.failure'].read_group(
                domain,
                ['equipment_id', 'id:count', 'date:max'],
                ['equipment_id'],
                lazy=False,
            )
            by_equipment = []
            for row in grouped:
                equipment = row.get('equipment_id')
                if not equipment:
                    continue
                by_equipment.append({
                    'equipment_id': equipment[0],
                    'equipment_name': equipment[1],
                    'failure_count': row.get('id_count', 0),
                    'last_failure_date': row.get('date_max'),
                })

            total_failures = request.env['scada.equipment.failure'].search_count(domain)
            summary = {
                'total_failures': total_failures,
                'equipment_count': len(by_equipment),
                'by_equipment': by_equipment,
            }

            return {
                'status': 'success',
                'count': len(data_rows),
                'data': data_rows,
                'summary': summary,
            }
        except Exception as e:
            _logger.error(f'Error getting equipment failure report: {str(e)}')
            return {'status': 'error', 'message': str(e)}

    # ===== PRODUCTS =====

    @http.route('/api/scada/products', type='http', auth='user', methods=['GET'])
    def get_product_list(self, **kwargs):
        """
        Get list produk

        Query params:
            category_id: ID kategori (optional)
            category_name: Nama kategori (optional)
            active: true/false/all (default true)
            limit: jumlah data (default 100)
            offset: offset data (default 0)
        """
        try:
            category_id = request.httprequest.args.get('category_id')
            category_name = request.httprequest.args.get('category_name')
            active_param = request.httprequest.args.get('active')
            limit = int(request.httprequest.args.get('limit', 100))
            offset = int(request.httprequest.args.get('offset', 0))

            if category_id:
                try:
                    category_id = int(category_id)
                except ValueError:
                    payload = {'status': 'error', 'message': 'Invalid category_id'}
                    response = request.make_response(
                        json.dumps(payload),
                        headers=[('Content-Type', 'application/json')],
                    )
                    response.status_code = 400
                    return response

            active = self._parse_bool_param(active_param, default=True)

            service = ProductService(request.env)
            payload = service.get_product_list(
                category_id=category_id,
                category_name=category_name,
                limit=limit,
                offset=offset,
                active=active
            )
            response = request.make_response(
                json.dumps(payload),
                headers=[('Content-Type', 'application/json')],
            )
            response.status_code = 200
            return response
        except Exception as e:
            _logger.error(f'Error getting product list: {str(e)}')
            payload = {'status': 'error', 'message': str(e)}
            response = request.make_response(
                json.dumps(payload),
                headers=[('Content-Type', 'application/json')],
            )
            response.status_code = 500
            return response

    @http.route('/api/scada/products', type='json', auth='user', methods=['POST'])
    def get_product_list_json(self, **kwargs):
        """Get list produk (JSON-RPC)."""
        try:
            data = request.jsonrequest or {}
            params = data.get('params') if isinstance(data, dict) else {}
            if not isinstance(params, dict):
                params = {}
            if kwargs:
                params.update(kwargs)

            category_id = params.get('category_id')
            category_name = params.get('category_name')
            active_param = params.get('active')
            limit = int(params.get('limit', 100))
            offset = int(params.get('offset', 0))

            if category_id:
                try:
                    category_id = int(category_id)
                except ValueError:
                    return {'status': 'error', 'message': 'Invalid category_id'}

            active = self._parse_bool_param(active_param, default=True)

            service = ProductService(request.env)
            return service.get_product_list(
                category_id=category_id,
                category_name=category_name,
                limit=limit,
                offset=offset,
                active=active
            )
        except Exception as e:
            _logger.error(f'Error getting product list (json): {str(e)}')
            return {'status': 'error', 'message': str(e)}

    @http.route('/api/scada/products-by-category', type='json', auth='user', methods=['POST'])
    def get_product_list_by_category_json(self, **kwargs):
        """Get list produk dengan filter kategori (JSON-RPC)."""
        try:
            data = request.jsonrequest or {}
            params = data.get('params') if isinstance(data, dict) else {}
            if not isinstance(params, dict):
                params = {}
            if kwargs:
                params.update(kwargs)

            category_id = params.get('category_id')
            category_name = params.get('category_name')
            active_param = params.get('active')
            limit = int(params.get('limit', 100))
            offset = int(params.get('offset', 0))

            if category_id:
                try:
                    category_id = int(category_id)
                except ValueError:
                    return {'status': 'error', 'message': 'Invalid category_id'}

            active = self._parse_bool_param(active_param, default=True)

            service = ProductService(request.env)
            return service.get_product_list(
                category_id=category_id,
                category_name=category_name,
                limit=limit,
                offset=offset,
                active=active
            )
        except Exception as e:
            _logger.error(f'Error getting product list by category (json): {str(e)}')
            return {'status': 'error', 'message': str(e)}

    # ===== BOM =====

    @http.route('/api/scada/boms', type='http', auth='user', methods=['GET'])
    def get_bom_list(self, **kwargs):
        """
        Get list BoM beserta komponen.

        Query params:
            bom_id: ID BoM (optional)
            product_id: ID product variant (optional)
            product_tmpl_id: ID product template (optional)
            active: true/false/all (default true)
            limit: jumlah data (default 100)
            offset: offset data (default 0)
        """
        try:
            bom_id = request.httprequest.args.get('bom_id')
            product_id = request.httprequest.args.get('product_id')
            product_tmpl_id = request.httprequest.args.get('product_tmpl_id')
            active_param = request.httprequest.args.get('active')
            limit = int(request.httprequest.args.get('limit', 100))
            offset = int(request.httprequest.args.get('offset', 0))

            if bom_id:
                try:
                    bom_id = int(bom_id)
                except ValueError:
                    payload = {'status': 'error', 'message': 'Invalid bom_id'}
                    response = request.make_response(
                        json.dumps(payload),
                        headers=[('Content-Type', 'application/json')],
                    )
                    response.status_code = 400
                    return response

            if product_id:
                try:
                    product_id = int(product_id)
                except ValueError:
                    payload = {'status': 'error', 'message': 'Invalid product_id'}
                    response = request.make_response(
                        json.dumps(payload),
                        headers=[('Content-Type', 'application/json')],
                    )
                    response.status_code = 400
                    return response

            if product_tmpl_id:
                try:
                    product_tmpl_id = int(product_tmpl_id)
                except ValueError:
                    payload = {'status': 'error', 'message': 'Invalid product_tmpl_id'}
                    response = request.make_response(
                        json.dumps(payload),
                        headers=[('Content-Type', 'application/json')],
                    )
                    response.status_code = 400
                    return response

            active = self._parse_bool_param(active_param, default=True)

            service = BomService(request.env)
            payload = service.get_bom_list(
                bom_id=bom_id,
                product_id=product_id,
                product_tmpl_id=product_tmpl_id,
                limit=limit,
                offset=offset,
                active=active,
            )
            response = request.make_response(
                json.dumps(payload),
                headers=[('Content-Type', 'application/json')],
            )
            response.status_code = 200
            return response
        except Exception as e:
            _logger.error(f'Error getting BoM list: {str(e)}')
            payload = {'status': 'error', 'message': str(e)}
            response = request.make_response(
                json.dumps(payload),
                headers=[('Content-Type', 'application/json')],
            )
            response.status_code = 500
            return response

    @http.route('/api/scada/boms', type='json', auth='user', methods=['POST'])
    def get_bom_list_json(self, **kwargs):
        """Get list BoM beserta komponen (JSON-RPC)."""
        try:
            data = request.jsonrequest or {}
            params = data.get('params') if isinstance(data, dict) else {}
            if not isinstance(params, dict):
                params = {}
            if kwargs:
                params.update(kwargs)

            bom_id = params.get('bom_id')
            product_id = params.get('product_id')
            product_tmpl_id = params.get('product_tmpl_id')
            active_param = params.get('active')
            limit = int(params.get('limit', 100))
            offset = int(params.get('offset', 0))

            if bom_id:
                try:
                    bom_id = int(bom_id)
                except ValueError:
                    return {'status': 'error', 'message': 'Invalid bom_id'}

            if product_id:
                try:
                    product_id = int(product_id)
                except ValueError:
                    return {'status': 'error', 'message': 'Invalid product_id'}

            if product_tmpl_id:
                try:
                    product_tmpl_id = int(product_tmpl_id)
                except ValueError:
                    return {'status': 'error', 'message': 'Invalid product_tmpl_id'}

            active = self._parse_bool_param(active_param, default=True)

            service = BomService(request.env)
            return service.get_bom_list(
                bom_id=bom_id,
                product_id=product_id,
                product_tmpl_id=product_tmpl_id,
                limit=limit,
                offset=offset,
                active=active,
            )
        except Exception as e:
            _logger.error(f'Error getting BoM list (json): {str(e)}')
            return {'status': 'error', 'message': str(e)}
