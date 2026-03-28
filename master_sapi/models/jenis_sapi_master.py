from odoo import models, fields

class jenis_sapi_master(models.Model):
    _name = "jenis.sapi.master"
    _description = "Jenis Sapi Master"
    _rec_name = 'jenis_sapi'

    jenis_sapi = fields.Char(string='Jenis Sapi')
    id_jenis_sapi = fields.Char('ID Jenis Sapi')
    keterangan = fields.Text('Keterangan')