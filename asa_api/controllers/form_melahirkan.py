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

	@http.route('/create_form_melahirkan', auth="none", type='json',cors='*')
	def create_form_melahirkan(self, **rec):
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
					if rec.get('kode_eartag_induk') :
						sapi = request.env['sapi'].sudo().search([('eartag_id','=',rec['kode_eartag_induk'])])
						ibu_id = sapi.id
					else :
						ibu_id = False
					if rec.get('pejantan_id') :
						pejantan_id = rec['pejantan_id']
					else :
						pejantan_id = False
					if rec.get('tgl_lahir') :
						tgl_lahir = rec['tgl_lahir']
					else :
						tgl_lahir = False
					if rec.get('status_lahir') :
						status_lahir = rec['status_lahir']
					else :
						status_lahir = False
					if rec.get('status_pelihara') :
						status_pelihara = rec['status_pelihara']
					else :
						status_pelihara = False
					if rec.get('jenis_kelamin') :
						jenis_kelamin = rec['jenis_kelamin']
					else :
						jenis_kelamin = False
					if rec.get('berat_lahir') :
						berat_lahir = rec['berat_lahir']
					else :
						berat_lahir = False
					if rec.get('kondisi_lahir') :
						kondisi_lahir = rec['kondisi_lahir']
					else :
						kondisi_lahir = False
					if rec.get('jumlah_lahir') :
						jumlah_lahir = rec['jumlah_lahir']
					else :
						jumlah_lahir = False
					if rec.get('jumlah_pelihara') :
						jumlah_pelihara = rec['jumlah_pelihara']
					else :
						jumlah_pelihara = False
					if rec.get('jumlah_mati') :
						jumlah_mati = rec['jumlah_mati']
					else :
						jumlah_mati = False
					if rec.get('jumlah_dijual') :
						jumlah_dijual = rec['jumlah_dijual']
					else :
						jumlah_dijual = False
					if rec.get('harga_jual') :
						harga_jual = rec['harga_jual']
					else :
						harga_jual = False
					if rec.get('keadaan_saat_melahirkan_id') :
						keadaan_saat_melahirkan_id = rec['keadaan_saat_melahirkan_id']
					else :
						keadaan_saat_melahirkan_id = False
					if rec.get('cat_petugas') :
						cat_petugas = rec['cat_petugas']
					else :
						cat_petugas = False
					if rec.get('bcs') :
						bcs = rec['bcs']
					else :
						bcs = False
					if rec.get('sex') :
						sex = rec['sex']
					else :
						sex = False

					value_data = {  'peternak_id': peternak_id,
									'petugas_id': petugas_id,
									'ibu_id': ibu_id,
									'pejantan_id': pejantan_id,
									'tgl_lahir': tgl_lahir,
									'status_lahir': status_lahir,
									'status_pelihara': status_pelihara,
									'jenis_kelamin': jenis_kelamin,
									'berat_lahir': berat_lahir,
									'kondisi_lahir': kondisi_lahir,
									'jumlah_lahir': jumlah_lahir,
									'jumlah_pelihara': jumlah_pelihara,
									'jumlah_mati': jumlah_mati,
									'jumlah_dijual': jumlah_dijual,
									'harga_jual': harga_jual,
									'keadaan_saat_melahirkan_id': keadaan_saat_melahirkan_id,
									'cat_petugas': cat_petugas,
									'tgl_layanan': tgl_layanan,
									'bcs': bcs,
									'jenis_kelamin': sex

									  }

					new_record = request.env['form.melahirkan'].sudo().create(value_data)
					new_record._onchange_peternak_id()
					new_record._onchange_petugas_id()
					new_record._onchange_tgl_layanan()

					if new_record :
						return ({'result':'Create Form Melahirkan Success...!!',"ID Layanan": new_record.id})
					else :
						return ({'result':'Create Form Melahirkan Gagal...!!'})


				return ({'result':'Failed Check Your Parameter'})
		except Exception as e:
			return {'status': False, 'error': str(e)}


	@http.route('/get_master_keadaan_melahirkan', auth="none", type='json',cors='*')
	def get_master_keadaan_melahirkan(self, **rec):
		try:
			if request.jsonrequest :
				master = request.env['master.keadaan.melahirkan'].sudo().search([])
				data_master = []
				for m in master:
					value = { 	'id'        				: m.id,
								'kode'						: m.kode or None,
								'nama_keadaan_melahirkan' 	: m.nama_keadaan_melahirkan or None,
									   
									  }
		
					data_master.append(value)
				return ({"message": "List Master Keadaan Melahirkan", "Data": data_master})
			else :
				return ({'result':'Failed Check Your Parameter'})
		except Exception as e:
			return {'status': False, 'error': str(e)}


	@http.route('/select_data_melahirkan', auth="none", type='json',cors='*')
	def select_data_melahirkan(self, **rec):
		try:
			header = request.httprequest.headers
			db= header.get('db')
			login = header.get('login')
			password = header.get('password')
			uid = request.session.authenticate(db, login, password)
			if uid:
				if request.jsonrequest :
					if rec.get('id_layanan'):
						layanan = request.env['form.melahirkan'].search([('id','=',rec.get('id_layanan'))])
						data_layanan = []
						if layanan :
							value = {   'Anggota/Peternak'    : layanan.peternak_id.peternak_name or None,
										'id_pemilik'          : layanan.id_pemilik or None,
										'wilayah'             : layanan.wilayah_id.wilayah_id or None,
										'petugas'          	  : layanan.petugas_id.nama_petugas or None,
										'jabatan'       	  : layanan.jabatan_id.nama_jabatan or None,
										'tgl_layanan'         : layanan.tgl_layanan or None,
										'periode'       	  : layanan.periode_id.periode_setoran or None,
										'nama_sapi'       	  : layanan.ayah_id.first_name or None,
										'eartag_id'       	  : layanan.eartag_ayah or None,
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

		
