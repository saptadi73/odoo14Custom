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

	@http.route('/create_form_sapi_masuk', auth="none", type='json',cors='*')
	def create_form_sapi_masuk(self, **rec):
		try:
			header = request.httprequest.headers
			db= header.get('db')
			login = header.get('login')
			password = header.get('password')
			uid = request.session.authenticate(db, login, password)
			if uid:
				if request.jsonrequest :
					if rec.get('peternak_id') :
						peternak_id = int(rec['peternak_id'])
					else :
						peternak_id = False
					if rec.get('petugas_id') :
						petugas_id = rec['petugas_id']
					else :
						petugas_id = False
					if rec.get('tgl_layanan') :
						tgl_layanan = rec['tgl_layanan']
					else :
						tgl_layanan = False
					if rec.get('eartag_id') :
						eartag_id = rec['eartag_id']
					else :
						eartag = False
					if rec.get('telinga_ki_ka') :
						telinga_ki_ka = rec['telinga_ki_ka']
					else :
						telinga_ki_ka = False
					if rec.get('nama_sapi') :
						nama_sapi = rec['nama_sapi']
					else :
						nama_sapi = False
					if rec.get('tipe_sapi_id') :
						tipe_sapi_id = rec['tipe_sapi_id']
					else :
						tipe_sapi_id = False
					if rec.get('status_sapi') :
						status_sapi = rec['status_sapi']
					else :
						status_sapi = False
					if rec.get('et') :
						et = rec['et']
					else :
						et = False
					if rec.get('kembar') :
						kembar = rec['kembar']
					else :
						kembar = False
					if rec.get('metoda_id') :
						metoda_id = rec['metoda_id']
					else :
						metoda_id = False
					if rec.get('tgl_lahir') :
						tgl_lahir = rec['tgl_lahir']
					else :
						tgl_lahir = False
					if rec.get('eartag_ibu') :
						sapi = request.env['sapi'].sudo().search([('eartag_id','=',rec['eartag_ibu'])])
						id_ibu = sapi.id
						eartag_ibu = rec.get('eartag_ibu')
					else :
						id_sapi = False
						id_ibu = False
					# if rec.get('ibu_id') :
					# 	ibu_id = int(rec['ibu_id'])
					# else :
					# 	ibu_id = False
					# if rec.get('ayah_id') :
					# 	ayah_id = int(rec['ayah_id'])
					# else :
					# 	ayah_id = False
					if rec.get('eartag_ayah') :
						sapi = request.env['sapi'].sudo().search([('eartag_id','=',rec['eartag_ayah'])])
						ayah_id = sapi.id
						eartag_ayah = rec.get('eartag_ayah')
					else :
						ayah_id = False
						eartag_ayah = False
					if rec.get('tgl_ident') :
						tgl_ident = rec['tgl_ident']
					else :
						tgl_ident = False
					if rec.get('breed_id') :
						breed_id = rec['breed_id']
					else :
						breed_id = False
					if rec.get('tie') :
						tie = rec['tie']
					else :
						tie = False
					if rec.get('kode_klhrn_id') :
						kode_klhrn_id = rec['kode_klhrn_id']
					else :
						kode_klhrn_id = False
					if rec.get('stts_prod') :
						stts_prod = rec['stts_prod']
					else :
						stts_prod = False
					# if rec.get('stts_laktasi_id') :
					# 	stts_laktasi_id = rec['stts_laktasi_id']
					# else :
					# 	stts_laktasi_id = False
					if rec.get('lak_ke') :
						lak_ke = rec['lak_ke']
					else :
						lak_ke = False
					if rec.get('cat_petugas') :
						cat_petugas = rec['cat_petugas']
					else :
						cat_petugas = False
					if rec.get('bcs') :
						bcs = rec['bcs']
					else :
						bcs = False
					if rec.get('status_aktif') :
						status_aktif = rec['status_aktif']
					else :
						status_aktif = False
					if rec.get('pejantan_id') :
						pejantan_id = rec['pejantan_id']
					else :
						pejantan_id = False
					if rec.get('sex') :
						sex = rec['sex']
					else :
						sex = False


					value_data = {  'peternak_id': peternak_id,
									'petugas_id': petugas_id,
									'tgl_layanan': tgl_layanan,
									'eartag_id': eartag_id,
									'telinga_ki_ka': telinga_ki_ka,
									'nama_sapi': nama_sapi,
									'tipe_sapi_id': tipe_sapi_id,
									'state': status_sapi,
									'et': et,
									'kembar': kembar,
									'metoda_id': metoda_id,
									'tgl_lahir': tgl_lahir,
									'eartag_ibu': eartag_ibu,
									'ibu_id': id_ibu,
									'eartag_ayah': eartag_ayah,
									'ayah_id': ayah_id,
									'tgl_ident': tgl_ident,
									'breed_id': breed_id,
									'tie': tie,
									'kode_klhrn_id': kode_klhrn_id,
									'stts_reprod_id': stts_prod,
									'lak_ke': lak_ke,
									'bcs': bcs,
									'cat_petugas': cat_petugas,
									'status_aktif': status_aktif,
									'pejantan_id': pejantan_id,
									'sex': sex

									  }

					new_record = request.env['form.masuk'].sudo().create(value_data)
					new_record._onchange_peternak_id()
					new_record._onchange_petugas_id()
					new_record._onchange_tgl_layanan()

					if new_record :
						return ({'result':'Create Form Sapi Masuk Success...!!', "ID Layanan": new_record.id})
					else :
						return ({'result':'Create Form Sapi Masuk Gagal...!!'})


				return ({'result':'Failed Check Your Parameter'})
		except Exception as e:
			return {'status': False, 'error': str(e)}


	@http.route('/get_pejantan', auth="none", type='json',cors='*')
	def get_pejantan(self, **rec):
		try:
			if request.jsonrequest :
				pejantan = request.env['pejantan'].sudo().search([])
				data_pejantan = []
				for m in pejantan:
					value = { 	'id'        		: m.id,
								'kode_pejantan'		: m.kode_pejantan or None,
								'pejantan_name' 	: m.pejantan_id or None,
									   
									  }
		
					data_pejantan.append(value)
				return ({"message": "List Pejantan", "Data": data_pejantan})
			else :
				return ({'result':'Failed Check Your Parameter'})
		except Exception as e:
			return {'status': False, 'error': str(e)}


	@http.route('/get_master_tipe_sapi', auth="none", type='json',cors='*')
	def get_master_tipe_sapi(self, **rec):
		try:
			if request.jsonrequest :
				master = request.env['master.tipe.sapi'].sudo().search([])
				data_master = []
				for m in master:
					value = { 	'id'        				: m.id,
								'kode'						: m.kode or None,
								'nama_tipe_sapi' 	: m.nama_tipe_sapi or None,
									   
									  }
		
					data_master.append(value)
				return ({"message": "List Master Tipe Sapi", "Data": data_master})
			else :
				return ({'result':'Failed Check Your Parameter'})
		except Exception as e:
			return {'status': False, 'error': str(e)}


	@http.route('/get_master_tipe_sapi', auth="none", type='json',cors='*')
	def get_master_tipe_sapi(self, **rec):
		try:
			if request.jsonrequest :
				master = request.env['master.tipe.sapi'].sudo().search([])
				data_master = []
				for m in master:
					value = { 	'id'        				: m.id,
								'kode'						: m.kode or None,
								'nama_tipe_sapi' 	: m.nama_tipe_sapi or None,
									   
									  }
		
					data_master.append(value)
				return ({"message": "List Master Tipe Sapi", "Data": data_master})
			else :
				return ({'result':'Failed Check Your Parameter'})
		except Exception as e:
			return {'status': False, 'error': str(e)}

	@http.route('/get_master_metoda', auth="none", type='json',cors='*')
	def get_master_metoda(self, **rec):
		try:
			if request.jsonrequest :
				master = request.env['master.metoda'].sudo().search([])
				data_master = []
				for m in master:
					value = { 	'id'        				: m.id,
								'kode'						: m.kode or None,
								'nama_metoda' 	: m.nama_metoda or None,
									   
									  }
		
					data_master.append(value)
				return ({"message": "List Master Metoda", "Data": data_master})
			else :
				return ({'result':'Failed Check Your Parameter'})
		except Exception as e:
			return {'status': False, 'error': str(e)}

	@http.route('/get_master_breed', auth="none", type='json',cors='*')
	def get_master_breed(self, **rec):
		try:
			if request.jsonrequest :
				master = request.env['master.breed'].sudo().search([])
				data_master = []
				for m in master:
					value = { 	'id'        				: m.id,
								'kode'						: m.kode or None,
								'nama_breed' 	: m.nama_breed or None,
									   
									  }
		
					data_master.append(value)
				return ({"message": "List Master Breed", "Data": data_master})
			else :
				return ({'result':'Failed Check Your Parameter'})
		except Exception as e:
			return {'status': False, 'error': str(e)}

	@http.route('/get_master_status_laktasi', auth="none", type='json',cors='*')
	def get_master_laktasi(self, **rec):
		try:
			if request.jsonrequest :
				master = request.env['master.status.laktasi'].sudo().search([])
				data_master = []
				for m in master:
					value = { 	'id'        				: m.id,
								'kode'						: m.kode or None,
								'nama_status_laktasi' 	: m.nama_status_laktasi or None,
									   
									  }
		
					data_master.append(value)
				return ({"message": "List Master Status Laktasi", "Data": data_master})
			else :
				return ({'result':'Failed Check Your Parameter'})
		except Exception as e:
			return {'status': False, 'error': str(e)}

	@http.route('/get_master_kode_kelahiran', auth="none", type='json',cors='*')
	def get_master_kode_kelahiran(self, **rec):
		try:
			if request.jsonrequest :
				master = request.env['master.kode.kelahiran'].sudo().search([])
				data_master = []
				for m in master:
					value = { 	'id'        				: m.id,
								'kode'						: m.kode or None,
								'nama_status_laktasi' 		: m.nama_kode_kelahiran or None,
									   
									  }
		
					data_master.append(value)
				return ({"message": "List Master Kode Kelahiran", "Data": data_master})
			else :
				return ({'result':'Failed Check Your Parameter'})
		except Exception as e:
			return {'status': False, 'error': str(e)}


	@http.route('/select_data_sapi_masuk', auth="none", type='json',cors='*')
	def select_data_sapi_masuk(self, **rec):
		try:
			header = request.httprequest.headers
			db= header.get('db')
			login = header.get('login')
			password = header.get('password')
			uid = request.session.authenticate(db, login, password)
			if uid:
				if request.jsonrequest :
					if rec.get('id_layanan'):
						layanan = request.env['form.masuk'].search([('id','=',rec.get('id_layanan'))])
						data_layanan = []
						if layanan :
							value = {   'Anggota/Peternak'    : layanan.peternak_id.peternak_name or None,
										'id_pemilik'          : layanan.id_pemilik or None,
										'wilayah'             : layanan.wilayah_id.wilayah_id or None,
										'petugas'          	  : layanan.petugas_id.nama_petugas or None,
										'jabatan'       	  : layanan.jabatan_id.nama_jabatan or None,
										'tgl_layanan'         : layanan.tgl_layanan or None,
										'periode'       	  : layanan.periode_id.periode_setoran or None,
										'nama_sapi'       	  : layanan.nama_sapi or None,
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

		
