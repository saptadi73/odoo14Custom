import json
import requests
from odoo.tests import Form
import werkzeug.wrappers

from odoo import http, _, exceptions
from odoo.http import content_disposition, request
import io

class peternak_sapi_rest_api(http.Controller):
    @http.route(['/api/peternak_sapi_get/'], type="http", auth="public", methods=['GET'], csrf=False)
    def peternak_sapi_restapi_get(self, **params):
        peternak_sapi = request.env['peternak_sapi'].sudo().search([])
        dict_peternak_sapi = {}
        data_peternak_sapi = []
        for h in peternak_sapi:
            dict_detail_sapi = {}
            detail_sapi = []
        for s in h.sapi_ids:
            dict_detail_sapi = {'first_name': s.first_name, 'kandang_id': s.kandang_id.id, 'sex': s.sex,
                                'date_of_birth': s.date_of_birth, 'jenis_sapi': s.jenis_sapi.name, 'state': s.state}
            detail_sapi.append(dict_detail_sapi)
        dict_peternak_sapi = {'sapi_ids': detail_sapi}
        data_peternak_sapi.append(dict_peternak_sapi)
        data = {
            'status': 200,
            'message': 'success',
            'response': data_peternak_sapi
        }
        try:
            return werkzeug.wrappers.Response(
                status=200,
                content_type='application/json; charset=utf-8',
                response=json.dumps(data)
                )
        except:
            return werkzeug.wrappers.Response(
                status=400,
                content_type='application/json; charset=utf-8',
                headers=[('Access-Control-Allow-Origin', '*')],
                response=json.dumps({
                    'error': 'Error',
                    'error_descrip': 'Error Description',
                })
            )