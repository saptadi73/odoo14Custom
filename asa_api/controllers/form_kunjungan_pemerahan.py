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


class KunjunganPemerahan(http.Controller):

	@http.route('/create_form_kunjungan_pemerahan', auth="none", type='json',cors='*')
	def create_form_kunjungan_pemerahan(self, **rec):
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
					if rec.get('kebersihan_susu') :
						kebersihan_susu = rec['kebersihan_susu']
					else :
						kebersihan_susu = False
					if rec.get('kebersihan_milkcan') :
						kebersihan_milkcan = rec['kebersihan_milkcan']
					else :
						kebersihan_milkcan = False
					if rec.get('kebersihan_ember_perah') :
						kebersihan_ember_perah = rec['kebersihan_ember_perah']
					else :
						kebersihan_ember_perah = False
					if rec.get('kebersihan_kandang') :
						kebersihan_kandang = rec['kebersihan_kandang']
					else :
						kebersihan_kandang = False
					if rec.get('kebersihan_sapi') :
						kebersihan_sapi = rec['kebersihan_sapi']
					else :
						kebersihan_sapi = False
					if rec.get('kebersihan_peternak') :
						kebersihan_peternak = rec['kebersihan_peternak']
					else :
						kebersihan_peternak = False
					if rec.get('penyetoran') :
						penyetoran = rec['penyetoran']
					else :
						penyetoran = False

					value_data = {  'peternak_id': peternak_id,
									'petugas_id': petugas_id,
									'tanggal_kunjungan': tanggal_kunjungan,
									'periode_id': periode_id,
									'jenis_management': '3',
									'keber_susu': kebersihan_susu,
									'keber_can': kebersihan_milkcan,
									'keber_ember': kebersihan_ember_perah,
									'keber_kandang': kebersihan_kandang,
									'keber_sapi': kebersihan_sapi,
									'keber_peternak': kebersihan_peternak,
									'penyetoran': penyetoran
									  }

					new_record = request.env['form.kunjungan.gdfp'].sudo().create(value_data)

					if new_record :
						return ({'result':'Create Form Kunjungan Pemerahan Success...!!'})
					else :
						return ({'result':'Create Form Kunjungan Pemerahan Gagal...!!'})


				return ({'result':'Failed Check Your Parameter'})
		except Exception as e:
			return {'status': False, 'error': str(e)}

		
