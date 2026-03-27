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

	@http.route('/create_form_ib', auth="none", type='json',cors='*')
	def create_form_ib(self, **rec):
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
						eartag = rec.get('eartag_id')
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
					if rec.get('bcs') :
						bcs = rec['bcs']
					else :
						bcs = False
					if rec.get('id_status_reproduksi') :
						id_status_reproduksi = rec['id_status_reproduksi']
					else :
						id_status_reproduksi = False
					if rec.get('id_pejantan') :
						id_pejantan = int(rec['id_pejantan'])
					else :
						id_pejantan = False
					if rec.get('no_pejantan') :
						no_pejantan = rec['no_pejantan']
					else :
						no_pejantan = False
					if rec.get('no_batch') :
						no_batch = rec['no_batch']
					else :
						no_batch = False
					if rec.get('lama_birahi') :
						lama_birahi = rec['lama_birahi']
					else :
						lama_birahi = False
					if rec.get('ib_ke') :
						ib_ke = rec['ib_ke']
					else :
						ib_ke = False
					if rec.get('pengamat_birahi') :
						nama_pengamat_birahi = rec['pengamat_birahi']
					else :
						nama_pengamat_birahi = False
					if rec.get('dose') :
						dose = rec['dose']
					else :
						dose = False
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
									'eartag_id': eartag,
									'tgl_layanan': tgl_layanan,
									'bcs': bcs,
									'id_status_reproduksi': id_status_reproduksi,
									'id_pejantan': id_pejantan,
									'no_pejantan': no_pejantan,
									'no_batch': no_batch,
									'lama_birahi': lama_birahi,
									'ib_ke': ib_ke,
									'nama_pengamat_birahi': nama_pengamat_birahi,
									'dose': dose,
									'cat_petugas': cat_petugas,
									'bcs': bcs

									  }
					print ("========value===========", value_data)

					new_record = request.env['form.ib'].sudo().create(value_data)
					new_record._onchange_peternak_id()
					new_record._onchange_petugas_id()
					new_record._onchange_tgl_layanan()

					if new_record :
						return ({'result':'Create Form IB Success...!!', "ID Layanan": new_record.id})
					else :
						return ({'result':'Create Form IB Gagal...!!'})


				return ({'result':'Failed Check Your Parameter'})
		except Exception as e:
			return {'status': False, 'error': str(e)}


	@http.route('/get_master_reproduksi', auth="none", type='json',cors='*')
	def get_master_reproduksi(self, **rec):
		try:
			if request.jsonrequest :
				master = request.env['master.status.reproduksi'].sudo().search([])
				data_master = []
				for m in master:
					value = { 	'id'        				: m.id,
								'kode'						: m.kode or None,
								'nama_status_reproduksi' 	: m.nama_status_reproduksi or None,
									   
									  }
		
					data_master.append(value)
				return ({"message": "List Master Reproduksi", "Data": data_master})
			else :
				return ({'result':'Failed Check Your Parameter'})
		except Exception as e:
			return {'status': False, 'error': str(e)}

	@http.route('/get_master_semen_beku', auth="none", type='json',cors='*')
	def get_master_semen_beku(self, **rec):
		try:
			if request.jsonrequest :
				master = request.env['master.semen.beku'].sudo().search([])
				data_master = []
				for m in master:
					value = { 	'id'        				: m.id,
								'kode'						: m.kode or None,
								'nama_semen_beku' 			: m.nama_semen_beku or None,
									   
									  }
		
					data_master.append(value)
				return ({"message": "List Master Semen Beku", "Data": data_master})
			else :
				return ({'result':'Failed Check Your Parameter'})
		except Exception as e:
			return {'status': False, 'error': str(e)}



	@http.route('/select_data_ib', auth="none", type='json',cors='*')
	def select_data_ib(self, **rec):
		try:
			header = request.httprequest.headers
			db= header.get('db')
			login = header.get('login')
			password = header.get('password')
			uid = request.session.authenticate(db, login, password)
			if uid:
				if request.jsonrequest :
					if rec.get('id_layanan'):
						layanan = request.env['form.ib'].search([('id','=',rec.get('id_layanan'))])
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

		
