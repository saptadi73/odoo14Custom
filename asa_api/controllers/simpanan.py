from odoo import http, models
from odoo.http import request
import json
import logging

_logger = logging.getLogger(__name__)


class SimpanPinjam(http.Controller):

    @http.route('/select_simpanan', auth="none", type='json',cors='*')
    def select_simpanan(self, **rec):
        try:
            header = request.httprequest.headers
            db= header.get('db')
            login = header.get('login')
            password = header.get('password')
            uid = request.session.authenticate(db, login, password)
            if uid:
                if request.jsonrequest :
                    if rec.get('kode_peternak'):
                        peternak = request.env['peternak.sapi'].search([('kode_peternak','=',rec.get('kode_peternak'))])
                        member = request.env['simpin_syariah.member'].search([('peternak_id','=',peternak.id)])
                        if member :
                            simpanan_obj = request.env['form.simpanan'].search([('member_id','=',member.id)])
                            if simpanan_obj :
                                data_simpanan = []
                                for simpanan in simpanan_obj :
                                    value = {   'no_simpanan'      : simpanan.ref,
                                                'nama_anggota'     : simpanan.member_id.name,
                                                'customer'         : simpanan.partner_id.name,
                                                'jenis_simpanan'   : simpanan.product_id.name,
                                                'balance'          : simpanan.balance,
                                                'max_debit'        : simpanan.max_debit
                                                       
                                            }
                                    data_simpanan.append(value)
                                return ({"message": "Data Simpnan", "Data": data_simpanan})
                            else :
                                return ({'result':'Simpanan tidak ditemukan'})


                        else :
                            return ({'result':'Nama Anggota Tidak Ditemukan'})

                    else:
                        return ({'result':'user_id Failed Check Your Parameter'})

                else :
                    return ({'result':'Failed Check Your Parameter'})
        except Exception as e:
            return {'status': False, 'error': str(e)}


    @http.route('/select_pinjaman', auth="none", type='json',cors='*')
    def select_pinjaman(self, **rec):
        try:
            header = request.httprequest.headers
            db= header.get('db')
            login = header.get('login')
            password = header.get('password')
            uid = request.session.authenticate(db, login, password)
            if uid:
                if request.jsonrequest :
                    if rec.get('kode_peternak'):
                        peternak = request.env['peternak.sapi'].search([('kode_peternak','=',rec.get('kode_peternak'))])
                        member = request.env['simpin_syariah.member'].search([('peternak_id','=',peternak.id)])
                        if member :
                            pinjaman_obj = request.env['form.pinjaman'].search([('member_id','=',member.id)])
                            if pinjaman_obj :
                                data_pinjaman = []
                                for pinjaman in pinjaman_obj :
                                    value = {   'no_simpanan'      : pinjaman.ref,
                                                'nama_anggota'     : pinjaman.member_id.name,
                                                'customer'         : pinjaman.partner_id.name,
                                                'nama_pinjaman'    : pinjaman.nama_pinjaman,
                                                'note'             : pinjaman.notes,
                                                'tgl_pinjaman'     : pinjaman.tgl_pinjaman,
                                                'nilai_pinjaman'   : pinjaman.nilai_pinjaman,
                                                'periode_angsuran' : pinjaman.periode_angsuran,
                                                'angsuran'         : pinjaman.angsuran
                                                       
                                            }
                                    data_pinjaman.append(value)
                                return ({"message": "Data Pinjaman", "Data": data_pinjaman})
                            else :
                                return ({'result':'Pinjaman tidak ditemukan'})


                        else :
                            return ({'result':'Nama Anggota Tidak Ditemukan'})

                    else:
                        return ({'result':'user_id Failed Check Your Parameter'})

                else :
                    return ({'result':'Failed Check Your Parameter'})
        except Exception as e:
            return {'status': False, 'error': str(e)}
