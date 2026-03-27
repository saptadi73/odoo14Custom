from odoo import api, fields, models, _

class master_posisi(models.Model):
    _name = 'master.posisi'
    _rec_name = 'nama_posisi'

    nama_posisi = fields.Char('Posisi')
    kode = fields.Integer('Kode')