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


class KunjunganKunjungan(http.Controller):

	@http.route('/get_master_jenis_kunjungan', auth="none", type='json',cors='*')
	def get_master_jenis_kunjungan(self, **rec):
		try:
			if request.jsonrequest :
				master = request.env['master.jenis.kunjungan'].sudo().search([])
				data_master = []
				for m in master:
					value = {   'id'                        : m.id,
								'jenis_kunjungan'           : m.jenis_kunjungan or None,
								'id_kunjungan'              : m.id_kunjungan or None
									   
									  }
		
					data_master.append(value)
				return ({"message": "List Master Jenis Kunjungan", "Data": data_master})
			else :
				return ({'result':'Failed Check Your Parameter'})
		except Exception as e:
			return {'status': False, 'error': str(e)}


	@http.route('/get_master_solusi_kunjungan', auth="none", type='json',cors='*')
	def get_master_solusi_kunjungan(self, **rec):
		try:
			if request.jsonrequest :
				master = request.env['master.solusi.kunjungan'].sudo().search([])
				data_master = []
				for m in master:
					value = {   'id'                        : m.id,
								'solusi_kunjungan'          : m.solusi_kunjungan or None,
								'kode'                      : m.kode or None
									   
									  }
		
					data_master.append(value)
				return ({"message": "List Master Solusi Kunjungan", "Data": data_master})
			else :
				return ({'result':'Failed Check Your Parameter'})
		except Exception as e:
			return {'status': False, 'error': str(e)}


	@http.route('/create_form_kunjungan', auth="none", type='json',cors='*')
	def create_form_kunjungan(self, **rec):
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
					if rec.get('note') :
						note = rec['note']
					else :
						note = False
					if rec.get("jenis_kunjungan_ids"):
						jenis_ids = []
						for j in rec["jenis_kunjungan_ids"]:
							data = request.env['master.jenis.kunjungan'].search([('id','=',j['id'])])
							if data :
								jenis_ids.append(data.id)

					if rec.get("solusi_kunjungan_ids"):
						solusi_ids = []
						for s in rec["solusi_kunjungan_ids"]:
							data = request.env['master.solusi.kunjungan'].search([('id','=',s['id'])])
							if data :
								solusi_ids.append(data.id)
					

					value_data = {  'peternak_id': peternak_id,
									'petugas_id': petugas_id,
									'tanggal_kunjungan': tanggal_kunjungan,
									'note': note,
									'jenis_kunjungan_ids': [(6,0, jenis_ids)] or None,
									'solusi_kunjungan_ids': [(6,0, solusi_ids)] or None,
									  }

					new_record = request.env['form.kunjungan'].sudo().create(value_data)

					if new_record :
						return ({'result':'Create Form Kunjungan Success...!!'})
					else :
						return ({'result':'Create Form Kunjungan Gagal...!!'})


				return ({'result':'Failed Check Your Parameter'})
		except Exception as e:
			return {'status': False, 'error': str(e)}

		
