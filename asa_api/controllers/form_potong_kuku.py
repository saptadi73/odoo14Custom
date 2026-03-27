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

	@http.route('/create_form_potong_kuku', auth="none", type='json',cors='*')
	def create_form_potong_kuku(self, **rec):
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
						petugas = rec['petugas_id']
					else :
						petugas = False
					if rec.get('tgl_layanan') :
						tgl_layanan = rec['tgl_layanan']
					else :
						tgl_layanan = False
					if rec.get('layanan_id') :
						layanan = rec['layanan_id']
					else :
						layanan = False
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
					if rec.get('alasan_id') :
						alasan = rec['alasan_id']
					else :
						alasan = False
					if rec.get('depan_kiri') :
						depan_kiri = rec['depan_kiri']
					else :
						depan_kiri = False
					if rec.get('depan_kanan') :
						depan_kanan = rec['depan_kanan']
					else :
						depan_kanan = False
					if rec.get('blkg_kiri') :
						blkg_kiri = rec['blkg_kiri']
					else :
						blkg_kiri = False
					if rec.get('blkg_kanan') :
						blkg_kanan = rec['blkg_kanan']
					else :
						blkg_kanan = False
					if rec.get('pengobatan_lain_1') :
						pengobatan_lain_1 = rec['pengobatan_lain_1']
					else :
						pengobatan_lain_1 = False
					if rec.get('pengobatan_lain_2') :
						pengobatan_lain_2 = rec['pengobatan_lain_2']
					else :
						pengobatan_lain_2 = False
					if rec.get('cat_petugas') :
						cat_petugas = rec['cat_petugas']
					else :
						cat_petugas = False
					if rec.get('bcs') :
						bcs = rec['bcs']
					else :
						bcs = False

					petugas_id = request.env['medical.physician'].sudo().search([('id','=',rec['petugas_id'])], limit=1)
					# sapi = request.env['sapi'].sudo().search([('eartag_id','=',rec['eartag_id'])])
					value_data = {  'peternak_id': peternak_id,
									'petugas_id': petugas,
									'tgl_layanan': tgl_layanan,
									'layanan_id': layanan,
									'id_sapi': id_sapi,
									'eartag_id': eartag,
									'alsn_ptg_kku_id': alasan,
									'dpn_kiri': depan_kiri,
									'dpn_kanan': depan_kanan,
									'blkg_kiri': blkg_kiri,
									'blkg_kanan': blkg_kanan,
									'pngbtn_lain_1_id': pengobatan_lain_1,
									'pngbtn_lain_2_id': pengobatan_lain_2,
									'cat_petugas': cat_petugas,
									'bcs': bcs
									  }

					new_record = request.env['form.pot.kuku'].sudo().create(value_data)
					new_record._onchange_peternak_id()
					new_record._onchange_petugas_id()
					new_record._onchange_tgl_layanan()

					if new_record :
						return ({'result':'Create Form Potong Kuku Success...!!', "ID Layanan": new_record.id})
					else :
						return ({'result':'Create Form Potong Kuku Gagal...!!'})

					
				return ({'result':'Failed Check Your Parameter'})
		except Exception as e:
			return {'status': False, 'error': str(e)}


	@http.route('/get_master_layanan', auth="none", type='json',cors='*')
	def get_master_layanan(self, **rec):
		try:
			if request.jsonrequest :
				master = request.env['jenis.pelayanan'].sudo().search([])
				data_master = []
				for m in master:
					value = { 	'id'        			: m.id,
								'code_pelayanan'		: m.code_pelayanan or None,
								'pelayanan_id' 			: m.pelayanan_id or None,
									   
									  }
		
					data_master.append(value)
				return ({"message": "List Master Jenis Pelayanan", "Data": data_master})
			else :
				return ({'result':'Failed Check Your Parameter'})
		except Exception as e:
			return {'status': False, 'error': str(e)}


	@http.route('/get_master_alasan_potkuku', auth="none", type='json',cors='*')
	def get_master_alasan_potkuku(self, **rec):
		try:
			if request.jsonrequest :
				master = request.env['master.alasan.potkuku'].sudo().search([])
				data_master = []
				for m in master:
					value = { 	'id'        			: m.id,
								'kode'					: m.kode or None,
								'nama_alasan_potkuku' 	: m.nama_alasan_potkuku or None,
									   
									  }
		
					data_master.append(value)
				return ({"message": "List Master Alasan Potong Kuku", "Data": data_master})
			else :
				return ({'result':'Failed Check Your Parameter'})
		except Exception as e:
			return {'status': False, 'error': str(e)}

	@http.route('/get_master_metoda_pengobatan', auth="none", type='json',cors='*')
	def get_master_metoda_pengobatan(self, **rec):
		try:
			if request.jsonrequest :
				master = request.env['master.metoda.pengobatan'].sudo().search([])
				data_master = []
				for m in master:
					value = { 	'id'        			: m.id,
								'kode'					: m.kode or None,
								'nama_metoda_pengobatan' 	: m.nama_metoda_pengobatan or None,
									   
									  }
		
					data_master.append(value)
				return ({"message": "List Master Metoda Pengobatan", "Data": data_master})
			else :
				return ({'result':'Failed Check Your Parameter'})
		except Exception as e:
			return {'status': False, 'error': str(e)}


	@http.route('/select_data_pot_kuku', auth="none", type='json',cors='*')
	def select_data_pot_kuku(self, **rec):
		try:
			header = request.httprequest.headers
			db= header.get('db')
			login = header.get('login')
			password = header.get('password')
			uid = request.session.authenticate(db, login, password)
			if uid:
				if request.jsonrequest :
					if rec.get('id_layanan'):
						layanan = request.env['form.pot.kuku'].search([('id','=',rec.get('id_layanan'))])
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


		
