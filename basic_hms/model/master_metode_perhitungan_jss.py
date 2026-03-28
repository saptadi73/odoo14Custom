from odoo import api, fields, models, _

class master_metode_perhitungan_jss(models.Model):
    _name = 'master.metode.perhitungan.jss'
    _rec_name = 'nama_metode_perhitungan_jss'

    nama_metode_perhitungan_jss = fields.Char('Metode Perhitungan JSS')
    kode = fields.Integer('Kode')