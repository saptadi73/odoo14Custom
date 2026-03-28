from odoo import api, fields, models, _

class master_kategori_obat(models.Model):
    _name = 'master.kategori.obat'
    _rec_name = 'nama_kategori_obat'

    nama_kategori_obat = fields.Char('Kategori Obat')
    kode = fields.Integer('Kode')