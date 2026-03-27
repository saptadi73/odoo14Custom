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


class KunjunganLimbah(http.Controller):

	@http.route('/create_form_kunjungan_pakan', auth="none", type='json',cors='*')
	def create_form_kunjungan_pakan(self, **rec):
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
					if rec.get('tgl_kunjungan') :
						tanggal_kunjungan = rec['tgl_kunjungan']
					else :
						tanggal_kunjungan = False
					if rec.get('periode_id') :
						periode_id = rec['periode_id']
					else :
						periode_id = False
					if rec.get('jns_hijauan_jerami') :
						jerami = rec['jns_hijauan_jerami']
					else :
						jerami = False
					if rec.get('jml_hijauan_jerami') :
						jml_jerami = rec['jml_hijauan_jerami']
					else :
						jml_jerami = False
					if rec.get('jns_hijauan_gajah') :
						gajah = rec['jns_hijauan_jerami']
					else :
						gajah = False
					if rec.get('jml_hijauan_gajah') :
						jml_gajah = rec['jml_hijauan_gajah']
					else :
						jml_gajah = False
					if rec.get('jenis_hijauan_tebon') :
						tebon = rec['jenis_hijauan_tebon']
					else :
						tebon = False
					if rec.get('juml_hijauan_tebon') :
						jml_tebon = rec['juml_hijauan_tebon']
					else :
						jml_tebon= False
					if rec.get('jenis_hijauan_tebu') :
						tebu = rec['jenis_hijauan_tebu']
					else :
						tebu = False
					if rec.get('juml_hijauan_tebu') :
						jml_tebu = rec['juml_hijauan_tebu']
					else :
						jml_tebu = False
					if rec.get('jenis_hijauan_pakchong') :
						packcong = rec['jenis_hijauan_pakchong']
					else :
						packcong = False
					if rec.get('juml_hijauan_pakchong') :
						jml_packcong = rec['juml_hijauan_pakchong']
					else :
						jml_packcong = False
					if rec.get('jenis_hijauan_odot') :
						odot = rec['jenis_hijauan_odot']
					else :
						odot = False
					if rec.get('juml_hijauan_odot') :
						jml_odot = rec['juml_hijauan_odot']
					else :
						jml_odot = False
					if rec.get('jenis_hijauan_lapang') :
						lapang = rec['jenis_hijauan_lapang']
					else :
						lapang = False
					if rec.get('juml_hijauan_lapang') :
						jml_lapang = rec['juml_hijauan_lapang']
					else :
						jml_lapang = False
					if rec.get('jenis_hijauan_1') :
						hijauan1 = rec['jenis_hijauan_1']
					else :
						hijauan1 = False
					if rec.get('juml_hijauan_1') :
						jml_hijauan1 = rec['juml_hijauan_1']
					else :
						jml_hijauan1 = False
					if rec.get('jenis_hijauan_2') :
						hijauan2 = rec['jenis_hijauan_2']
					else :
						hijauan2 = False
					if rec.get('juml_hijauan_2') :
						jml_hijauan2 = rec['juml_hijauan_2']
					else :
						jml_hijauan2 = False
					if rec.get('jenis_hijauan_3') :
						hijauan3 = rec['jenis_hijauan_3']
					else :
						hijauan3 = False
					if rec.get('juml_hijauan_3') :
						jml_hijauan3 = rec['juml_hijauan_3']
					else :
						jml_hijauan3 = False
					if rec.get('jenis_hijauan_4') :
						hijauan4 = rec['jenis_hijauan_4']
					else :
						hijauan4 = False
					if rec.get('juml_hijauan_4') :
						jml_hijauan4 = rec['juml_hijauan_4']
					else :
						jml_hijauan4 = False
					if rec.get('jenis_hijauan_5') :
						hijauan5 = rec['jenis_hijauan_5']
					else :
						hijauan5 = False
					if rec.get('juml_hijauan_5') :
						jml_hijauan5 = rec['juml_hijauan_5']
					else :
						jml_hijauan5 = False
					if rec.get('jenis_kons_plus') :
						kons_plus = rec['jenis_kons_plus']
					else :
						kons_plus = False
					if rec.get('juml_kons_plus') :
						jml_kons_plus = rec['juml_kons_plus']
					else :
						jml_kons_plus = False
					if rec.get('jenis_kons_2a') :
						kons_2a = rec['jenis_kons_2a']
					else :
						kons_2a = False
					if rec.get('juml_kons_2a') :
						jml_kons_2a = rec['juml_kons_2a']
					else :
						jml_kons_2a = False
					if rec.get('jenis_kons_mapan') :
						kons_mapan = rec['jenis_kons_mapan']
					else :
						kons_mapan = False
					if rec.get('juml_kons_mapan') :
						jml_kons_mapan = rec['juml_kons_mapan']
					else :
						jml_kons_mapan = False
					if rec.get('jenis_kons_feed') :
						kons_feed = rec['jenis_kons_feed']
					else :
						kons_feed = False
					if rec.get('juml_kons_feed') :
						jml_kons_feed = rec['juml_kons_feed']
					else :
						jml_kons_feed = False
					if rec.get('jenis_tambah_selep') :
						tambah_selep = rec['jenis_tambah_selep']
					else :
						tambah_selep = False
					if rec.get('juml_tambah_selep') :
						jml_tambah_selep = rec['juml_tambah_selep']
					else :
						jml_tambah_selep = False
					if rec.get('jenis_tambah_tawar') :
						tambah_tawar = rec['jenis_tambah_tawar']
					else :
						tambah_tawar = False
					if rec.get('juml_tambah_tawar') :
						jml_tambah_tawar = rec['juml_tambah_tawar']
					else :
						jml_tambah_tawar = False
					if rec.get('jenis_tambah_singkong') :
						tambah_singkong = rec['jenis_tambah_singkong']
					else :
						tambah_singkong = False
					if rec.get('juml_tambah_singkong') :
						jml_tambah_singkong = rec['juml_tambah_singkong']
					else :
						jml_tambah_singkong = False
					if rec.get('jenis_tambah_gamblong') :
						tambah_gamblong = rec['jenis_tambah_gamblong']
					else :
						tambah_gamblong = False
					if rec.get('juml_tambah_gamblong') :
						jml_tambah_gamblong = rec['juml_tambah_gamblong']
					else :
						jml_tambah_gamblong = False
					if rec.get('jenis_tambah_bir') :
						tambah_bir = rec['jenis_tambah_bir']
					else :
						tambah_bir = False
					if rec.get('juml_tambah_bir') :
						jml_tambah_bir = rec['juml_tambah_bir']
					else :
						jml_tambah_bir = False
					if rec.get('jenis_tambah_tahu') :
						tambah_tahu = rec['jenis_tambah_tahu']
					else :
						tambah_tahu = False
					if rec.get('juml_tambah_tahu') :
						jml_tambah_tahu = rec['juml_tambah_tahu']
					else :
						jml_tambah_tahu = False
					if rec.get('luas_lahan') :
						luas_lahan = rec['luas_lahan']
					else :
						luas_lahan = False
					if rec.get('jns_hpt') :
						jns_hpt = rec['jns_hpt']
					else :
						jns_hpt = False
					if rec.get('add_jns_hpt') :
						add_jns_hpt = rec['add_jns_hpt']
					else :
						add_jns_hpt = False
					if rec.get('produktivitas') :
						produktivitas = rec['produktivitas']
					else :
						produktivitas = False
					if rec.get('stts_kpmlkn') :
						stts_kpmlkn = rec['stts_kpmlkn']
					else :
						stts_kpmlkn = False
					if rec.get('choper') :
						choper = rec['choper']
					else :
						choper = False
					if rec.get('sapi_lines') :
						line_ids = []
						for line in rec.get('sapi_lines'):
							peternak = request.env['peternak.sapi'].search([('kode_peternak','=',line['kode_peternak'])])
							sapi = request.env['sapi'].sudo().search([('eartag_id','=',line['eartag_id'])])
							line_ids.append((0, 0,{	
													'peternak_id': peternak.id,
													'id_sapi': sapi.id,
													'prod_susu_liter' : line['prod_susu'],
													'id_status_reproduksi':line['status_reproduksi']
													}))

					
					
					value_data = {  'peternak_id': peternak_id,
									'petugas_id': petugas_id,
									'tanggal_kunjungan': tanggal_kunjungan,
									'periode_id': periode_id,
									'jenis_management': '1',
									'kunjungan_gdfp_line' : line_ids or None,
									'jenis_hijauan_jerami': jerami,
									'juml_hijauan_jerami': jml_jerami,
									'jenis_hijauan_gajah': gajah,
									'juml_hijauan_gajah': jml_gajah,
									'jenis_hijauan_tebon': tebon,
									'juml_hijauan_tebon': jml_tebon,
									'jenis_hijauan_tebu': tebu,
									'juml_hijauan_tebu': jml_tebu,
									'jenis_hijauan_pakchong': packcong,
									'juml_hijauan_pakchong': jml_packcong,
									'jenis_hijauan_odot': odot,
									'juml_hijauan_odot': jml_odot,
									'jenis_hijauan_lapang': lapang,
									'juml_hijauan_lapang': jml_lapang,
									'jenis_hijauan_1': hijauan1,
									'juml_hijauan_1': jml_hijauan1,
									'jenis_hijauan_2': hijauan2,
									'juml_hijauan_2': jml_hijauan2,
									'jenis_hijauan_3': hijauan3,
									'juml_hijauan_3': jml_hijauan3,
									'jenis_hijauan_4': hijauan4,
									'juml_hijauan_4': jml_hijauan4,
									'jenis_hijauan_5': hijauan5,
									'juml_hijauan_5': jml_hijauan5,
									'jenis_kons_plus': kons_plus,
									'juml_kons_plus': jml_kons_plus,
									'jenis_kons_2a': kons_2a,
									'juml_kons_2a': jml_kons_2a,
									'jenis_kons_mapan': kons_mapan,
									'juml_kons_mapan': jml_kons_mapan,
									'jenis_kons_feed': kons_feed,
									'juml_kons_feed': jml_kons_feed,
									'jenis_tambah_selep': tambah_selep,
									'juml_tambah_selep': jml_tambah_selep,
									'jenis_tambah_tawar': tambah_tawar,
									'juml_tambah_tawar': jml_tambah_tawar,
									'jenis_tambah_singkong': tambah_singkong,
									'juml_tambah_singkong': jml_tambah_singkong,
									'jenis_tambah_gamblong': tambah_gamblong,
									'juml_tambah_gamblong': jml_tambah_gamblong,
									'jenis_tambah_bir': tambah_bir,
									'juml_tambah_bir': jml_tambah_bir,
									'jenis_tambah_tahu': tambah_tahu,
									'juml_tambah_tahu': jml_tambah_tahu,
									'luas_lahan': luas_lahan,
									'jns_hpt': jns_hpt,
									'add_jns_hpt': add_jns_hpt,
									'produktivitas': produktivitas,
									'stts_kpmlkn': stts_kpmlkn,
									'choper'	: choper

									  }

					new_record = request.env['form.kunjungan.gdfp'].sudo().create(value_data)

					if new_record :
						return ({'result':'Create Form Kunjungan Pakan Success...!!'})
					else :
						return ({'result':'Create Form Kunjungan Pakan Gagal...!!'})


				return ({'result':'Failed Check Your Parameter'})
		except Exception as e:
			return {'status': False, 'error': str(e)}

		
