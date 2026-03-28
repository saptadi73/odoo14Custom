from odoo import api, fields, models, _

class master_kasus_penyakit(models.Model):
    _name = 'master.kasus.penyakit'
    _rec_name = 'nama_kasus_penyakit'

    kategori_penyakit_id = fields.Many2one('master.kategori.penyakit', 'Kategori Penyakit')
    nama_kasus_penyakit = fields.Char('Kasus Penyakit')
    perbedaan_penyakit = fields.Selection([
        ('l', 'Penyakit'),
        ('p', 'Program'),
    ], 'Perbedaan Penyakit')
    kode = fields.Integer('Kode')