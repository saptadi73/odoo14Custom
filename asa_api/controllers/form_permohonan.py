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


class KunjunganKunjungan(http.Controller):


	@http.route('/create_form_permohonan', auth="none", type='json',cors='*')
	def create_form_permohonan(self, **rec):
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
					if rec.get('tgl_permohonan') :
						tgl_permohonan = rec['tgl_permohonan']
					else :
						tgl_permohonan = False
					if rec.get('catatan') :
						catatan = rec['catatan']
					else :
						catatan = False
					if rec.get('jenis_layanan') :
						jenis_layanan = str(rec['jenis_layanan'])
					else :
						jenis_layanan = False
				
					

					value_data = {  'peternak_id': peternak_id,
									'tgl_layanan': tgl_permohonan,
									'comments': catatan,
									'jenis_layanan': jenis_layanan,
									'status_layanan': 'draft',
								}

					new_record = request.env['medical.appointment'].sudo().create(value_data)

					if new_record :
						return ({'result':'Create Form Permohonan Success...!!'})
					else :
						return ({'result':'Create Form Permohonan Gagal...!!'})


				return ({'result':'Failed Check Your Parameter'})
		except Exception as e:
			return {'status': False, 'error': str(e)}

	@http.route('/update_form_permohonan', auth="none", type='json',cors='*')
	def update_form_permohonan(self, **rec):
		try:
			header = request.httprequest.headers
			db= header.get('db')
			login = header.get('login')
			password = header.get('password')
			uid = request.session.authenticate(db, login, password)
			if uid:
				if request.jsonrequest :
					if rec.get('permohonan_id') :
						permohonan = request.env['medical.appointment'].search([('id','=',rec.get('permohonan_id'))])
						if permohonan :
							if rec.get('eartag_id') :
								sapi = request.env['sapi'].sudo().search([('eartag_id','=',rec['eartag_id'])])
								id_sapi = sapi.id
							else :
								id_sapi = False
							if rec.get('petugas_id') :
								petugas_id = rec['petugas_id']
							else :
								petugas_id = False

							if permohonan.jenis_layanan == '1' :

								if rec.get('layanan_id') :
									layanan_id = rec['layanan_id']
								else :
									layanan_id = False
							
								value_data = {  'patient_id': id_sapi,
												'petugas_id': petugas_id,
												'pkb_id' : layanan_id,
												'status_layanan': 'open'
											}

								update_record = permohonan.sudo().write(value_data)
								permohonan.pkb_id.sudo().write({'is_permohonan': True})

							elif permohonan.jenis_layanan == '2' :

								if rec.get('layanan_id') :
									layanan_id = rec['layanan_id']
								else :
									layanan_id = False
							
								value_data = {  'patient_id': id_sapi,
												'petugas_id': petugas_id,
												'pengobatan_id' : layanan_id,
												'status_layanan': 'open'
											}

								update_record = permohonan.sudo().write(value_data)
								permohonan.pengobatan_id.sudo().write({'is_permohonan': True})

							elif permohonan.jenis_layanan == '3' :

								if rec.get('layanan_id') :
									layanan_id = rec['layanan_id']
								else :
									layanan_id = False
							
								value_data = {  'patient_id': id_sapi,
												'petugas_id': petugas_id,
												'mutasi_id' : layanan_id,
												'status_layanan': 'open'
											}

								update_record = permohonan.sudo().write(value_data)
								permohonan.mutasi_id.sudo().write({'is_permohonan': True})

							elif permohonan.jenis_layanan == '4' :

								if rec.get('layanan_id') :
									layanan_id = rec['layanan_id']
								else :
									layanan_id = False
							
								value_data = {  'patient_id': id_sapi,
												'petugas_id': petugas_id,
												'ganti_sapi_id' : layanan_id,
												'status_layanan': 'open'
											}

								update_record = permohonan.sudo().write(value_data)
								permohonan.mutasi_id.sudo().write({'is_permohonan': True})

							elif permohonan.jenis_layanan == '5' :

								if rec.get('layanan_id') :
									layanan_id = rec['layanan_id']
								else :
									layanan_id = False
							
								value_data = {  'patient_id': id_sapi,
												'petugas_id': petugas_id,
												'ib_id' : layanan_id,
												'status_layanan': 'open'
											}

								update_record = permohonan.sudo().write(value_data)
								permohonan.mutasi_id.sudo().write({'is_permohonan': True})

							elif permohonan.jenis_layanan == '6' :

								if rec.get('layanan_id') :
									layanan_id = rec['layanan_id']
								else :
									layanan_id = False
							
								value_data = {  'patient_id': id_sapi,
												'petugas_id': petugas_id,
												'sapi_masuk_id' : layanan_id,
												'status_layanan': 'open'
											}

								update_record = permohonan.sudo().write(value_data)
								permohonan.mutasi_id.sudo().write({'is_permohonan': True})

							elif permohonan.jenis_layanan == '7' :

								if rec.get('layanan_id') :
									layanan_id = rec['layanan_id']
								else :
									layanan_id = False
							
								value_data = {  'patient_id': id_sapi,
												'petugas_id': petugas_id,
												'melahirkan_id' : layanan_id,
												'status_layanan': 'open'
											}

								update_record = permohonan.sudo().write(value_data)
								permohonan.mutasi_id.sudo().write({'is_permohonan': True})

							elif permohonan.jenis_layanan == '8' :

								if rec.get('layanan_id') :
									layanan_id = rec['layanan_id']
								else :
									layanan_id = False
							
								value_data = {  'patient_id': id_sapi,
												'petugas_id': petugas_id,
												'ganti_pemilik_id' : layanan_id,
												'status_layanan': 'open'
											}

								update_record = permohonan.sudo().write(value_data)
								permohonan.mutasi_id.sudo().write({'is_permohonan': True})

							elif permohonan.jenis_layanan == '10' :

								if rec.get('layanan_id') :
									layanan_id = rec['layanan_id']
								else :
									layanan_id = False
							
								value_data = {  'patient_id': id_sapi,
												'petugas_id': petugas_id,
												'vaksin_id' : layanan_id,
												'status_layanan': 'open'
											}

								update_record = permohonan.sudo().write(value_data)
								permohonan.mutasi_id.sudo().write({'is_permohonan': True})

							elif permohonan.jenis_layanan == '11' :

								if rec.get('layanan_id') :
									layanan_id = rec['layanan_id']
								else :
									layanan_id = False
							
								value_data = {  'patient_id': id_sapi,
												'petugas_id': petugas_id,
												'abortus_id' : layanan_id,
												'status_layanan': 'open'
											}

								update_record = permohonan.sudo().write(value_data)
								permohonan.mutasi_id.sudo().write({'is_permohonan': True})

							elif permohonan.jenis_layanan == '12' :

								if rec.get('layanan_id') :
									layanan_id = rec['layanan_id']
								else :
									layanan_id = False
							
								value_data = {  'patient_id': id_sapi,
												'petugas_id': petugas_id,
												'specimen_id' : layanan_id,
												'status_layanan': 'open'
											}

								update_record = permohonan.sudo().write(value_data)
								permohonan.mutasi_id.sudo().write({'is_permohonan': True})

							elif permohonan.jenis_layanan == '13' :

								if rec.get('layanan_id') :
									layanan_id = rec['layanan_id']
								else :
									layanan_id = False
							
								value_data = {  'patient_id': id_sapi,
												'petugas_id': petugas_id,
												'kering_kandang_id' : layanan_id,
												'status_layanan': 'open'
											}

								update_record = permohonan.sudo().write(value_data)
								permohonan.mutasi_id.sudo().write({'is_permohonan': True})

							elif permohonan.jenis_layanan == '14' :

								if rec.get('layanan_id') :
									layanan_id = rec['layanan_id']
								else :
									layanan_id = False
							
								value_data = {  'patient_id': id_sapi,
												'petugas_id': petugas_id,
												'potong_id' : layanan_id,
												'status_layanan': 'open'
											}

								update_record = permohonan.sudo().write(value_data)
								permohonan.mutasi_id.sudo().write({'is_permohonan': True})

							elif permohonan.jenis_layanan == '15' :

								if rec.get('layanan_id') :
									layanan_id = rec['layanan_id']
								else :
									layanan_id = False
							
								value_data = {  'patient_id': id_sapi,
												'petugas_id': petugas_id,
												'potong_tanduk_id' : layanan_id,
												'status_layanan': 'open'
											}

								update_record = permohonan.sudo().write(value_data)
								permohonan.mutasi_id.sudo().write({'is_permohonan': True})

							elif permohonan.jenis_layanan == '16' :

								if rec.get('layanan_id') :
									layanan_id = rec['layanan_id']
								else :
									layanan_id = False
							
								value_data = {  'patient_id': id_sapi,
												'petugas_id': petugas_id,
												'nkt_id' : layanan_id,
												'status_layanan': 'open'
											}

								update_record = permohonan.sudo().write(value_data)
								permohonan.mutasi_id.sudo().write({'is_permohonan': True})

							elif permohonan.jenis_layanan == '17' :

								if rec.get('layanan_id') :
									layanan_id = rec['layanan_id']
								else :
									layanan_id = False
							
								value_data = {  'patient_id': id_sapi,
												'petugas_id': petugas_id,
												'palpasi_id' : layanan_id,
												'status_layanan': 'open'
											}

								update_record = permohonan.sudo().write(value_data)
								permohonan.mutasi_id.sudo().write({'is_permohonan': True})

							elif permohonan.jenis_layanan == '18' :

								if rec.get('layanan_id') :
									layanan_id = rec['layanan_id']
								else :
									layanan_id = False
							
								value_data = {  'patient_id': id_sapi,
												'petugas_id': petugas_id,
												'sampel_id' : layanan_id,
												'status_layanan': 'open'
											}

								update_record = permohonan.sudo().write(value_data)
								permohonan.mutasi_id.sudo().write({'is_permohonan': True})

							elif permohonan.jenis_layanan == '20' :

								if rec.get('layanan_id') :
									layanan_id = rec['layanan_id']
								else :
									layanan_id = False
							
								value_data = {  'patient_id': id_sapi,
												'petugas_id': petugas_id,
												'identifikasi_id' : layanan_id,
												'status_layanan': 'open'
											}

								update_record = permohonan.sudo().write(value_data)
								permohonan.mutasi_id.sudo().write({'is_permohonan': True})


							if update_record :
								return ({'result':'Update Form Permohonan Success...!!'})
							else :
								return ({'result':'Update Form Permohonan Gagal...!!'})


					else :
						return ({'result':'Failed Check Your Parameter'})



				return ({'result':'Failed Check Your Parameter'})
		except Exception as e:
			return {'status': False, 'error': str(e)}

	@http.route('/update_status_permohonan_close', auth="none", type='json',cors='*')
	def update_status_permohonan(self, **rec):
		try:
			header = request.httprequest.headers
			db= header.get('db')
			login = header.get('login')
			password = header.get('password')
			uid = request.session.authenticate(db, login, password)
			if uid:
				if request.jsonrequest :
					if rec.get('permohonan_id') :
						permohonan = request.env['medical.appointment'].search([('id','=',rec.get('permohonan_id'))])
						if permohonan :
						
							value_data = { 
											'status_layanan': 'close'
										}

							update_record = permohonan.sudo().write(value_data)

							if update_record :
								return ({'result':'Update Status Permohonan Success...!!'})
							else :
								return ({'result':'Update Status Permohonan Gagal...!!'})


					else :
						return ({'result':'Failed Check Your Parameter'})



				return ({'result':'Failed Check Your Parameter'})
		except Exception as e:
			return {'status': False, 'error': str(e)}



	@http.route('/select_data_permohonan', auth="none", type='json',cors='*')
	def select_data_permohonan(self, **rec):
		try:
			header = request.httprequest.headers
			db= header.get('db')
			login = header.get('login')
			password = header.get('password')
			uid = request.session.authenticate(db, login, password)
			if uid:
				if request.jsonrequest :
					if rec.get('petugas_id'):
						permohonan = request.env['medical.appointment'].search([('petugas_id','=',rec.get('petugas_id')),('status_layanan','=','open')])
						data_permohonan = []
						if permohonan :
							for p in permohonan :
								if p.jenis_layanan == '1' :
									jns_layanan = 'PKB'
								elif p.jenis_layanan == '2' :
									jns_layanan = 'Pengobatan'
								elif p.jenis_layanan == '3' :
									jns_layanan = 'Mutasi'
								elif p.jenis_layanan == '4' :
									jns_layanan = 'Ganti ID Sapi'
								elif p.jenis_layanan == '5' :
									jns_layanan = 'IB'
								elif p.jenis_layanan == '6' :
									jns_layanan = 'Sapi Masuk'
								elif p.jenis_layanan == '7' :
									jns_layanan = 'Melahirkan'
								elif p.jenis_layanan == '8' :
									jns_layanan = 'Ganti Pemilik'
								elif p.jenis_layanan == '10' :
									jns_layanan = 'Vaksinasi'
								elif p.jenis_layanan == '11' :
									jns_layanan = 'Abortus'
								elif p.jenis_layanan == '12' :
									jns_layanan = 'Specimen'
								elif p.jenis_layanan == '13' :
									jns_layanan = 'Kering Kandang'
								elif p.jenis_layanan == '14' :
									jns_layanan = 'Potong kuku'
								elif p.jenis_layanan == '15' :
									jns_layanan = 'Potong Tanduk'
								elif p.jenis_layanan == '16' :
									jns_layanan = 'NKT/Ukur BB TB'
								elif p.jenis_layanan == '17' :
									jns_layanan = 'Palpasi Rektal'
								elif p.jenis_layanan == '18' :
									jns_layanan = 'Sampel Kuartir'
								elif p.jenis_layanan == '20' :
									jns_layanan = 'Identifikasi'
								else :
									jns_layanan = False


								value = {   'permohonan_id'        : p.id,
											'sapi'           	   : p.patient_id.first_name,
											'peternak_id'          : p.peternak_id.id,
											'peternak_name'        : p.peternak_id.peternak_name,
											'kode_peternak'        : p.peternak_id.kode_peternak,
											'tps_id'          	   : p.peternak_id.tps_id.id,
											'tps_name'        	   : p.peternak_id.tps_id.tps_name,
											'wilayah'              : p.peternak_id.wilayah_id.wilayah_id,
											'tgl_permohonan'       : p.tgl_layanan,
											'petugas_id'           : p.petugas_id.id,
											'petugas_name'         : p.petugas_id.nama_petugas,
											'jabatan_id'           : p.petugas_id.jabatan_id.nama_jabatan,
											'id_jenis_layanan'     : p.jenis_layanan,
											'jenis_layanan'        : jns_layanan,
											'comments'             : p.comments,
											'status_layanan'       : p.status_layanan
												   
										}
								data_permohonan.append(value)
							return ({"message": "Data Permohonan", "Data": data_permohonan})
						else :
							return ({'result':'Permohonan tidak ditemukan'})


					elif rec.get('tps_id'):
						permohonan = request.env['medical.appointment'].search([('peternak_id.tps_id','=',rec.get('tps_id')),('status_layanan','=','draft')])
						data_permohonan = []
						if permohonan :
							for p in permohonan :
								if p.jenis_layanan == '1' :
									jns_layanan = 'PKB'
								elif p.jenis_layanan == '2' :
									jns_layanan = 'Pengobatan'
								elif p.jenis_layanan == '3' :
									jns_layanan = 'Mutasi'
								elif p.jenis_layanan == '4' :
									jns_layanan = 'Ganti ID Sapi'
								elif p.jenis_layanan == '5' :
									jns_layanan = 'IB'
								elif p.jenis_layanan == '6' :
									jns_layanan = 'Sapi Masuk'
								elif p.jenis_layanan == '7' :
									jns_layanan = 'Melahirkan'
								elif p.jenis_layanan == '8' :
									jns_layanan = 'Ganti Pemilik'
								elif p.jenis_layanan == '10' :
									jns_layanan = 'Vaksinasi'
								elif p.jenis_layanan == '11' :
									jns_layanan = 'Abortus'
								elif p.jenis_layanan == '12' :
									jns_layanan = 'Specimen'
								elif p.jenis_layanan == '13' :
									jns_layanan = 'Kering Kandang'
								elif p.jenis_layanan == '14' :
									jns_layanan = 'Potong kuku'
								elif p.jenis_layanan == '15' :
									jns_layanan = 'Potong Tanduk'
								elif p.jenis_layanan == '16' :
									jns_layanan = 'NKT/Ukur BB TB'
								elif p.jenis_layanan == '17' :
									jns_layanan = 'Palpasi Rektal'
								elif p.jenis_layanan == '18' :
									jns_layanan = 'Sampel Kuartir'
								elif p.jenis_layanan == '20' :
									jns_layanan = 'Identifikasi'
								else :
									jns_layanan = False


								value = {   'permohonan_id'        : p.id,
											'sapi'           	   : p.patient_id.first_name,
											'peternak_id'          : p.peternak_id.id,
											'peternak_name'        : p.peternak_id.peternak_name,
											'kode_peternak'        : p.peternak_id.kode_peternak,
											'tps_id'          	   : p.peternak_id.tps_id.id,
											'tps_name'        	   : p.peternak_id.tps_id.tps_name,
											'wilayah'              : p.peternak_id.wilayah_id.wilayah_id,
											'tgl_permohonan'       : p.tgl_layanan,
											'petugas_id'           : p.petugas_id.id,
											'petugas_name'         : p.petugas_id.nama_petugas,
											'jabatan_id'           : p.petugas_id.jabatan_id.nama_jabatan,
											'id_jenis_layanan'     : p.jenis_layanan,
											'jenis_layanan'        : jns_layanan,
											'comments'             : p.comments,
											'status_layanan'       : p.status_layanan
												   
										}
								data_permohonan.append(value)
							return ({"message": "Data Permohonan", "Data": data_permohonan})
						else :
							return ({'result':'Permohonan tidak ditemukan'})
					

					else :
						permohonan = request.env['medical.appointment'].search([('status_layanan','=','draft')])
						data_permohonan = []
						if permohonan :
							for p in permohonan :
								if p.jenis_layanan == '1' :
									jns_layanan = 'PKB'
								elif p.jenis_layanan == '2' :
									jns_layanan = 'Pengobatan'
								elif p.jenis_layanan == '3' :
									jns_layanan = 'Mutasi'
								elif p.jenis_layanan == '4' :
									jns_layanan = 'Ganti ID Sapi'
								elif p.jenis_layanan == '5' :
									jns_layanan = 'IB'
								elif p.jenis_layanan == '6' :
									jns_layanan = 'Sapi Masuk'
								elif p.jenis_layanan == '7' :
									jns_layanan = 'Melahirkan'
								elif p.jenis_layanan == '8' :
									jns_layanan = 'Ganti Pemilik'
								elif p.jenis_layanan == '10' :
									jns_layanan = 'Vaksinasi'
								elif p.jenis_layanan == '11' :
									jns_layanan = 'Abortus'
								elif p.jenis_layanan == '12' :
									jns_layanan = 'Specimen'
								elif p.jenis_layanan == '13' :
									jns_layanan = 'Kering Kandang'
								elif p.jenis_layanan == '14' :
									jns_layanan = 'Potong kuku'
								elif p.jenis_layanan == '15' :
									jns_layanan = 'Potong Tanduk'
								elif p.jenis_layanan == '16' :
									jns_layanan = 'NKT/Ukur BB TB'
								elif p.jenis_layanan == '17' :
									jns_layanan = 'Palpasi Rektal'
								elif p.jenis_layanan == '18' :
									jns_layanan = 'Sampel Kuartir'
								elif p.jenis_layanan == '20' :
									jns_layanan = 'Identifikasi'
								else :
									jns_layanan = False

								value = {   'permohonan_id'        : p.id,
											'sapi'           	   : p.patient_id.first_name,
											'peternak_id'          : p.peternak_id.id,
											'peternak_name'        : p.peternak_id.peternak_name,
											'kode_peternak'        : p.peternak_id.kode_peternak,
											'tps_id'          	   : p.peternak_id.tps_id.id,
											'tps_name'        	   : p.peternak_id.tps_id.tps_name,
											'wilayah'              : p.peternak_id.wilayah_id.wilayah_id,
											'tgl_permohonan'       : p.tgl_layanan,
											'petugas_id'           : p.petugas_id.id,
											'petugas_name'         : p.petugas_id.nama_petugas,
											'jabatan_id'           : p.petugas_id.jabatan_id.nama_jabatan,
											'id_jenis_layanan'     : p.jenis_layanan,
											'jenis_layanan'        : jns_layanan,
											'comments'             : p.comments,
											'status_layanan'       : p.status_layanan
												   
										}
								data_permohonan.append(value)
							return ({"message": "Data Permohonan", "Data": data_permohonan})
						else :
							return ({'result':'Permohonan tidak ditemukan'})

				else :
					return ({'result':'Failed Check Your Parameter'})
		except Exception as e:
			return {'status': False, 'error': str(e)}



	@http.route('/history_permohonan_petugas', auth="none", type='json',cors='*')
	def select_history_permohonan(self, **rec):
		try:
			header = request.httprequest.headers
			db= header.get('db')
			login = header.get('login')
			password = header.get('password')
			uid = request.session.authenticate(db, login, password)
			if uid:
				if request.jsonrequest :
					if rec.get('petugas_id'):
						permohonan = request.env['medical.appointment'].search([('petugas_id','=',rec.get('petugas_id')),('status_layanan','=','close')])
						data_permohonan = []
						if permohonan :
							for p in permohonan :
								if p.jenis_layanan == '1' :

									value_data = {  'id_layanan' : p.pkb_id.id,
													'jenis_layanan': 'PKB',
													'id_sapi': p.patient_id.id,
													'created' : p.create_date,
												}


								elif p.jenis_layanan == '2' :

									value_data = {  'id_layanan' : p.pengobatan_id.id,
													'jenis_layanan': 'Pengobatan',
													'id_sapi': p.patient_id.id,
													'created' : p.create_date,
												}


								elif p.jenis_layanan == '3' :

									value_data = {  'id_layanan' : p.mutasi_id.id,
													'jenis_layanan': 'Mutasi',
													'id_sapi': p.patient_id.id,
													'created' : p.create_date,
												}
								elif p.jenis_layanan == '4' :

									value_data = {  'id_layanan' : p.ganti_sapi_id.id,
													'jenis_layanan': "Ganti ID Sapi",
													'id_sapi': p.patient_id.id,
													'created' : p.create_date,
												}
								elif p.jenis_layanan == '5' :

									value_data = {  'id_layanan' : p.ib_id.id,
													'jenis_layanan': 'IB',
													'id_sapi': p.patient_id.id,
													'created' : p.create_date,
												}
								elif p.jenis_layanan == '6' :

									value_data = {  'id_layanan' : p.sapi_masuk_id.id,
													'jenis_layanan': "Sapi Masuk",
													'id_sapi': p.patient_id.id,
													'created' : p.create_date,
												}
								elif p.jenis_layanan == '7' :

									value_data = {  'id_layanan' : p.melahirkan_id.id,
													'jenis_layanan': 'Melahirkan',
													'id_sapi': p.patient_id.id,
													'created' : p.create_date,
												}
								elif p.jenis_layanan == '8' :

									value_data = {  'id_layanan' : p.ganti_pemilik_id.id,
													'jenis_layanan': "Ganti Pemilik",
													'id_sapi': p.patient_id.id,
													'created' : p.create_date,
												}
								elif p.jenis_layanan == '10' :

									value_data = {  'id_layanan' : p.vaksin_id.id,
													'jenis_layanan': 'Vaksinasi',
													'id_sapi': p.patient_id.id,
													'created' : p.create_date,
												}
								elif p.jenis_layanan == '11' :

									value_data = {  'id_layanan' : p.abortus_id.id,
													'jenis_layanan': 'Abortus',
													'id_sapi': p.patient_id.id,
													'created' : p.create_date,
												}
								elif p.jenis_layanan == '12' :

									value_data = {  'id_layanan' : p.specimen_id.id,
													'jenis_layanan': 'Specimen',
													'id_sapi': p.patient_id.id,
													'created' : p.create_date,
												}
								elif p.jenis_layanan == '13' :

									value_data = {  'id_layanan' : p.kering_kandang_id.id,
													'jenis_layanan': "Kering Kandang",
													'id_sapi': p.patient_id.id,
													'created' : p.create_date,
												}
								elif p.jenis_layanan == '14' :

									value_data = {  'id_layanan' : p.potong_id.id,
													'jenis_layanan': "Potong Kuku",
													'id_sapi': p.patient_id.id,
													'created' : p.create_date,
												}
								elif p.jenis_layanan == '15' :

									value_data = {  'id_layanan' : p.potong_tanduk_id.id,
													'jenis_layanan': "Potong Tanduk",
													'id_sapi': p.patient_id.id,
													'created' : p.create_date,
												}
								elif p.jenis_layanan == '16' :

									value_data = {  'id_layanan' : p.nkt_id.id,
													'jenis_layanan': 'NKT',
													'id_sapi': p.patient_id.id,
													'created' : p.create_date,
												}
								elif p.jenis_layanan == '17' :

									value_data = {  'id_layanan' : p.palpasi_id.id,
													'jenis_layanan': "Palpasi Rektal",
													'id_sapi': p.patient_id.id,
													'created' : p.create_date,
												}
								elif p.jenis_layanan == '18' :

									value_data = {  'id_layanan' : p.sampel_id.id,
													'jenis_layanan': "Sample Quartir",
													'id_sapi': p.patient_id.id,
													'created' : p.create_date,
												}
								elif p.jenis_layanan == '20' :

									value_data = {  'id_layanan' : p.identifikasi_id.id,
													'jenis_layanan': 'Identifikasi',
													'id_sapi': p.patient_id.id,
													'created' : p.create_date,
												}
								else :

									value_data = {  'id_layanan' :False,
													'jenis_layanan': False,
													'id_sapi': False,
													'created' : False,
												}


								data_permohonan.append(value_data)
							return ({"message": "Data History", "Data": data_permohonan})
						else :
							return ({'result':'History Permohonan tidak ditemukan'})


				else :
					return ({'result':'Failed Check Your Parameter'})
		except Exception as e:
			return {'status': False, 'error': str(e)}




	@http.route('/history_permohonan_peternak', auth="none", type='json',cors='*')
	def select_history_permohonan_peternak(self, **rec):
		try:
			header = request.httprequest.headers
			db= header.get('db')
			login = header.get('login')
			password = header.get('password')
			uid = request.session.authenticate(db, login, password)
			if uid:
				if request.jsonrequest :
					if rec.get('peternak_id'):
						permohonan = request.env['medical.appointment'].search([('peternak_id','=',rec.get('peternak_id'))])
						data_permohonan = []
						if permohonan :
							for p in permohonan :
								if p.jenis_layanan == '1' :

									value_data = {  'id_layanan' : p.pkb_id.id,
													'jenis_layanan': 'PKB',
													'id_sapi': p.patient_id.id,
													'created' : p.create_date,
													'tgl_permohonan' : p.tgl_layanan,
													'catatan' : p.comments,
													'status' : p.status_layanan
												}


								elif p.jenis_layanan == '2' :

									value_data = {  'id_layanan' : p.pengobatan_id.id,
													'jenis_layanan': 'Pengobatan',
													'id_sapi': p.patient_id.id,
													'created' : p.create_date,
													'tgl_permohonan' : p.tgl_layanan,
													'catatan' : p.comments,
													'status' : p.status_layanan
												}


								elif p.jenis_layanan == '3' :

									value_data = {  'id_layanan' : p.mutasi_id.id,
													'jenis_layanan': 'Mutasi',
													'id_sapi': p.patient_id.id,
													'created' : p.create_date,
													'tgl_permohonan' : p.tgl_layanan,
													'catatan' : p.comments,
													'status' : p.status_layanan
												}
								elif p.jenis_layanan == '4' :

									value_data = {  'id_layanan' : p.ganti_sapi_id.id,
													'jenis_layanan': "Ganti ID Sapi",
													'id_sapi': p.patient_id.id,
													'created' : p.create_date,
													'tgl_permohonan' : p.tgl_layanan,
													'catatan' : p.comments,
													'status' : p.status_layanan
												}
								elif p.jenis_layanan == '5' :

									value_data = {  'id_layanan' : p.ib_id.id,
													'jenis_layanan': 'IB',
													'id_sapi': p.patient_id.id,
													'created' : p.create_date,
													'tgl_permohonan' : p.tgl_layanan,
													'catatan' : p.comments,
													'status' : p.status_layanan
												}
								elif p.jenis_layanan == '6' :

									value_data = {  'id_layanan' : p.sapi_masuk_id.id,
													'jenis_layanan': "Sapi Masuk",
													'id_sapi': p.patient_id.id,
													'created' : p.create_date,
													'tgl_permohonan' : p.tgl_layanan,
													'catatan' : p.comments,
													'status' : p.status_layanan
												}
								elif p.jenis_layanan == '7' :

									value_data = {  'id_layanan' : p.melahirkan_id.id,
													'jenis_layanan': 'Melahirkan',
													'id_sapi': p.patient_id.id,
													'created' : p.create_date,
													'tgl_permohonan' : p.tgl_layanan,
													'catatan' : p.comments,
													'status' : p.status_layanan
												}
								elif p.jenis_layanan == '8' :

									value_data = {  'id_layanan' : p.ganti_pemilik_id.id,
													'jenis_layanan': "Ganti Pemilik",
													'id_sapi': p.patient_id.id,
													'created' : p.create_date,
													'tgl_permohonan' : p.tgl_layanan,
													'catatan' : p.comments,
													'status' : p.status_layanan
												}
								elif p.jenis_layanan == '10' :

									value_data = {  'id_layanan' : p.vaksin_id.id,
													'jenis_layanan': 'Vaksinasi',
													'id_sapi': p.patient_id.id,
													'created' : p.create_date,
													'tgl_permohonan' : p.tgl_layanan,
													'catatan' : p.comments,
													'status' : p.status_layanan
												}
								elif p.jenis_layanan == '11' :

									value_data = {  'id_layanan' : p.abortus_id.id,
													'jenis_layanan': 'Abortus',
													'id_sapi': p.patient_id.id,
													'created' : p.create_date,
													'tgl_permohonan' : p.tgl_layanan,
													'catatan' : p.comments,
													'status' : p.status_layanan
												}
								elif p.jenis_layanan == '12' :

									value_data = {  'id_layanan' : p.specimen_id.id,
													'jenis_layanan': 'Specimen',
													'id_sapi': p.patient_id.id,
													'created' : p.create_date,
													'tgl_permohonan' : p.tgl_layanan,
													'catatan' : p.comments,
													'status' : p.status_layanan
												}
								elif p.jenis_layanan == '13' :

									value_data = {  'id_layanan' : p.kering_kandang_id.id,
													'jenis_layanan': "Kering Kandang",
													'id_sapi': p.patient_id.id,
													'created' : p.create_date,
													'tgl_permohonan' : p.tgl_layanan,
													'catatan' : p.comments,
													'status' : p.status_layanan
												}
								elif p.jenis_layanan == '14' :

									value_data = {  'id_layanan' : p.potong_id.id,
													'jenis_layanan': "Potong Kuku",
													'id_sapi': p.patient_id.id,
													'created' : p.create_date,
													'tgl_permohonan' : p.tgl_layanan,
													'catatan' : p.comments,
													'status' : p.status_layanan
												}
								elif p.jenis_layanan == '15' :

									value_data = {  'id_layanan' : p.potong_tanduk_id.id,
													'jenis_layanan': "Potong Tanduk",
													'id_sapi': p.patient_id.id,
													'created' : p.create_date,
													'tgl_permohonan' : p.tgl_layanan,
													'catatan' : p.comments,
													'status' : p.status_layanan
												}
								elif p.jenis_layanan == '16' :

									value_data = {  'id_layanan' : p.nkt_id.id,
													'jenis_layanan': 'NKT',
													'id_sapi': p.patient_id.id,
													'created' : p.create_date,
													'tgl_permohonan' : p.tgl_layanan,
													'catatan' : p.comments,
													'status' : p.status_layanan
												}
								elif p.jenis_layanan == '17' :

									value_data = {  'id_layanan' : p.palpasi_id.id,
													'jenis_layanan': "Palpasi Rektal",
													'id_sapi': p.patient_id.id,
													'created' : p.create_date,
													'tgl_permohonan' : p.tgl_layanan,
													'catatan' : p.comments,
													'status' : p.status_layanan
												}
								elif p.jenis_layanan == '18' :

									value_data = {  'id_layanan' : p.sampel_id.id,
													'jenis_layanan': "Sample Quartir",
													'id_sapi': p.patient_id.id,
													'created' : p.create_date,
													'tgl_permohonan' : p.tgl_layanan,
													'catatan' : p.comments,
													'status' : p.status_layanan
												}
								elif p.jenis_layanan == '20' :

									value_data = {  'id_layanan' : p.identifikasi_id.id,
													'jenis_layanan': 'Identifikasi',
													'id_sapi': p.patient_id.id,
													'created' : p.create_date,
													'status' : p.status_layanan

												}
								else :

									value_data = {  'id_layanan' :False,
													'jenis_layanan': False,
													'id_sapi': False,
													'created' : False,
												}


								data_permohonan.append(value_data)
							return ({"message": "Data History", "Data": data_permohonan})
						else :
							return ({'result':'History Permohonan tidak ditemukan'})


				else :
					return ({'result':'Failed Check Your Parameter'})
		except Exception as e:
			return {'status': False, 'error': str(e)}



		
