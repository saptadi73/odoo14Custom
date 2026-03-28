from odoo import api, fields, models, _

class master_alasan_potkuku(models.Model):
    _name = 'master.alasan.potkuku'
    _rec_name = 'nama_alasan_potkuku'

    nama_alasan_potkuku = fields.Char('Alasan Potong Kuku')
    kode = fields.Integer('Kode')