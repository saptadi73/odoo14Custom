from odoo import api, fields, models, _

class master_tipe_sapi(models.Model):
    _name = 'master.tipe.sapi'
    _rec_name = 'nama_tipe_sapi'

    nama_tipe_sapi = fields.Char('Tipe Sapi')
    kode = fields.Integer('Kode')