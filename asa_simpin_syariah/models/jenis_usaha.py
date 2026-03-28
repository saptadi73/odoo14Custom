from odoo import models, fields, api

class usaha_anggota(models.Model):
    _name = "usaha.anggota"
    _description = "Usaha Anggota"
    _rec_name = 'jenis_usaha'

    usaha_name = fields.Char(string='Nama Usaha')
    jenis_usaha = fields.Selection([
        ('sapi', 'Sapi'),
        ('tebu', 'Tebu')
    ], 'Jenis Usaha', required=True, default=False)
