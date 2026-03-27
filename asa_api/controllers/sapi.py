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

	@http.route('/change_id_eartag', auth="none", type='json',cors='*')
	def change_password(self, **rec):
		try:
			header = request.httprequest.headers
			db= header.get('db')
			login = header.get('login')
			password = header.get('password')
			uid = request.session.authenticate(db, login, password)
			if uid:
				if request.jsonrequest :
					if rec.get('peternak_id') :
						peternak = rec['peternak_id']
					else :
						peternak = False
					if rec.get('petugas_id') :
						petugas = rec['petugas_id']
					else :
						petugas = False
					# if rec.get('id_sapi') :
					# 	sapi = rec['id_sapi']
					# else :
					# 	sapi = False
					# if rec.get('eartag_id_lama') :
					# 	eartag_lama = rec['eartag_id_lama']
					# else :
					# 	eartag_lama = False
					if rec.get('eartag_id_lama') :
						sapi = request.env['sapi'].sudo().search([('eartag_id','=',rec['eartag_id_lama'])])
						id_sapi = sapi.id
						eartag = rec.get('eartag_id_lama')
					else :
						id_sapi = False
						eartag = False
					if rec.get('eartag_id_baru') :
						eartag_baru = rec['eartag_id_baru']
					else :
						eartag_baru = False
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

					value_data = {  'peternak_id': peternak,
									'petugas_id': petugas,
									'id_sapi': id_sapi,
									'eartag_id': eartag,
									'eartag_id_baru': eartag_baru,
									'tgl_layanan': tgl_layanan,
									'bcs': bcs,
									'cat_petugas': cat_petugas
									  }

					new_record = request.env['form.gis'].sudo().create(value_data)
					new_record._onchange_peternak_id()
					new_record._onchange_petugas_id()
					new_record._onchange_tgl_layanan()

					if rec.get('eartag_id_lama') and rec.get('eartag_id_baru') :
						sapi = request.env['sapi'].sudo().search([('eartag_id','=',rec['eartag_id_lama'])])
						if sapi :
							sapi.sudo().write({'eartag_id': rec['eartag_id_baru']})
							return ({'result':'Success Create History Ganti ID Sapi and Update ID Eartag', "ID Layanan": new_record.id})
						else :
							return ({'result':'Data Sapi Tidak Ditemukan'})
					return ({'result':'ID Peternak Or New ID Ear Tag is Empty'})
				return ({'result':'Failed Check Your Parameter'})
		except Exception as e:
			return {'status': False, 'error': str(e)}



	@http.route('/select_data_gis', auth="none", type='json',cors='*')
	def select_data_gis(self, **rec):
		try:
			header = request.httprequest.headers
			db= header.get('db')
			login = header.get('login')
			password = header.get('password')
			uid = request.session.authenticate(db, login, password)
			if uid:
				if request.jsonrequest :
					if rec.get('id_layanan'):
						layanan = request.env['form.gis'].search([('id','=',rec.get('id_layanan'))])
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

		
