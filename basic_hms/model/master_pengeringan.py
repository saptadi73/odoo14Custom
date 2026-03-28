from odoo import api, fields, models, _

class master_pengeringan(models.Model):
    _name = 'master.pengeringan'
    _rec_name = 'nama_pengeringan'

    nama_pengeringan = fields.Char('Pengeringan')
    kode = fields.Integer('Kode')