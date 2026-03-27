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

	@http.route('/ganti_pemilik', auth="none", type='json',cors='*')
	def change_password(self, **rec):
		try:
			header = request.httprequest.headers
			db= header.get('db')
			login = header.get('login')
			password = header.get('password')
			uid = request.session.authenticate(db, login, password)
			if uid:
				if request.jsonrequest :
					if rec.get('tgl_layanan') :
						tgl_layanan = rec['tgl_layanan']
					else :
						tgl_layanan = False
					if rec.get('petugas_id') :
						petugas = rec['petugas_id']
					else :
						petugas = False
					if rec.get('eartag_id') :
						sapi = request.env['sapi'].sudo().search([('eartag_id','=',rec['eartag_id'])])
						id_sapi = sapi.id
						eartag = rec.get('eartag_id')
					else :
						id_sapi = False
						eartag = False
					# if rec.get('id_sapi') :
					# 	id_sapi = int(rec['id_sapi'])
					# else :
					# 	id_sapi = False
					if rec.get('kode_peternak_baru') :
						peternak = request.env['peternak.sapi'].sudo().search([('kode_peternak','=',rec['kode_peternak_baru'])], limit=1)
						peternak_baru = peternak.id
					else :
						peternak_baru = False
					if rec.get('keterangan') :
						keterangan = rec['keterangan']
					else :
						keterangan = False
					if rec.get('bcs') :
						bcs = rec['bcs']
					else :
						bcs = False

					petugas_id = request.env['medical.physician'].sudo().search([('id','=',rec['petugas_id'])], limit=1)
					sapi = request.env['sapi'].sudo().search([('eartag_id','=',rec['eartag_id'])],limit=1)
					value_data = {  'tgl_layanan': tgl_layanan,
									'petugas_id': petugas,
									'jabatan_id': petugas_id.jabatan_id.id,
									'id_sapi': id_sapi,
									'eartag_id': eartag,
									'kode_peternak_baru': rec['kode_peternak_baru'],
									'peternak_baru_id': peternak_baru,
									'peternak_lama_id': sapi.peternak_id.id,
									'bcs': bcs,
									'keterangan': keterangan
									  }

					new_record = request.env['form.ganti.pmlk'].sudo().create(value_data)
					new_record._onchange_petugas_id()
					new_record._onchange_tgl_layanan()

					if rec.get('eartag_id') and rec.get('kode_peternak_baru') :
						sapi = request.env['sapi'].sudo().search([('eartag_id','=',rec['eartag_id'])])
						if sapi :
							sapi.sudo().write({'peternak_id': peternak_baru})
							return ({'result':'Success Create History Ganti Pemilik Sapi and Update Pemilik Sapi', "ID Layanan": new_record.id})
						else :
							return ({'result':'Data Sapi Tidak Ditemukan'})
					return ({'result':'ID Sapi Or ID Peternak Baru is Empty'})
				return ({'result':'Failed Check Your Parameter'})
		except Exception as e:
			return {'status': False, 'error': str(e)}


	@http.route('/select_data_ganti_pemilik', auth="none", type='json',cors='*')
	def select_data_ganti_pemilik(self, **rec):
		try:
			header = request.httprequest.headers
			db= header.get('db')
			login = header.get('login')
			password = header.get('password')
			uid = request.session.authenticate(db, login, password)
			if uid:
				if request.jsonrequest :
					if rec.get('id_layanan'):
						layanan = request.env['form.ganti.pmlk'].search([('id','=',rec.get('id_layanan'))])
						data_layanan = []
						if layanan :
							value = {   'Anggota/Peternak'    : layanan.peternak_lama_id.peternak_name or None,
										'id_pemilik'          : None,
										'wilayah'             : None,
										'petugas'          	  : layanan.petugas_id.nama_petugas or None,
										'jabatan'       	  : layanan.jabatan_id.nama_jabatan or None,
										'tgl_layanan'         : layanan.tgl_layanan or None,
										'periode'       	  : layanan.periode_id.periode_setoran or None,
										'nama_sapi'       	  : layanan.id_sapi.first_name or None,
										'eartag_id'       	  : layanan.eartag_id or None,
										'bcs'       	  	  : layanan.bcs or None,
										'tps'    			  : layanan.tps_id.tps_name or None,
										'catatan_petugas'     : layanan.keterangan or None
										   
								}
			
							data_layanan.append(value)

							return ({"message": "Data Layanan", "Data": data_layanan})
						else :
							return ({'result':'Data Layanan tidak ditemukan'})


				else :
					return ({'result':'Failed Check Your Parameter'})
		except Exception as e:
			return {'status': False, 'error': str(e)}

		
