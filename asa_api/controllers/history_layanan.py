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


class HistoryLayanan(http.Controller):


	@http.route('/history_layanan_sapi', auth="none", type='json',cors='*')
	def select_history_layanan_sapi(self, **rec):
		try:
			header = request.httprequest.headers
			db= header.get('db')
			login = header.get('login')
			password = header.get('password')
			uid = request.session.authenticate(db, login, password)
			if uid:
				if request.jsonrequest :
					if rec.get('peternak_id') and rec.get('eartag_id') and rec.get('periode_id'):
						data_layanan = []
						value_data = {}
						pengobatan = request.env['form.pengobatan'].search([('peternak_id','=',rec.get('peternak_id')),('eartag_id','=',rec.get('eartag_id')),('periode_id','=',rec.get('periode_id'))])
						if pengobatan :
							for res in pengobatan :
								value_data = {  'tgl_layanan' :res.tgl_layanan,
												'id_layanan' :res.id,
												'nama_layanan': 'Pengobatan',
												'petugas_id': res.petugas_id.id
											}

							data_layanan.append(value_data)
						abortus = request.env['form.abortus'].search([('peternak_id','=',rec.get('peternak_id')),('eartag_id','=',rec.get('eartag_id')),('periode_id','=',rec.get('periode_id'))])
						if abortus :
							for res in abortus :
								value_data = {  'tgl_layanan' :res.tgl_layanan,
												'id_layanan' :res.id,
												'nama_layanan': 'Abortus',
												'petugas_id': res.petugas_id.id
											}

							data_layanan.append(value_data)
						pkb = request.env['form.pkb'].search([('peternak_id','=',rec.get('peternak_id')),('eartag_id','=',rec.get('eartag_id')),('periode_id','=',rec.get('periode_id'))])
						if pkb :
							for res in pkb :
								value_data = {  'tgl_layanan' :res.tgl_layanan,
												'id_layanan' :res.id,
												'nama_layanan': 'PKB',
												'petugas_id': res.petugas_id.id
											}

							data_layanan.append(value_data)
						mutasi = request.env['form.mutasi'].search([('peternak_id','=',rec.get('peternak_id')),('eartag_id','=',rec.get('eartag_id')),('periode_id','=',rec.get('periode_id'))])
						if mutasi :
							for res in mutasi :
								value_data = {  'tgl_layanan' :res.tgl_layanan,
												'id_layanan' :res.id,
												'nama_layanan': 'Mutasi',
												'petugas_id': res.petugas_id.id
											}

							data_layanan.append(value_data)
						ganti_id = request.env['form.gis'].search([('peternak_id','=',rec.get('peternak_id')),('eartag_id','=',rec.get('eartag_id')),('periode_id','=',rec.get('periode_id'))])
						if ganti_id :
							for res in ganti_id :
								value_data = {  'tgl_layanan' :res.tgl_layanan,
												'id_layanan' :res.id,
												'nama_layanan': "Ganti ID Sapi",
												'petugas_id': res.petugas_id.id
											}

							data_layanan.append(value_data)
						ib = request.env['form.ib'].search([('peternak_id','=',rec.get('peternak_id')),('eartag_id','=',rec.get('eartag_id')),('periode_id','=',rec.get('periode_id'))])
						if ib :
							for res in ib :
								value_data = {  'tgl_layanan' :res.tgl_layanan,
												'id_layanan' :res.id,
												'nama_layanan': 'IB',
												'petugas_id': res.petugas_id.id
											}

							data_layanan.append(value_data)
						kk = request.env['form.kk'].search([('peternak_id','=',rec.get('peternak_id')),('eartag_id','=',rec.get('eartag_id')),('periode_id','=',rec.get('periode_id'))])
						if kk :
							for res in kk :
								value_data = {  'tgl_layanan' :res.tgl_layanan,
												'id_layanan' :res.id,
												'nama_layanan': "Kering Kandang",
												'petugas_id': res.petugas_id.id
											}

							data_layanan.append(value_data)
						masuk = request.env['form.masuk'].search([('peternak_id','=',rec.get('peternak_id')),('eartag_id','=',rec.get('eartag_id')),('periode_id','=',rec.get('periode_id'))])
						if masuk :
							for res in masuk :
								value_data = {  'tgl_layanan' :res.tgl_layanan,
												'id_layanan' :res.id,
												'nama_layanan': 'Masuk',
												'petugas_id': res.petugas_id.id
											}

							data_layanan.append(value_data)
						melahirkan = request.env['form.melahirkan'].search([('peternak_id','=',rec.get('peternak_id')),('kode_eartag','=',rec.get('eartag_id')),('periode_id','=',rec.get('periode_id'))])
						if melahirkan :
							for res in melahirkan :
								value_data = {  'tgl_layanan' :res.tgl_layanan,
												'id_layanan' :res.id,
												'nama_layanan': 'Melahirkan',
												'petugas_id': res.petugas_id.id
											}

							data_layanan.append(value_data)
						nkt = request.env['form.nkt'].search([('peternak_id','=',rec.get('peternak_id')),('eartag_id','=',rec.get('eartag_id')),('periode_id','=',rec.get('periode_id'))])
						if nkt :
							for res in nkt :
								value_data = {  'tgl_layanan' :res.tgl_layanan,
												'id_layanan' :res.id,
												'nama_layanan': 'NKT',
												'petugas_id': res.petugas_id.id
											}

							data_layanan.append(value_data)
						pr = request.env['form.pr'].search([('peternak_id','=',rec.get('peternak_id')),('eartag_id','=',rec.get('eartag_id')),('periode_id','=',rec.get('periode_id'))])
						if pr :
							for res in pr :
								value_data = {  'tgl_layanan' :res.tgl_layanan,
												'id_layanan' :res.id,
												'nama_layanan': "Palpasi Rektal",
												'petugas_id': res.petugas_id.id
											}

							data_layanan.append(value_data)
						pt = request.env['form.pt'].search([('peternak_id','=',rec.get('peternak_id')),('eartag_id','=',rec.get('eartag_id')),('periode_id','=',rec.get('periode_id'))])
						if pt :
							for res in pt :
								value_data = {  'tgl_layanan' :res.tgl_layanan,
												'id_layanan' :res.id,
												'nama_layanan': "Potong Tanduk",
												'petugas_id': res.petugas_id.id
											}

							data_layanan.append(value_data)
						sq = request.env['form.sq'].search([('peternak_id','=',rec.get('peternak_id')),('eartag_id','=',rec.get('eartag_id')),('periode_id','=',rec.get('periode_id'))])
						if sq :
							for res in sq :
								value_data = {  'tgl_layanan' :res.tgl_layanan,
												'id_layanan' :res.id,
												'nama_layanan': "Sample Quartir",
												'petugas_id': res.petugas_id.id
											}

							data_layanan.append(value_data)
						specimen = request.env['form.specimen'].search([('peternak_id','=',rec.get('peternak_id')),('eartag_id','=',rec.get('eartag_id')),('periode_id','=',rec.get('periode_id'))])
						if specimen :
							for res in specimen :
								value_data = {  'tgl_layanan' :res.tgl_layanan,
												'id_layanan' :res.id,
												'nama_layanan': 'Specimen',
												'petugas_id': res.petugas_id.id
											}

							data_layanan.append(value_data)
						ganti_pemilik = request.env['form.ganti.pmlk'].search([('peternak_lama_id','=',rec.get('peternak_id')),('eartag_id','=',rec.get('eartag_id')),('periode_id','=',rec.get('periode_id'))])
						if ganti_pemilik :
							for res in ganti_pemilik :
								value_data = {  'tgl_layanan' :res.tgl_layanan,
												'id_layanan' :res.id,
												'nama_layanan': "Ganti Pemilik",
												'petugas_id': res.petugas_id.id
											}

							data_layanan.append(value_data)
						vaksinasi = request.env['form.vaksinasi'].search([('peternak_id','=',rec.get('peternak_id')),('eartag_id','=',rec.get('eartag_id')),('periode_id','=',rec.get('periode_id'))])
						if vaksinasi :
							for res in vaksinasi :
								value_data = {  'tgl_layanan' :res.tgl_layanan,
												'id_layanan' :res.id,
												'nama_layanan': 'Vaksinasi',
												'petugas_id': res.petugas_id.id
											}

							data_layanan.append(value_data)
						potong_kuku = request.env['form.pot.kuku'].search([('peternak_id','=',rec.get('peternak_id')),('eartag_id','=',rec.get('eartag_id')),('periode_id','=',rec.get('periode_id'))])
						if potong_kuku :
							for res in potong_kuku :
								value_data = {  'tgl_layanan' :res.tgl_layanan,
												'id_layanan' :res.id,
												'nama_layanan': "Potong Kuku",
												'petugas_id': res.petugas_id.id
											}

							data_layanan.append(value_data)
						identifikasi = request.env['form.ident'].search([('peternak_id','=',rec.get('peternak_id')),('eartag_id','=',rec.get('eartag_id')),('periode_id','=',rec.get('periode_id'))])
						if identifikasi :
							for res in identifikasi :
								value_data = {  'tgl_layanan' :res.tgl_layanan,
												'id_layanan' :res.id,
												'nama_layanan': 'Identifikasi',
												'petugas_id': res.petugas_id.id
											}

							data_layanan.append(value_data)
						return ({"message": "Data History Layanan", "Data": data_layanan})
					else :
						return ({'result':'Failed Check Your Parameter'})


				else :
					return ({'result':'Failed Check Your Parameter'})
		except Exception as e:
			return {'status': False, 'error': str(e)}


	@http.route('/history_layanan_petugas', auth="none", type='json',cors='*')
	def select_history_layanan_petugas(self, **rec):
		try:
			header = request.httprequest.headers
			db= header.get('db')
			login = header.get('login')
			password = header.get('password')
			uid = request.session.authenticate(db, login, password)
			if uid:
				if request.jsonrequest :
					if rec.get('petugas_id'):
						data_layanan = []
						value_data = {}
						pengobatan = request.env['form.pengobatan'].search([('petugas_id','=',rec.get('petugas_id'))])
						if pengobatan :
							for res in pengobatan :
								value_data = {  'tgl_layanan' :res.tgl_layanan,
												'id_layanan' :res.id,
												'nama_layanan': 'Pengobatan',
												'eartag_id': res.eartag_id,
												'is_permohonan': res.is_permohonan
											}

							data_layanan.append(value_data)
						abortus = request.env['form.abortus'].search([('petugas_id','=',rec.get('petugas_id'))])
						if abortus :
							for res in abortus :
								value_data = {  'tgl_layanan' :res.tgl_layanan,
												'id_layanan' :res.id,
												'nama_layanan': 'Abortus',
												'eartag_id': res.eartag_id,
												'is_permohonan': res.is_permohonan
											}

							data_layanan.append(value_data)
						pkb = request.env['form.pkb'].search([('petugas_id','=',rec.get('petugas_id'))])
						if pkb :
							for res in pkb :
								value_data = {  'tgl_layanan' :res.tgl_layanan,
												'id_layanan' :res.id,
												'nama_layanan': 'PKB',
												'eartag_id': res.eartag_id,
												'is_permohonan': res.is_permohonan
											}

							data_layanan.append(value_data)
						mutasi = request.env['form.mutasi'].search([('petugas_id','=',rec.get('petugas_id'))])
						if mutasi :
							for res in mutasi :
								value_data = {  'tgl_layanan' :res.tgl_layanan,
												'id_layanan' :res.id,
												'nama_layanan': 'Mutasi',
												'eartag_id': res.eartag_id,
												'is_permohonan': res.is_permohonan
											}

							data_layanan.append(value_data)
						ganti_id = request.env['form.gis'].search([('petugas_id','=',rec.get('petugas_id'))])
						if ganti_id :
							for res in ganti_id :
								value_data = {  'tgl_layanan' :res.tgl_layanan,
												'id_layanan' :res.id,
												'nama_layanan': "Ganti ID Sapi",
												'eartag_id': res.eartag_id,
												'is_permohonan': res.is_permohonan
											}

							data_layanan.append(value_data)
						ib = request.env['form.ib'].search([('petugas_id','=',rec.get('petugas_id'))])
						if ib :
							for res in ib :
								value_data = {  'tgl_layanan' :res.tgl_layanan,
												'id_layanan' :res.id,
												'nama_layanan': 'IB',
												'eartag_id': res.eartag_id,
												'is_permohonan': res.is_permohonan
											}

							data_layanan.append(value_data)
						kk = request.env['form.kk'].search([('petugas_id','=',rec.get('petugas_id'))])
						if kk :
							for res in kk :
								value_data = {  'tgl_layanan' :res.tgl_layanan,
												'id_layanan' :res.id,
												'nama_layanan': "Kering Kandang",
												'eartag_id': res.eartag_id,
												'is_permohonan': res.is_permohonan
											}

							data_layanan.append(value_data)
						masuk = request.env['form.masuk'].search([('petugas_id','=',rec.get('petugas_id'))])
						if masuk :
							for res in masuk :
								value_data = {  'tgl_layanan' :res.tgl_layanan,
												'id_layanan' :res.id,
												'nama_layanan': 'Masuk',
												'eartag_id': res.eartag_id,
												'is_permohonan': res.is_permohonan
											}

							data_layanan.append(value_data)
						melahirkan = request.env['form.melahirkan'].search([('petugas_id','=',rec.get('petugas_id'))])
						if melahirkan :
							for res in melahirkan :
								value_data = {  'tgl_layanan' :res.tgl_layanan,
												'id_layanan' :res.id,
												'nama_layanan': 'Melahirkan',
												'eartag_id': res.kode_eartag,
												'is_permohonan': res.is_permohonan
											}

							data_layanan.append(value_data)
						nkt = request.env['form.nkt'].search([('petugas_id','=',rec.get('petugas_id'))])
						if nkt :
							for res in nkt :
								value_data = {  'tgl_layanan' :res.tgl_layanan,
												'id_layanan' :res.id,
												'nama_layanan': 'NKT',
												'eartag_id': res.eartag_id,
												'is_permohonan': res.is_permohonan
											}

							data_layanan.append(value_data)
						pr = request.env['form.pr'].search([('petugas_id','=',rec.get('petugas_id'))])
						if pr :
							for res in pr :
								value_data = {  'tgl_layanan' :res.tgl_layanan,
												'id_layanan' :res.id,
												'nama_layanan': "Palpasi Rektal",
												'eartag_id': res.eartag_id,
												'is_permohonan': res.is_permohonan
											}

							data_layanan.append(value_data)
						pt = request.env['form.pt'].search([('petugas_id','=',rec.get('petugas_id'))])
						if pt :
							for res in pt :
								value_data = {  'tgl_layanan' :res.tgl_layanan,
												'id_layanan' :res.id,
												'nama_layanan': "Potong Tanduk",
												'eartag_id': res.eartag_id,
												'is_permohonan': res.is_permohonan
											}

							data_layanan.append(value_data)
						sq = request.env['form.sq'].search([('petugas_id','=',rec.get('petugas_id'))])
						if sq :
							for res in sq :
								value_data = {  'tgl_layanan' :res.tgl_layanan,
												'id_layanan' :res.id,
												'nama_layanan': "Sample Quartir",
												'eartag_id': res.eartag_id,
												'is_permohonan': res.is_permohonan
											}

							data_layanan.append(value_data)
						specimen = request.env['form.specimen'].search([('petugas_id','=',rec.get('petugas_id'))])
						if specimen :
							for res in specimen :
								value_data = {  'tgl_layanan' :res.tgl_layanan,
												'id_layanan' :res.id,
												'nama_layanan': 'Specimen',
												'eartag_id': res.eartag_id,
												'is_permohonan': res.is_permohonan
											}

							data_layanan.append(value_data)
						ganti_pemilik = request.env['form.ganti.pmlk'].search([('petugas_id','=',rec.get('petugas_id'))])
						if ganti_pemilik :
							for res in ganti_pemilik :
								value_data = {  'tgl_layanan' :res.tgl_layanan,
												'id_layanan' :res.id,
												'nama_layanan': "Ganti Pemilik",
												'eartag_id': res.eartag_id,
												'is_permohonan': res.is_permohonan
											}

							data_layanan.append(value_data)
						vaksinasi = request.env['form.vaksinasi'].search([('petugas_id','=',rec.get('petugas_id'))])
						if vaksinasi :
							for res in vaksinasi :
								value_data = {  'tgl_layanan' :res.tgl_layanan,
												'id_layanan' :res.id,
												'nama_layanan': 'Vaksinasi',
												'eartag_id': res.eartag_id,
												'is_permohonan': res.is_permohonan
											}

							data_layanan.append(value_data)
						potong_kuku = request.env['form.pot.kuku'].search([('petugas_id','=',rec.get('petugas_id'))])
						if potong_kuku :
							for res in potong_kuku :
								value_data = {  'tgl_layanan' :res.tgl_layanan,
												'id_layanan' :res.id,
												'nama_layanan': "Potong Kuku",
												'eartag_id': res.eartag_id,
												'is_permohonan': res.is_permohonan
											}

							data_layanan.append(value_data)
						identifikasi = request.env['form.ident'].search([('petugas_id','=',rec.get('petugas_id'))])
						if identifikasi :
							for res in identifikasi :
								value_data = {  'tgl_layanan' :res.tgl_layanan,
												'id_layanan' :res.id,
												'nama_layanan': 'Identifikasi',
												'eartag_id': res.eartag_id,
												'is_permohonan': res.is_permohonan
											}

							data_layanan.append(value_data)
						return ({"message": "Data History Layanan", "Data": data_layanan})
					else :
						return ({'result':'Failed Check Your Parameter'})


				else :
					return ({'result':'Failed Check Your Parameter'})
		except Exception as e:
			return {'status': False, 'error': str(e)}



		
