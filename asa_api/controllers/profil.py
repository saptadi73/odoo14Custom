from odoo import http, models
from odoo.http import request
import json
import logging

_logger = logging.getLogger(__name__)


class ProfilSapi(http.Controller):
    
    @http.route('/load_profil_sapi', auth="none", type='json',cors='*')
    def load_profil_sapi(self, **rec):
        try:
            header = request.httprequest.headers
            db= header.get('db')
            login = header.get('login')
            password = header.get('password')
            uid = request.session.authenticate(db, login, password)
            if uid:
                if request.jsonrequest :
                    if rec.get('eartag_id'):
                        eartag = rec['eartag_id'].strip()  # Menghapus spasi ekstra jika ada
                        sapi = request.env['sapi'].sudo().search([('eartag_id', '=', eartag)])
                    else:
                        sapi = request.env['sapi'].sudo().search([])

                    data_sapi = []
                    for s in sapi:
                        if s.kembar == 'y' :
                            kembar = 'Ya'
                        elif s.kembar == 't' :
                            kembar = 'Tidak'
                        else :
                            kembar = None

                        if s.sex == 'm' :
                            sex = 'Male'
                        elif s.sex == 'f' :
                            sex = 'Female'
                        elif s.sex == 'o' :
                            sex = 'Other'
                        else :
                            sex = None

                        if s.status_aktif == 'a' :
                            status_aktif = 'Aktif'
                        elif s.status_aktif == 'ta' :
                            status_aktif = 'Tidak Aktif'
                        else :
                            status_aktif = None

                        if s.status_lahir == 'h' :
                            status_lahir = 'Hidup'
                        elif s.status_lahir == 'm' :
                            status_lahir = 'Mati'
                        else :
                            status_lahir = None




                        value = {   'id_sapi'             : s.id,
                                    'eartag_id'           : s.eartag_id or None,
                                    'kode_peternak'       : s.peternak_id.kode_peternak or None,
                                    'peternak_id'         : s.peternak_id.id or None,
                                    'peternak_name'       : s.peternak_id.peternak_name or None,
                                    'tps'                 : s.tps_id.tps_name or None,
                                    'nama_sapi'           : s.first_name or None,
                                    'kembar'              : kembar,
                                    'jenis_kelamin'       : sex,
                                    'metoda'              : s.metoda_id.nama_metoda or None,
                                    'date_of_birth'       : s.date_of_birth or None,
                                    'ayah_id'             : s.id_ayah.id or None,
                                    'ibu_id'              : s.id_induk.id or None,
                                    'tgl_identifikasi'    : s.tgl_identifikasi or None,
                                    'kode_kelahiran'      : s.kode_kelahiran or None,
                                    'id_breed'            : s.breed_id.id or None,
                                    'nama_breed'          : s.breed_id.nama_breed or None,
                                    'kandang_id'          : s.kandang_id.id or None,
                                    'nama_peternakan'     : s.kandang_id.nama_peternakan or None,
                                    'pemilik'             : s.kandang_id.peternak_id.peternak_name or None,
                                    'almt'                : s.kandang_id.almt or None,
                                    'status_aktif'        : status_aktif,
                                    'status_lahir'        : status_lahir,
                                    'posisi_eartag'       : s.posisi_eartag or None,
                                    'state'               : s.state or None,
                                    'bobot'               : s.bobot or None,
                                    'panjang'             : s.id or None,
                                    'tinggi'              : s.panjang or None,
                                    'lgkr_perut'          : s.lgkr_perut or None,
                                    'nama_kandang'        : s.kandang_id.nama_peternakan or None,
                                    'nama_metoda'         : s.metoda_id.nama_metoda or None
                                           
                                }
            
                        data_sapi.append(value)
                    return ({"message": "List Profil Sapi", "Data": data_sapi})
                else :
                    return ({'result':'Failed Check Your Parameter'})
        except Exception as e:
            return {'status': False, 'error': str(e)}


    @http.route('/load_profil_peternakan', auth="none", type='json',cors='*')
    def load_profil_peternakan(self, **rec):
        try:
            header = request.httprequest.headers
            db= header.get('db')
            login = header.get('login')
            password = header.get('password')
            uid = request.session.authenticate(db, login, password)
            if uid:
                if request.jsonrequest :
                    kandang = request.env['kandang.sapi.perah'].sudo().search([])
                    data_kandang = []
                    for s in kandang:
                        if s.status_kepemilikan == 'sendiri' :
                            status_milik = 'Milik Sendiri'
                        elif s.status_kepemilikan == 'terpisah' :
                            status_milik = 'Terpisah'
                        elif status_milik == 'Perusahaan' :
                            status_milik = 'Perusahaan'
                        else :
                            status_milik = None


                        value = {   'peternak_id'           : s.peternak_id.id,
                                    'kandang_id'            : s.id or None,
                                    'nama_peternakan'       : s.nama_peternakan or None,
                                    'almt'                  : s.almt or None,
                                    'provinsi_id'           : s.provinsi_id.id or None,
                                    'kabkota_id'            : s.kabkota_id.id or None,
                                    'kecamatan_id'          : s.kecamatan_id.id or None,
                                    'kelurahan_id'          : s.kelurahan_id.id or None,
                                    'peternak_name'         : s.peternak_id.peternak_name or None,
                                    'provinsi'              : s.provinsi_id.name or None,
                                    'kab_kota'              : s.kabkota_id.name or None,
                                    'kelurahan'             : s.kelurahan_id.name or None,
                                    'status_kepemilikan'    : status_milik
                                           
                                }

                        sapi_data = []    
                        if s.sapi_kandang_ids:
                            for sapi in s.sapi_kandang_ids :
                                sapi_data.append(
                                                    {
                                                    'sapi_id'   : sapi.id,
                                                    'nama_sapi' : sapi.first_name}
                                                )
                        value.update({'sapi':sapi_data})  
            
                        data_kandang.append(value)
                    return ({"message": "List Profil Peternakan", "Data": data_kandang})
                else :
                    return ({'result':'Failed Check Your Parameter'})
        except Exception as e:
            return {'status': False, 'error': str(e)}



    @http.route('/search_peternak', auth="none", type='json',cors='*')
    def search_peternak(self, **rec):
        try:
            if request.jsonrequest :
                if rec.get('kode_peternak'):
                    peternak = request.env['peternak.sapi'].sudo().search([('kode_peternak','=',rec.get('kode_peternak'))])
                    if peternak :
                        data_master = []
                        for m in peternak:
                            value = {   'id'                        : m.id,
                                        'name'                      : m.peternak_name or None,
                                        'kode_peternak'             : m.kode_peternak or None,
                                               
                                              }
                
                            data_master.append(value)
                        return ({"message": "List Peternak", "Data": data_master})
                    else :
                        return ({'result':'Peternak tidak ditemukan'})
                else :
                    return ({'result':'name is Empty'})

            else :
                return ({'result':'Failed Check Your Parameter'})
        except Exception as e:
            return {'status': False, 'error': str(e)}

