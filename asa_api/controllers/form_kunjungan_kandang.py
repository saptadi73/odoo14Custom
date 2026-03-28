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


class KunjunganPakan(http.Controller):

	@http.route('/get_master_periode', auth="none", type='json',cors='*')
	def get_master_reproduksi(self, **rec):
		try:
			if request.jsonrequest :
				master = request.env['periode.setoran'].sudo().search([])
				data_master = []
				for m in master:
					value = { 	'id'        				: m.id,
								'periode_setoran'			: m.periode_setoran or None,
								'periode_setoran_awal' 		: m.periode_setoran_awal or None,
								'periode_setoran_akhir' 	: m.periode_setoran_akhir or None,
									   
									  }
		
					data_master.append(value)
				return ({"message": "List Master Periode Setoran", "Data": data_master})
			else :
				return ({'result':'Failed Check Your Parameter'})
		except Exception as e:
			return {'status': False, 'error': str(e)}


	@http.route('/create_form_kunjungan_kandang', auth="none", type='json',cors='*')
	def create_form_kunjungan_kandang(self, **rec):
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
					if rec.get('atap') :
						atap = rec['atap']
					else :
						atap = False
					if rec.get('lantai') :
						lantai = rec['lantai']
					else :
						lantai = False
					if rec.get('thi_index') :
						thi_index = rec['thi_index']
					else :
						thi_index = False
					if rec.get('palungan') :
						palungan = rec['palungan']
					else :
						palungan = False
					if rec.get('water_adlib') :
						water_adlib = rec['water_adlib']
					else :
						water_adlib = False

					value_data = {  'peternak_id': peternak_id,
									'petugas_id': petugas_id,
									'tanggal_kunjungan': tanggal_kunjungan,
									'periode_id': periode_id,
									'jenis_management': '2',
									'atap': atap,
									'lantai': lantai,
									'thi_index': thi_index,
									'palungan': palungan,
									'water_adlib': water_adlib
									  }

					new_record = request.env['form.kunjungan.gdfp'].sudo().create(value_data)

					if new_record :
						return ({'result':'Create Form Kunjungan Kandang Success...!!'})
					else :
						return ({'result':'Create Form Kunjungan Kandang Gagal...!!'})


				return ({'result':'Failed Check Your Parameter'})
		except Exception as e:
			return {'status': False, 'error': str(e)}

		
