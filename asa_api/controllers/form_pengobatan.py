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

	@http.route('/create_form_pengobatan', auth="none", type='json',cors='*')
	def create_form_pengobatan(self, **rec):
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
					if rec.get('eartag_id') :
						sapi = request.env['sapi'].sudo().search([('eartag_id','=',rec['eartag_id'])])
						id_sapi = sapi.id
					else :
						id_sapi = False
						eartag = False
					# if rec.get('id_sapi') :
					# 	id_sapi = int(rec['id_sapi'])
					# 	sapi = request.env['sapi'].sudo().search([('id','=',id_sapi)])
					# 	eartag = sapi.eartag_id
					# else :
					# 	id_sapi = False
					# 	eartag = False
					if rec.get('tgl_layanan') :
						tgl_layanan = rec['tgl_layanan']
					else :
						tgl_layanan = False
					if rec.get('id_kasus_penyakit') :
						id_kasus_penyakit = rec['id_kasus_penyakit']
					else :
						id_kasus_penyakit = False
					if rec.get('status_kesehatan_id') :
						status_kesehatan_id = rec['status_kesehatan_id']
					else :
						status_kesehatan_id = False
					if rec.get('metoda_pengobatan_id1') :
						metoda_pengobatan_id1 = rec['metoda_pengobatan_id1']
					else :
						metoda_pengobatan_id1 = False
					if rec.get('obat1') :
						obat1 = rec['obat1']
					else :
						obat1 = False
					if rec.get('dose1') :
						dose1 = rec['dose1']
					else :
						dose1 = False
					if rec.get('metoda_pengobatan_id2') :
						metoda_pengobatan_id2 = rec['metoda_pengobatan_id2']
					else :
						metoda_pengobatan_id2 = False
					if rec.get('obat2') :
						obat2 = rec['obat2']
					else :
						obat2 = False
					if rec.get('dose2') :
						dose2 = rec['dose2']
					else :
						dose2 = False
					if rec.get('metoda_pengobatan_id3') :
						metoda_pengobatan_id3 = rec['metoda_pengobatan_id3']
					else :
						metoda_pengobatan_id3 = False
					if rec.get('obat3') :
						obat3 = rec['obat3']
					else :
						obat3 = False
					if rec.get('dose3') :
						dose3 = rec['dose3']
					else :
						dose3 = False
					if rec.get('metoda_pengobatan_id4') :
						metoda_pengobatan_id4 = rec['metoda_pengobatan_id4']
					else :
						metoda_pengobatan_id4 = False
					if rec.get('obat4') :
						obat4 = rec['obat4']
					else :
						obat4 = False
					if rec.get('dose4') :
						dose4 = rec['dose4']
					else :
						dose4 = False
					if rec.get('metoda_pengobatan_id5') :
						metoda_pengobatan_id5 = rec['metoda_pengobatan_id5']
					else :
						metoda_pengobatan_id5 = False
					if rec.get('obat5') :
						obat5 = rec['obat5']
					else :
						obat5 = False
					if rec.get('dose5') :
						dose5 = rec['dose5']
					else :
						dose5 = False
					if rec.get('cat_petugas') :
						cat_petugas = rec['cat_petugas']
					else :
						cat_petugas = False
					if rec.get('bcs') :
						bcs = rec['bcs']
					else :
						bcs = False

					value_data = {  'peternak_id': peternak_id,
									'petugas_id': petugas_id,
									'id_sapi': id_sapi,
									'eartag_id': rec['eartag_id'],
									'tgl_layanan': tgl_layanan,
									'id_kasus_penyakit': id_kasus_penyakit,
									'status_kesehatan_id': status_kesehatan_id,
									'metoda_pengobatan_id': metoda_pengobatan_id1,
									'metoda_pengobatan_id2': metoda_pengobatan_id2,
									'metoda_pengobatan_id3': metoda_pengobatan_id3,
									'metoda_pengobatan_id4': metoda_pengobatan_id4,
									'metoda_pengobatan_id5': metoda_pengobatan_id5,
									'obat1': obat1,
									'dose1': dose1,
									'obat2': obat2,
									'dose2': dose2,
									'obat3': obat3,
									'dose3': dose3,
									'obat4': obat4,
									'dose4': dose4,
									'obat5': obat5,
									'dose5': dose5,
									'cat_petugas': cat_petugas,
									'bcs': bcs

									  }

					new_record = request.env['form.pengobatan'].sudo().create(value_data)
					new_record._onchange_peternak_id()
					new_record._onchange_petugas_id()
					new_record._onchange_tgl_layanan()


					if new_record :
						return ({'result':'Create Form Pengobatan Success...!!', "ID Layanan": new_record.id})
					else :
						return ({'result':'Create Form Pengobatan Gagal...!!'})


				return ({'result':'Failed Check Your Parameter'})
		except Exception as e:
			return {'status': False, 'error': str(e)}



	@http.route('/get_master_kasus_penyakit', auth="none", type='json',cors='*')
	def get_master_penyakit(self, **rec):
		try:
			if request.jsonrequest :
				master = request.env['master.kasus.penyakit'].sudo().search([])
				data_master = []
				for m in master:
					value = { 	'id'        			: m.id,
								'kode'					: m.kode or None,
								'nama_kasus_penyakit' 	: m.nama_kasus_penyakit or None,
									   
									  }
		
					data_master.append(value)
				return ({"message": "List Master Kasus Penyakit", "Data": data_master})
			else :
				return ({'result':'Failed Check Your Parameter'})
		except Exception as e:
			return {'status': False, 'error': str(e)}


	@http.route('/get_master_status_kesehatan', auth="none", type='json',cors='*')
	def get_master_status_kesehatan(self, **rec):
		try:
			if request.jsonrequest :
				master = request.env['master.status.kesehatan'].sudo().search([])
				data_master = []
				for m in master:
					value = { 	'id'        				: m.id,
								'kode'						: m.kode or None,
								'nama_status_kesehatan' 	: m.nama_status_kesehatan or None,
									   
									  }
		
					data_master.append(value)
				return ({"message": "List Master Status Kesehatan", "Data": data_master})
			else :
				return ({'result':'Failed Check Your Parameter'})
		except Exception as e:
			return {'status': False, 'error': str(e)}


	@http.route('/select_data_pengobatan', auth="none", type='json',cors='*')
	def select_data_pengobatan(self, **rec):
		try:
			header = request.httprequest.headers
			db= header.get('db')
			login = header.get('login')
			password = header.get('password')
			uid = request.session.authenticate(db, login, password)
			if uid:
				if request.jsonrequest :
					if rec.get('id_layanan'):
						layanan = request.env['form.pengobatan'].search([('id','=',rec.get('id_layanan'))])
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


		
