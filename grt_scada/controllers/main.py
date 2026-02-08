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
            data = request.get_json_data() or {}
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
        Create material consumption record
        
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
            data = request.get_json_data() or {}
            result = request.env['scada.material.consumption'].create_from_api(data)
            return result
        except Exception as e:
            _logger.error(f'Error creating material consumption: {str(e)}')
            return {'status': 'error', 'message': str(e)}

    @http.route('/api/scada/material-consumption/<int:record_id>', type='json', auth='user', methods=['GET'])
    def get_material_consumption(self, record_id, **kwargs):
        """Get material consumption by ID"""
        try:
            result = request.env['scada.material.consumption'].get_by_id(
                record_id,
                fields=['id', 'equipment_id', 'product_id', 'quantity', 'timestamp', 'status']
            )
            return result
        except Exception as e:
            _logger.error(f'Error getting material consumption: {str(e)}')
            return {'status': 'error', 'message': str(e)}

    @http.route('/api/scada/material-consumption/validate', type='json', auth='user', methods=['POST'])
    def validate_material_consumption(self, **kwargs):
        """Validate material consumption payload"""
        try:
            data = request.get_json_data() or {}
            result = request.env['scada.material.consumption'].validate_payload(data)
            return result
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

            result = request.env['scada.mo.data'].get_mo_list_for_equipment(
                equipment_code, status=mo_status, limit=limit, offset=offset
            )
            return result
        except Exception as e:
            _logger.error(f'Error getting MO list: {str(e)}')
            return {'status': 'error', 'message': str(e)}

    @http.route('/api/scada/mo/<int:mo_id>/acknowledge', type='json', auth='user', methods=['POST'])
    def acknowledge_mo(self, mo_id, **kwargs):
        """Acknowledge MO"""
        try:
            data = request.get_json_data() or {}
            result = request.env['scada.mo.data'].acknowledge_mo(mo_id, data)
            return result
        except Exception as e:
            _logger.error(f'Error acknowledging MO: {str(e)}')
            return {'status': 'error', 'message': str(e)}

    @http.route('/api/scada/mo/<int:mo_id>/update-status', type='json', auth='user', methods=['POST'])
    def update_mo_status(self, mo_id, **kwargs):
        """Update MO status"""
        try:
            data = request.get_json_data() or {}
            result = request.env['scada.mo.data'].update_mo_status(mo_id, data)
            return result
        except Exception as e:
            _logger.error(f'Error updating MO status: {str(e)}')
            return {'status': 'error', 'message': str(e)}

    @http.route('/api/scada/mo/<int:mo_id>/mark-done', type='json', auth='user', methods=['POST'])
    def mark_mo_done(self, mo_id, **kwargs):
        """Mark MO as done"""
        try:
            data = request.get_json_data() or {}
            result = request.env['scada.mo.data'].mark_mo_done(mo_id, data)
            return result
        except Exception as e:
            _logger.error(f'Error marking MO done: {str(e)}')
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
            data = request.get_json_data() or {}
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
