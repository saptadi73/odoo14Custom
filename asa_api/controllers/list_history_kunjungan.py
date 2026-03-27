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

	@http.route('/list_management_kandang', auth="none", type='json',cors='*')
	def list_management_kandang(self, **rec):
		try:
			header = request.httprequest.headers
			db= header.get('db')
			login = header.get('login')
			password = header.get('password')
			uid = request.session.authenticate(db, login, password)
			if uid:
				if request.jsonrequest :
					kunjungan_kandang = request.env['form.kunjungan.gdfp'].search([('jenis_management','=','2')])
					if kunjungan_kandang :
						data_kunjungan = []
						for kunjungan in kunjungan_kandang :
							value = {   'peternak_id'    : kunjungan.peternak_id.id or None,
										'kode_peternak'  : kunjungan.kode_peternak or None,
										'tgl_kunjungan'  : kunjungan.tanggal_kunjungan or None,
										'tps_id'         : kunjungan.peternak_id.tps_id.id or None,
										'tps_name'       : kunjungan.peternak_id.tps_id.tps_name or None,
										'atap'      	 : dict(kunjungan._fields['atap'].selection).get(kunjungan.atap) or None,
										'lantai'         : dict(kunjungan._fields['lantai'].selection).get(kunjungan.lantai) or None,
										'thi_index'      : dict(kunjungan._fields['thi_index'].selection).get(kunjungan.thi_index) or None,
										'palungan'       : dict(kunjungan._fields['palungan'].selection).get(kunjungan.palungan) or None,
										'water_adlib'    : dict(kunjungan._fields['water_adlib'].selection).get(kunjungan.water_adlib) or None,
										   
								}
			
							data_kunjungan.append(value)

						return ({"message": "Data Kunjungan", "Data": data_kunjungan})
					else :
						return ({'result':'Data Kunjungan Pakan tidak ditemukan'})


				else :
					return ({'result':'Failed Check Your Parameter'})
		except Exception as e:
			return {'status': False, 'error': str(e)}


	@http.route('/list_management_pemerahan', auth="none", type='json',cors='*')
	def list_management_pemerahan(self, **rec):
		try:
			header = request.httprequest.headers
			db= header.get('db')
			login = header.get('login')
			password = header.get('password')
			uid = request.session.authenticate(db, login, password)
			if uid:
				if request.jsonrequest :
					kunjungan_pemerahan = request.env['form.kunjungan.gdfp'].search([('jenis_management','=','3')])
					if kunjungan_pemerahan :
						data_kunjungan = []
						for kunjungan in kunjungan_pemerahan :
							value = {   'peternak_id'     : kunjungan.peternak_id.id or None,
										'kode_peternak'   : kunjungan.kode_peternak or None,
										'tgl_kunjungan'   : kunjungan.tanggal_kunjungan or None,
										'tps_id'          : kunjungan.peternak_id.tps_id.id or None,
										'tps_name'        : kunjungan.peternak_id.tps_id.tps_name or None,
										'keber_susu'      : dict(kunjungan._fields['keber_susu'].selection).get(kunjungan.keber_susu) or None,
										'keber_can'       : dict(kunjungan._fields['keber_can'].selection).get(kunjungan.keber_can) or None,
										'keber_ember'     : dict(kunjungan._fields['keber_ember'].selection).get(kunjungan.keber_ember) or None,
										'keber_kandang'   : dict(kunjungan._fields['keber_kandang'].selection).get(kunjungan.keber_kandang) or None,
										'keber_sapi'      : dict(kunjungan._fields['keber_sapi'].selection).get(kunjungan.keber_sapi) or None,
										'keber_peternak'  : dict(kunjungan._fields['keber_peternak'].selection).get(kunjungan.keber_peternak) or None,
										'penyetoran'      : dict(kunjungan._fields['penyetoran'].selection).get(kunjungan.penyetoran) or None,
										   
								}
			
							data_kunjungan.append(value)

						return ({"message": "Data Kunjungan", "Data": data_kunjungan})
					else :
						return ({'result':'Data Kunjungan Pemerahan tidak ditemukan'})


				else :
					return ({'result':'Failed Check Your Parameter'})
		except Exception as e:
			return {'status': False, 'error': str(e)}


	@http.route('/list_management_dsb', auth="none", type='json',cors='*')
	def list_management_dsb(self, **rec):
		try:
			header = request.httprequest.headers
			db= header.get('db')
			login = header.get('login')
			password = header.get('password')
			uid = request.session.authenticate(db, login, password)
			if uid:
				if request.jsonrequest :
					kunjungan_dsb = request.env['form.kunjungan.gdfp'].search([('jenis_management','=','4')])
					print ("=================daya saing============", kunjungan_dsb)
					if kunjungan_dsb :
						data_kunjungan = []
						for kunjungan in kunjungan_dsb :
							value = {   'peternak_id'   : kunjungan.peternak_id.id or None,
										'kode_peternak' : kunjungan.kode_peternak or None,
										'tgl_kunjungan' : kunjungan.tanggal_kunjungan or None,
										'tps_id'        : kunjungan.peternak_id.tps_id.id or None,
										'tps_name'      : kunjungan.peternak_id.tps_id.tps_name or None,
										'listrik'      	: kunjungan.listrik or None,
										'pakan'       	: kunjungan.pakan or None,
										'air'     		: kunjungan.air or None,
										'tenaga_kerja'  : kunjungan.tenaga_kerja or None,
										'bbm'      		: kunjungan.bbm or None,
										'ib'  			: kunjungan.ib or None,
										'keswan'      	: kunjungan.keswan or None,
										'pakan_tambah'  : kunjungan.pakan_tambah or None,
										'total_biaya'  	: kunjungan.total_biaya or None,
										   
								}
			
							data_kunjungan.append(value)

						return ({"message": "Data Kunjungan", "Data": data_kunjungan})
					else :
						return ({'result':'Data Kunjungan DSB tidak ditemukan'})


				else :
					return ({'result':'Failed Check Your Parameter'})
		except Exception as e:
			return {'status': False, 'error': str(e)}



	@http.route('/list_management_limbah', auth="none", type='json',cors='*')
	def list_management_limbah(self, **rec):
		try:
			header = request.httprequest.headers
			db= header.get('db')
			login = header.get('login')
			password = header.get('password')
			uid = request.session.authenticate(db, login, password)
			if uid:
				if request.jsonrequest :
					kunjungan_limbah = request.env['form.kunjungan.gdfp'].search([('jenis_management','=','5')])
					if kunjungan_limbah :
						data_kunjungan = []
						for kunjungan in kunjungan_limbah :
							value = {   'peternak_id'   : kunjungan.peternak_id.id or None,
										'kode_peternak' : kunjungan.kode_peternak or None,
										'tgl_kunjungan' : kunjungan.tanggal_kunjungan or None,
										'tps_id'        : kunjungan.peternak_id.tps_id.id or None,
										'tps_name'      : kunjungan.peternak_id.tps_id.tps_name or None,
										'limbah'      	: dict(kunjungan._fields['limbah'].selection).get(kunjungan.limbah) or None,
										   
								}
			
							data_kunjungan.append(value)

						return ({"message": "Data Kunjungan", "Data": data_kunjungan})
					else :
						return ({'result':'Data Kunjungan Limbah tidak ditemukan'})


				else :
					return ({'result':'Failed Check Your Parameter'})
		except Exception as e:
			return {'status': False, 'error': str(e)}



	@http.route('/list_history_kunjungan', auth="none", type='json',cors='*')
	def list_history_kunjungan(self, **rec):
		try:
			header = request.httprequest.headers
			db= header.get('db')
			login = header.get('login')
			password = header.get('password')
			uid = request.session.authenticate(db, login, password)
			if uid:
				if request.jsonrequest :
					kunjungan_history = request.env['form.kunjungan'].search([])
					if kunjungan_history :
						data_kunjungan = []
						for kunjungan in kunjungan_history :
							value = {   'peternak_id'   		: kunjungan.peternak_id.id or None,
										'kode_peternak' 		: kunjungan.kode_peternak or None,
										'tgl_kunjungan' 		: kunjungan.tanggal_kunjungan or None,
										'tps_id'        		: kunjungan.peternak_id.tps_id.id or None,
										'tps_name'      		: kunjungan.peternak_id.tps_id.tps_name or None,
										'jenis_kunjungan_ids'   : kunjungan.jenis_kunjungan_ids.ids or None,
										'solusi_kunjungan_ids'  : kunjungan.solusi_kunjungan_ids.ids or None,
										'note' 					: kunjungan.note or None,
										   
								}
			
							data_kunjungan.append(value)

						return ({"message": "Data Kunjungan", "Data": data_kunjungan})
					else :
						return ({'result':'Data Kunjungan tidak ditemukan'})


				else :
					return ({'result':'Failed Check Your Parameter'})
		except Exception as e:
			return {'status': False, 'error': str(e)}

