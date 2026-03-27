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


class KunjunganDsb(http.Controller):

	@http.route('/create_form_kunjungan_dsb', auth="none", type='json',cors='*')
	def create_form_kunjungan_dsb(self, **rec):
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
					if rec.get('listrik') :
						listrik = rec['listrik']
					else :
						listrik = False
					if rec.get('pakan') :
						pakan = rec['pakan']
					else :
						pakan = False
					if rec.get('air') :
						air = rec['air']
					else :
						air = False
					if rec.get('tenaga_kerja') :
						tenaga_kerja = rec['tenaga_kerja']
					else :
						tenaga_kerja = False
					if rec.get('bbm') :
						bbm = rec['bbm']
					else :
						bbm = False
					if rec.get('ib') :
						ib = rec['ib']
					else :
						ib = False
					if rec.get('kesehatan_hewan') :
						kesehatan_hewan = rec['kesehatan_hewan']
					else :
						kesehatan_hewan = False
					if rec.get('pakan_tambah') :
						pakan_tambah = rec['pakan_tambah']
					else :
						pakan_tambah = False

					if rec.get('peternak_id') and rec.get('periode_id') :
						peternak = int(rec['peternak_id'])
						periode = int(rec['periode_id'])
						liter = request.env['liter.sapi'].search([('peternak_id', '=', peternak),('periode_id', '=', periode)], limit=1)
						print ("============liter sapi===========", liter, rec['peternak_id'], rec['periode_id'])
						if liter:
							juml_susu_periode  = liter.setoran
							harga_susu         = liter.harga_real
						else :
							juml_susu_periode  = 0
							harga_susu         = 0

					else :
						juml_susu_periode  = 0
						harga_susu         = 0


					value_data = {  'peternak_id': peternak_id,
									'petugas_id': petugas_id,
									'tanggal_kunjungan': tanggal_kunjungan,
									'periode_id': periode_id,
									'jenis_management': '4',
									'listrik': listrik,
									'pakan': pakan,
									'air': air,
									'tenaga_kerja': tenaga_kerja,
									'bbm': bbm,
									'ib': ib,
									'keswan': kesehatan_hewan,
									'pakan_tambah': pakan_tambah,
									'juml_susu_periode': juml_susu_periode,
									'harga_susu': harga_susu,

									  }

					new_record = request.env['form.kunjungan.gdfp'].sudo().create(value_data)

					if new_record :
						return ({'result':'Create Form Kunjungan DSB Success...!!'})
					else :
						return ({'result':'Create Form Kunjungan DSB Gagal...!!'})


				return ({'result':'Failed Check Your Parameter'})
		except Exception as e:
			return {'status': False, 'error': str(e)}

		
