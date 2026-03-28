from odoo import http, models
from odoo.http import request
import json
import logging

_logger = logging.getLogger(__name__)


class ProfilAnggota(http.Controller):

    @http.route('/load_profil_petugas', auth="none", type='json',cors='*')
    def load_profil_petugas(self, **rec):
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
                            petugas = request.env['medical.physician'].search([('user_id','=',user.id)])
                            data_petugas = []
                            if petugas :
                                if rec.get('kode_peternak'):
                                    kandang = []
                                    peternak = request.env['peternak.sapi'].search([('kode_peternak','=',rec.get('kode_peternak'))])
                                    obj_kandang = request.env['kandang.sapi.perah'].search([('wilayah_id','=',petugas.wilayah_id.id),('peternak_id','=',peternak.id)])
                                    for k in obj_kandang :
                                        value = {   'nama_peternakan'      : k.nama_peternakan,
                                                    'kandang_id'           : k.id,
                                                    'alamat'               : k.almt
                                                }

                                        kandang.append(value)
                                else :
                                    kandang = []
                                    obj_kandang = request.env['kandang.sapi.perah'].search([('wilayah_id','=',petugas.wilayah_id.id)])
                                    for k in obj_kandang :
                                        value = {   'nama_peternakan'      : k.nama_peternakan,
                                                    'kandang_id'           : k.id,
                                                    'alamat'               : k.almt
                                                }

                                        kandang.append(value)




                                value = {   'user_id'          : user.id,
                                            'kode_petugas'     : petugas.kode_petugas,
                                            'nama_petugas'     : petugas.nama_petugas,
                                            'alias'            : petugas.alias,
                                            'gender'           : petugas.gender,
                                            'email'            : petugas.email,
                                            'no_hp'            : petugas.no_hp,
                                            'nama_jabatan'     : petugas.jabatan_id.nama_jabatan,
                                            'nama_supervisi'   : petugas.supervisi_id.nama_petugas,
                                            'nama_wilayah'     : petugas.wilayah_id.wilayah_id,
                                            'petugas_id'       : petugas.id,
                                            'list_kandang'     : kandang,
                                                   
                                        }
                                data_petugas.append(value)
                                return ({"message": "Profil Petugas", "Data": data_petugas})
                            else :
                                return ({'result':'Petugas tidak ditemukan'})


                        else :
                            return ({'result':'User tidak ditemukan'})

                    else:
                        return ({'result':'user_id Failed Check Your Parameter'})

                else :
                    return ({'result':'Failed Check Your Parameter'})
        except Exception as e:
            return {'status': False, 'error': str(e)}
