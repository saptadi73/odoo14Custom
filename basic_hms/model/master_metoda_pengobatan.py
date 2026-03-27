from odoo import api, fields, models, _

class master_metoda_pengobatan(models.Model):
    _name = 'master.metoda.pengobatan'
    _rec_name = 'nama_metoda_pengobatan'

    nama_metoda_pengobatan = fields.Char('Metoda Pengobatan')
    kode = fields.Integer('Kode')