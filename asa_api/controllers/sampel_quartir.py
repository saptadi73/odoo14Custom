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

	@http.route('/create_form_sampel_quartir', auth="none", type='json',cors='*')
	def create_form_sampel_quartir(self, **rec):
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
					if rec.get('cat_petugas') :
						cat_petugas = rec['cat_petugas']
					else :
						cat_petugas = False
					if rec.get('met_pengh_jss') :
						met_pengh_jss = rec['met_pengh_jss']
					else :
						met_pengh_jss = False
					if rec.get('knn_dpn_jss') :
						knn_dpn_jss = rec['knn_dpn_jss']
					else :
						knn_dpn_jss = False
					if rec.get('knn_dpn_kuman') :
						knn_dpn_kuman = rec['knn_dpn_kuman']
					else :
						knn_dpn_kuman = False
					if rec.get('knn_blkg_jss') :
						knn_blkg_jss = rec['knn_blkg_jss']
					else :
						knn_blkg_jss = False
					if rec.get('knn_blkg_kuman') :
						knn_blkg_kuman = rec['knn_blkg_kuman']
					else :
						knn_blkg_kuman = False
					if rec.get('kiri_dpn_jss') :
						kiri_dpn_jss = rec['kiri_dpn_jss']
					else :
						kiri_dpn_jss = False
					if rec.get('kiri_dpn_kuman') :
						kiri_dpn_kuman = rec['kiri_dpn_kuman']
					else :
						kiri_dpn_kuman = False
					if rec.get('kiri_blkg_jss') :
						kiri_blkg_jss = rec['kiri_blkg_jss']
					else :
						kiri_blkg_jss = False
					if rec.get('kiri_blkg_kuman') :
						kiri_blkg_kuman = rec['kiri_blkg_kuman']
					else :
						kiri_blkg_kuman = False
					if rec.get('biaya') :
						biaya = rec['biaya']
					else :
						biaya = False
					if rec.get('bcs') :
						bcs = rec['bcs']
					else :
						bcs = False

					petugas_id = request.env['medical.physician'].sudo().search([('id','=',rec['petugas_id'])], limit=1)
					# sapi = request.env['sapi'].sudo().search([('id','=',rec['id_sapi'])],limit=1)
					value_data = {  'peternak_id': peternak_id,
									'petugas_id': petugas,
									'tgl_layanan': tgl_layanan,
									'id_sapi': id_sapi,
									'eartag_id': eartag,
									'cat_petugas': cat_petugas,
									'met_pengh_jss_id': met_pengh_jss,
									'knn_dpn_jss': knn_dpn_jss,
									'kanan_dpn_kuman_id': knn_dpn_kuman,
									'knn_blkg_jss': knn_blkg_jss,
									'knn_blkg_kuman_id': knn_blkg_kuman,
									'kiri_dpn_jss': kiri_dpn_jss,
									'kiri_dpn_kuman_id': kiri_dpn_kuman,
									'kiri_blkg_jss': kiri_blkg_jss,
									'kiri_blkg_kuman_id': kiri_blkg_kuman,
									'biaya': biaya,
									'bcs': bcs
									  }

					new_record = request.env['form.sq'].sudo().create(value_data)
					new_record._onchange_peternak_id()
					new_record._onchange_petugas_id()
					new_record._onchange_tgl_layanan()
					if new_record :
						return ({'result':'Create Form Sampel Quartir Success...!!', "ID Layanan": new_record.id})
					else :
						return ({'result':'Create Form Sampel Quartir Gagal...!!'})

					
				return ({'result':'Failed Check Your Parameter'})
		except Exception as e:
			return {'status': False, 'error': str(e)}


	@http.route('/get_master_perhitungan_jss', auth="none", type='json',cors='*')
	def get_master_metoda_perhitungan_jss(self, **rec):
		try:
			if request.jsonrequest :
				master = request.env['master.metode.perhitungan.jss'].sudo().search([])
				data_master = []
				for m in master:
					value = { 	'id'        			: m.id,
								'kode'					: m.kode or None,
								'nama_metode_perhitungan_jss' 	: m.nama_metode_perhitungan_jss or None,
									   
									  }
		
					data_master.append(value)
				return ({"message": "List Master Metoda Perhitungan JSS", "Data": data_master})
			else :
				return ({'result':'Failed Check Your Parameter'})
		except Exception as e:
			return {'status': False, 'error': str(e)}


	@http.route('/get_master_kuman_kuartir', auth="none", type='json',cors='*')
	def get_master_metoda_pengobatan(self, **rec):
		try:
			if request.jsonrequest :
				master = request.env['master.kuman.sampel.kuartir'].sudo().search([])
				data_master = []
				for m in master:
					value = { 	'id'        			: m.id,
								'kode'					: m.kode or None,
								'nama_kuman_sampel_kuartir' 	: m.nama_kuman_sampel_kuartir or None,
									   
									  }
		
					data_master.append(value)
				return ({"message": "List Master Kuman Kuartir", "Data": data_master})
			else :
				return ({'result':'Failed Check Your Parameter'})
		except Exception as e:
			return {'status': False, 'error': str(e)}



	@http.route('/select_data_sampel', auth="none", type='json',cors='*')
	def select_data_sampel(self, **rec):
		try:
			header = request.httprequest.headers
			db= header.get('db')
			login = header.get('login')
			password = header.get('password')
			uid = request.session.authenticate(db, login, password)
			if uid:
				if request.jsonrequest :
					if rec.get('id_layanan'):
						layanan = request.env['form.sq'].search([('id','=',rec.get('id_layanan'))])
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


		
