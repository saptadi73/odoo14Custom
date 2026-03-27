from odoo import api, fields, models, _

class master_obat(models.Model):
    _name = 'master.obat'
    _rec_name = 'nama_obat'

    kategori_obat_id = fields.Many2one('master.kategori.obat', 'Kategori Obat')
    nama_obat = fields.Char('Obat')
    kode = fields.Integer('Kode')