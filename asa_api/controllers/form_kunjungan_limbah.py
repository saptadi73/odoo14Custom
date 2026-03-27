# -*- coding: utf-8 -*-
import json
import logging
import functools
import werkzeug.wrappers

from odoo import http
from odoo.addons.asa_api.models.common import invalid_response, valid_response
from odoo.exceptions import AccessDenied, AccessError
from odoo.http import request
from odoo.addons.asa_api.controllers.controllers import validate_token

_logger = logging.getLogger(__name__)


class KunjunganLimbah(http.Controller):

	@http.route('/create_form_kunjungan_limbah', auth="none", type='json',cors='*')
	def create_form_kunjungan_limbah(self, **rec):
		try:
			header = request.httprequest.headers
			db= header.get('db')
			login = header.get('login')
			password = header.get('password')
			uid = request.session.authenticate(db, login, password)
			if uid:
				if request.jsonrequest :
					if rec.get('peternak_id') :
						peternak_id = rec['peternak_id']
					else :
						peternak_id = False
					if rec.get('petugas_id') :
						petugas_id = rec['petugas_id']
					else :
						petugas_id = False
					if rec.get('tgl_kunjungan') :
						tanggal_kunjungan = rec['tgl_kunjungan']
					else :
						tanggal_kunjungan = False
					if rec.get('periode_id') :
						periode_id = rec['periode_id']
					else :
						periode_id = False
					if rec.get('limbah') :
						limbah = rec['limbah']
						nilai  = int(rec['limbah'])
					else :
						limbah = False
						nilai = False
					
					value_data = {  'peternak_id': peternak_id,
									'petugas_id': petugas_id,
									'tanggal_kunjungan': tanggal_kunjungan,
									'periode_id': periode_id,
									'jenis_management': '5',
									'limbah': limbah,
									'nilai_limbah': nilai
									  }

					new_record = request.env['form.kunjungan.gdfp'].sudo().create(value_data)

					if new_record :
						return ({'result':'Create Form Kunjungan Limbah Success...!!'})
					else :
						return ({'result':'Create Form Kunjungan Limbah Gagal...!!'})


				return ({'result':'Failed Check Your Parameter'})
		except Exception as e:
			return {'status': False, 'error': str(e)}

		
