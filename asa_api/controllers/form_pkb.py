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

	@http.route('/create_form_pkb', auth="none", type='json',cors='*')
	def create_form_pkb(self, **rec):
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
					if rec.get('tgl_layanan') :
						tgl_layanan = rec['tgl_layanan']
					else :
						tgl_layanan = False
					if rec.get('cat_petugas') :
						cat_petugas = rec['cat_petugas']
					else :
						cat_petugas = False
					if rec.get('bcs') :
						bcs = rec['bcs']
					else :
						bcs = False
					if rec.get('id_tanda_kebuntingan') :
						id_tanda_kebuntingan = rec['id_tanda_kebuntingan']
					else :
						id_tanda_kebuntingan = False
					if rec.get('id_posisi') :
						id_posisi = rec['id_posisi']
					else :
						id_posisi = False
					if rec.get('tgl_ib_akhir') :
						tgl_ib_akhir = rec['tgl_ib_akhir']
					else :
						tgl_ib_akhir = False
					if rec.get('umur_kebuntingan') :
						umur_kebuntingan = rec['umur_kebuntingan']
					else :
						umur_kebuntingan = False

					value_data = {  'peternak_id': peternak_id,
									'petugas_id': petugas_id,
									'id_sapi': id_sapi,
									'eartag_id': rec['eartag_id'],
									'tgl_layanan': tgl_layanan,
									'bcs': bcs,
									'id_tanda_kebuntingan': id_tanda_kebuntingan,
									'id_posisi': id_posisi,
									'tgl_ib_akhir': tgl_ib_akhir,
									'umur_kebuntingan': umur_kebuntingan,
									'cat_petugas': cat_petugas,

									  }

					new_record = request.env['form.pkb'].sudo().create(value_data)
					new_record._onchange_peternak_id()
					new_record._onchange_petugas_id()
					new_record._onchange_tgl_layanan()

					if new_record :
						return ({'result':'Create Form PKB Success...!!',"ID Layanan": new_record.id})
					else :
						return ({'result':'Create Form PKB Gagal...!!'})


				return ({'result':'Failed Check Your Parameter'})
		except Exception as e:
			return {'status': False, 'error': str(e)}


	@http.route('/get_master_kebuntingan', auth="none", type='json',cors='*')
	def get_master_bunting(self, **rec):
		try:
			if request.jsonrequest :
				master = request.env['master.tanda.kebuntingan'].sudo().search([])
				data_master = []
				for m in master:
					value = { 	'id'        				: m.id,
								'kode'						: m.kode or None,
								'nama_tanda_kebuntingan' 	: m.nama_tanda_kebuntingan or None,
									   
									  }
		
					data_master.append(value)
				return ({"message": "List Master Kebuntingan", "Data": data_master})
			else :
				return ({'result':'Failed Check Your Parameter'})
		except Exception as e:
			return {'status': False, 'error': str(e)}


	@http.route('/get_master_posisi', auth="none", type='json',cors='*')
	def get_master_posisi(self, **rec):
		try:
			if request.jsonrequest :
				master = request.env['master.posisi'].sudo().search([])
				data_master = []
				for m in master:
					value = { 	'id'        				: m.id,
								'kode'						: m.kode or None,
								'nama_posisi' 				: m.nama_posisi or None,
									   
									  }
		
					data_master.append(value)
				return ({"message": "List Master Posisi", "Data": data_master})
			else :
				return ({'result':'Failed Check Your Parameter'})
		except Exception as e:
			return {'status': False, 'error': str(e)}

	@http.route('/select_data_pkb', auth="none", type='json',cors='*')
	def select_data_pkb(self, **rec):
		try:
			header = request.httprequest.headers
			db= header.get('db')
			login = header.get('login')
			password = header.get('password')
			uid = request.session.authenticate(db, login, password)
			if uid:
				if request.jsonrequest :
					if rec.get('id_layanan'):
						layanan = request.env['form.pkb'].search([('id','=',rec.get('id_layanan'))])
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
										'tanda_kebuntingan'   : layanan.id_tanda_kebuntingan.nama_tanda_kebuntingan or None,
										'posisi'       	  	  : layanan.id_posisi.nama_posisi or None,
										'tgl_ib_terakhir'     : layanan.tgl_ib_akhir or None,
										'umur_kebuntingan'    : layanan.umur_kebuntingan or None,
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

		
