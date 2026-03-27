from odoo import http, models
from odoo.http import request
import json
import logging

_logger = logging.getLogger(__name__)


class ProfilAnggota(http.Controller):

    @http.route('/load_profil_anggota', auth="none", type='json',cors='*')
    def load_profil_anggota(self, **rec):
        try:
            header = request.httprequest.headers
            db= header.get('db')
            login = header.get('login')
            password = header.get('password')
            uid = request.session.authenticate(db, login, password)
            if uid:
                if request.jsonrequest :
                    if rec.get('user_id'):
                        user = request.env['res.users'].search([('id','=',rec.get('user_id'))])
                        if user :
                            peternak = request.env['peternak.sapi'].search([('partner_id','=',user.partner_id.id)])
                            data_peternak = []
                            if peternak :
                                kandang = []
                                for k in peternak.kandang_ids :
                                    value = {   'nama_peternakan'      : k.nama_peternakan,
                                                'kandang_id'           : k.id
                                            }

                                    kandang.append(value)
                                member = request.env['simpin_syariah.member'].search([('peternak_id','=',peternak.id)], limit=1)

                                value = {   'user_id'               : user.id,
                                            'peternak_id'           : peternak.id,
                                            'kode_peternak'         : peternak.kode_peternak,
                                            'partner_id'            : peternak.partner_id.id,
                                            'kode_anggota'          : member.kode_anggota,
                                            'peternak_name'         : peternak.peternak_name,
                                            'gender'                : peternak.gender,
                                            'phone'                 : peternak.phone,
                                            'jabatan_id'            : peternak.jabatan_id.id,
                                            'nama_jabatan'          : peternak.jabatan_id.jabatan,
                                            'wilayah_id'            : peternak.wilayah_id.id,
                                            'nama_wilayah'          : peternak.wilayah_id.wilayah_id,
                                            'contact_address'       : peternak.contact_address,
                                            'kandang'               : kandang,
                                            'kelompok_id'           : peternak.kelompok_id.id,
                                            'nama_kelompok'         : peternak.kelompok_id.name,
                                            'ka_id'                 : peternak.ka_id.id,
                                            'nama_ka'               : peternak.ka_id.peternak_name,
                                            'ko_id'                 : peternak.ko_id.id,
                                            'nama_ko'               : peternak.ko_id.peternak_name,
                                            'tipe_mitra'            : peternak.tipe_mitra
                                                   
                                        }
                                data_peternak.append(value)
                                return ({"message": "Profil Anggota", "Data": data_peternak})
                            else :
                                return ({'result':'Anggota tidak ditemukan'})


                        else :
                            return ({'result':'User tidak ditemukan'})

                    if rec.get('kode_peternak'):
                        peternak = request.env['peternak.sapi'].search([('kode_peternak','=',rec.get('kode_peternak'))])
                        data_peternak = []
                        if peternak :
                            kandang = []
                            for k in peternak.kandang_ids :
                                value = {   'nama_peternakan'      : k.nama_peternakan,
                                            'kandang_id'           : k.id
                                        }

                                kandang.append(value)

                            sapi = []
                            for s in peternak.list_sapi_ids :
                                value = {   'nama_sapi'            : s.first_name,
                                            'kandang'              : s.kandang_id.nama_peternakan,
                                            'id_eartag'            : s.eartag_id
                                        }

                                sapi.append(value)

                            member = request.env['simpin_syariah.member'].search([('peternak_id','=',peternak.id)], limit=1)
                            value = { 
                                        'peternak_id'           : peternak.id,
                                        'kode_peternak'         : peternak.kode_peternak,
                                        'partner_id'            : peternak.partner_id.id,
                                        'kode_anggota'          : member.kode_anggota,
                                        'peternak_name'         : peternak.peternak_name,
                                        'gender'                : peternak.gender,
                                        'phone'                 : peternak.phone,
                                        'jabatan_id'            : peternak.jabatan_id.id,
                                        'nama_jabatan'          : peternak.jabatan_id.jabatan,
                                        'wilayah_id'            : peternak.wilayah_id.id,
                                        'nama_wilayah'          : peternak.wilayah_id.wilayah_id,
                                        'contact_address'       : peternak.contact_address,
                                        'kelompok_id'           : peternak.kelompok_id.id,
                                        'nama_kelompok'         : peternak.kelompok_id.name,
                                        'ka_id'                 : peternak.ka_id.id,
                                        'nama_ka'               : peternak.ka_id.peternak_name,
                                        'ko_id'                 : peternak.ko_id.id,
                                        'nama_ko'               : peternak.ko_id.peternak_name,
                                        'tipe_mitra'            : peternak.tipe_mitra,
                                        'list_kandang'          : kandang,
                                        'list_sapi'             : sapi
                                               
                                    }
                            data_peternak.append(value)
                            return ({"message": "Profil Anggota", "Data": data_peternak})
                        else :
                            return ({'result':'Anggota tidak ditemukan'})

                    else:
                        return ({'result':'user_id Failed Check Your Parameter'})

                else :
                    return ({'result':'Failed Check Your Parameter'})
        except Exception as e:
            return {'status': False, 'error': str(e)}
