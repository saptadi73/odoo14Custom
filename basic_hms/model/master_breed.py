from odoo import api, fields, models, _

class master_breed(models.Model):
    _name = 'master.breed'
    _rec_name = 'nama_breed'

    kategori_breed_id = fields.Many2one('master.kategori.breed', 'Kategori Breed')
    nama_breed = fields.Char('Breed')
    kode = fields.Integer('Kode')