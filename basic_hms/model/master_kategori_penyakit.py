from odoo import api, fields, models, _

class master_kategori_penyakit(models.Model):
    _name = 'master.kategori.penyakit'
    _rec_name = 'nama_kategori_penyakit'

    nama_kategori_penyakit = fields.Char('Kategori Penyakit')
    kode = fields.Integer('Kode')