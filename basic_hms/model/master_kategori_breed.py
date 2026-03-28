from odoo import api, fields, models, _

class master_kategori_breed(models.Model):
    _name = 'master.kategori.breed'
    _rec_name = 'nama_kategori_breed'

    nama_kategori_breed = fields.Char('Kategori Breed')
    kode = fields.Integer('Kode')