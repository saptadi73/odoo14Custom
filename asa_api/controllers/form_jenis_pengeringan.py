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

	@http.route('/create_form_kering_kandang', auth="none", type='json',cors='*')
	def create_form_kering_kandang(self, **rec):
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
					# 	id_sapi = rec['id_sapi']
					# else :
					# 	id_sapi = False
					if rec.get('jenis_pengeringan_id') :
						jenis_pengeringan_id = rec['jenis_pengeringan_id']
					else :
						jenis_pengeringan_id = False
					if rec.get('pengobatan1') :
						pengobatan1 = rec['pengobatan1']
					else :
						pengobatan1 = False
					if rec.get('pengobatan2') :
						pengobatan2 = rec['pengobatan2']
					else :
						pengobatan2 = False
					if rec.get('bcs') :
						bcs = rec['bcs']
					else :
						bcs = False
					if rec.get('cat_petugas') :
						cat_petugas = rec['cat_petugas']
					else :
						cat_petugas = False

					petugas_id = request.env['medical.physician'].sudo().search([('id','=',rec['petugas_id'])], limit=1)
					# sapi = request.env['sapi'].sudo().search([('id','=',rec['id_sapi'])],limit=1)
					value_data = {  'peternak_id': peternak_id,
									'petugas_id': petugas,
									'tgl_layanan': tgl_layanan,
									'id_sapi': id_sapi,
									'eartag_id': eartag,
									'jenis_pengeringan_id': jenis_pengeringan_id,
									'pengobatan1': pengobatan1,
									'pengobatan2': pengobatan2,
									'bcs': bcs,
									'cat_petugas': cat_petugas
									  }

					new_record = request.env['form.kk'].sudo().create(value_data)
					new_record._onchange_peternak_id()
					new_record._onchange_petugas_id()
					new_record._onchange_tgl_layanan()
					if new_record :
						return ({'result':'Create Form Kering Kandang Success...!!', "ID Layanan": new_record.id})
					else :
						return ({'result':'Create Form Kering Kandang Gagal...!!'})

					
				return ({'result':'Failed Check Your Parameter'})
		except Exception as e:
			return {'status': False, 'error': str(e)}


	@http.route('/get_master_pengeringan', auth="none", type='json',cors='*')
	def get_master_abortus(self, **rec):
		try:
			if request.jsonrequest :
				master = request.env['master.pengeringan'].sudo().search([])
				data_master = []
				for m in master:
					value = { 	'id'        				: m.id,
								'kode'						: m.kode or None,
								'nama_pengeringan' 			: m.nama_pengeringan or None,
									   
									  }
		
					data_master.append(value)
				return ({"message": "List Master Pengeringan", "Data": data_master})
			else :
				return ({'result':'Failed Check Your Parameter'})
		except Exception as e:
			return {'status': False, 'error': str(e)}

	@http.route('/get_master_obat', auth="none", type='json',cors='*')
	def get_master_obat(self, **rec):
		try:
			if request.jsonrequest :
				master = request.env['master.obat'].sudo().search([])
				data_master = []
				for m in master:
					value = { 	'id'        				: m.id,
								'kode'						: m.kode or None,
								'nama_obat' 				: m.nama_obat or None,
									   
									  }
		
					data_master.append(value)
				return ({"message": "List Master Obat", "Data": data_master})
			else :
				return ({'result':'Failed Check Your Parameter'})
		except Exception as e:
			return {'status': False, 'error': str(e)}


	@http.route('/search_obat', auth="none", type='json',cors='*')
	def search_master_obat(self, **rec):
		try:
			if request.jsonrequest :
				if rec.get('name'):
					if rec.get('offset'):
						obat = request.env['master.obat'].sudo().search([('nama_obat','ilike',rec.get('name'))], offset=int(rec.get('offset')))
					else :
						obat = request.env['master.obat'].sudo().search([('nama_obat','ilike',rec.get('name'))])
					if obat :
						data_master = []
						for m in obat:
							value = { 	'id'        				: m.id,
										'kode'						: m.kode or None,
										'nama_obat' 				: m.nama_obat or None,
											   
											  }
				
							data_master.append(value)
						return ({"message": "List Master Obat", "Data": data_master})
					else :
						return ({'result':'Obat tidak ditemukan'})
				else :
					if rec.get('offset') :
						obat = request.env['master.obat'].sudo().search([], limit=20, offset=int(rec.get('offset')))
					else:
						obat = request.env['master.obat'].sudo().search([], limit=20, offset=0)
					if obat :
						data_master = []
						for m in obat:
							value = { 	'id'        				: m.id,
										'kode'						: m.kode or None,
										'nama_obat' 				: m.nama_obat or None,
											   
											  }
				
							data_master.append(value)
						return ({"message": "List Master Obat", "Data": data_master})
					else :
						return ({'result':'Obat tidak ditemukan'})

			else :
				return ({'result':'Failed Check Your Parameter'})
		except Exception as e:
			return {'status': False, 'error': str(e)}


	@http.route('/select_data_kering_kandang', auth="none", type='json',cors='*')
	def select_data_kering_kandang(self, **rec):
		try:
			header = request.httprequest.headers
			db= header.get('db')
			login = header.get('login')
			password = header.get('password')
			uid = request.session.authenticate(db, login, password)
			if uid:
				if request.jsonrequest :
					if rec.get('id_layanan'):
						layanan = request.env['form.kk'].search([('id','=',rec.get('id_layanan'))])
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


		
