"""
SCADA Main Controller - JSON-RPC API
Simple JSON-RPC endpoints optimized for Vue.js frontend

Authentication: Odoo Session (JSON-RPC)
"""

from odoo import http
from odoo.http import request
import logging
import json
from datetime import datetime
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
        
        POST /api/scada/material-consumption
        Auth: Session cookie
        
        Body:
        {
            "equipment_id": "PLC01",
            "product_id": 123,
            "quantity": 10.5,
            "timestamp": "2025-02-06T10:30:00",
            "mo_id": "MO/2025/001"
        }
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
        """Get confirmed MO list (minimal fields)."""
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
                data.append({
                    'mo_id': mo.name,
                    'reference': mo.origin or None,
                    'schedule': mo.date_planned_start.isoformat() if mo.date_planned_start else None,
                    'product': mo.product_id.display_name if mo.product_id else None,
                    'quantity': mo.product_qty,
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
                        'equipment_id': component_equipment.id if component_equipment else None,
                        'equipment_code': component_equipment.equipment_code if component_equipment else None,
                        'equipment_name': component_equipment.name if component_equipment else None,
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
