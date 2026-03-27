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


class SapiApi(http.Controller):

	@http.route('/create_form_palpasi', auth="none", type='json',cors='*')
	def create_form_palpasi(self, **rec):
		try:
			header = request.httprequest.headers
			db= header.get('db')
			login = header.get('login')
			password = header.get('password')
			uid = request.session.authenticate(db, login, password)
			if uid:
				print ("===============ok================")
				if request.jsonrequest :
					if rec.get('peternak_id') :
						peternak_id = rec['peternak_id']
					else :
						peternak_id = False
					if rec.get('petugas_id') :
						petugas = rec['petugas_id']
					else :
						petugas = False
					if rec.get('tgl_layanan') :
						tgl_layanan = rec['tgl_layanan']
					else :
						tgl_layanan = False
					if rec.get('eartag_id') :
						sapi = request.env['sapi'].sudo().search([('eartag_id','=',rec['eartag_id'])])
						id_sapi = sapi.id
						eartag = rec.get('eartag_id')
					else :
						id_sapi = False
						eartag = False
					# if rec.get('id_sapi') :
					# 	sapi_id = rec['id_sapi']
					# else :
					# 	sapi_id = False
					if rec.get('alsn_pal_rek_id') :
						alsn_pal_rek_id = rec['alsn_pal_rek_id']
					else :
						alsn_pal_rek_id = False
					if rec.get('uterus_id') :
						uterus_id = rec['uterus_id']
					else :
						uterus_id = False
					if rec.get('ovarikiri_id') :
						ovarikiri_id = rec['ovarikiri_id']
					else :
						ovarikiri_id = False
					if rec.get('ovarikanan_id') :
						ovarikanan_id = rec['ovarikanan_id']
					else :
						ovarikanan_id = False
					if rec.get('cervix_id') :
						cervix_id = rec['cervix_id']
					else :
						cervix_id = False
					if rec.get('perk_siklus') :
						perk_siklus = rec['perk_siklus']
					else :
						perk_siklus = False
					if rec.get('cat_petugas') :
						cat_petugas = rec['cat_petugas']
					else :
						cat_petugas = False
					if rec.get('bcs') :
						bcs = rec['bcs']
					else :
						bcs = False

					petugas_id = request.env['medical.physician'].sudo().search([('id','=',rec['petugas_id'])], limit=1)
					# sapi = request.env['sapi'].sudo().search([('id','=',rec['id_sapi'])],limit=1)
					value_data = {  'peternak_id': peternak_id,
									'petugas_id': petugas,
									'jabatan_id': petugas_id.jabatan_id.id,
									'tgl_layanan': tgl_layanan,
									'id_sapi': id_sapi,
									'eartag_id': eartag,
									'alsn_pal_rek_id': alsn_pal_rek_id,
									'uterus_id': uterus_id,
									'ovarikiri_id': ovarikiri_id,
									'ovarikanan_id': ovarikanan_id,
									'cervix_id': cervix_id,
									'perk_siklus': perk_siklus,
									'cat_petugas': cat_petugas,
									'bcs': bcs
									  }

					new_record = request.env['form.pr'].sudo().create(value_data)
					new_record._onchange_peternak_id()
					new_record._onchange_petugas_id()
					new_record._onchange_tgl_layanan()
					if new_record :
						return ({'result':'Create Form Palpasi Success...!!', "ID Layanan": new_record.id})
					else :
						return ({'result':'Create Form Palpasi Gagal...!!'})

					
				return ({'result':'Failed Check Your Parameter'})
		except Exception as e:
			return {'status': False, 'error': str(e)}


	@http.route('/get_master_alasan_palpasi', auth="none", type='json',cors='*')
	def get_master_alasan_palpasi(self, **rec):
		try:
			if request.jsonrequest :
				master = request.env['master.alasan.palpasi'].sudo().search([])
				data_master = []
				for m in master:
					value = { 	'id'        				: m.id,
								'kode'						: m.kode or None,
								'nama_alasan_palpasi' 		: m.nama_alasan_palpasi or None,
									   
									  }
		
					data_master.append(value)
				return ({"message": "List Master Alasan Palpasi", "Data": data_master})
			else :
				return ({'result':'Failed Check Your Parameter'})
		except Exception as e:
			return {'status': False, 'error': str(e)}


	@http.route('/get_master_uterus', auth="none", type='json',cors='*')
	def get_master_uterus(self, **rec):
		try:
			if request.jsonrequest :
				master = request.env['master.temuan.uterus'].sudo().search([])
				data_master = []
				for m in master:
					value = { 	'id'        				: m.id,
								'kode'						: m.kode or None,
								'nama_temuan_uterus' 		: m.nama_temuan_uterus or None,
									   
									  }
		
					data_master.append(value)
				return ({"message": "List Master Uterus", "Data": data_master})
			else :
				return ({'result':'Failed Check Your Parameter'})
		except Exception as e:
			return {'status': False, 'error': str(e)}

	@http.route('/get_master_ovarium', auth="none", type='json',cors='*')
	def get_master_ovarium(self, **rec):
		try:
			if request.jsonrequest :
				master = request.env['master.temuan.ovarium'].sudo().search([])
				data_master = []
				for m in master:
					value = { 	'id'        				: m.id,
								'kode'						: m.kode or None,
								'nama_temuan_ovarium' 		: m.nama_temuan_ovarium or None,
									   
									  }
		
					data_master.append(value)
				return ({"message": "List Master Ovarium", "Data": data_master})
			else :
				return ({'result':'Failed Check Your Parameter'})
		except Exception as e:
			return {'status': False, 'error': str(e)}

	@http.route('/get_master_cervix', auth="none", type='json',cors='*')
	def get_master_cervix(self, **rec):
		try:
			if request.jsonrequest :
				master = request.env['master.temuan.cervix'].sudo().search([])
				data_master = []
				for m in master:
					value = { 	'id'        				: m.id,
								'kode'						: m.kode or None,
								'nama_temuan_cervix' 		: m.nama_temuan_cervix or None,
									   
									  }
		
					data_master.append(value)
				return ({"message": "List Master Cervix", "Data": data_master})
			else :
				return ({'result':'Failed Check Your Parameter'})
		except Exception as e:
			return {'status': False, 'error': str(e)}	



	@http.route('/select_data_palpasi', auth="none", type='json',cors='*')
	def select_data_palpasi(self, **rec):
		try:
			header = request.httprequest.headers
			db= header.get('db')
			login = header.get('login')
			password = header.get('password')
			uid = request.session.authenticate(db, login, password)
			if uid:
				if request.jsonrequest :
					if rec.get('id_layanan'):
						layanan = request.env['form.pr'].search([('id','=',rec.get('id_layanan'))])
						data_layanan = []
						if layanan :
							value = {   'Anggota/Peternak'    : layanan.peternak_id.peternak_name or None,
										'id_pemilik'          : layanan.id_pemilik or None,
										'wilayah'             : layanan.wilayah_id.wilayah_id or None,
										'petugas'          	  : layanan.petugas_id.nama_petugas or None,
										'jabatan'       	  : layanan.jabatan_id.nama_jabatan or None,
										'tgl_layanan'         : layanan.tgl_layanan or None,
										'periode'       	  : layanan.periode_id.periode_setoran or None,
										'nama_sapi'       	  : layanan.id_sapi.first_name or None,
										'eartag_id'       	  : layanan.eartag_id or None,
										'bcs'       	  	  : layanan.bcs or None,
										'tps'    			  : layanan.tps_id.tps_name or None,
										'catatan_petugas'     : layanan.cat_petugas or None
										   
								}
			
							data_layanan.append(value)

							return ({"message": "Data Layanan", "Data": data_layanan})
						else :
							return ({'result':'Data Layanan tidak ditemukan'})
				else :
					return ({'result':'Failed Check Your Parameter'})
		except Exception as e:
			return {'status': False, 'error': str(e)}

		
