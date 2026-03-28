from odoo import api, fields, models, _

class master_metoda(models.Model):
    _name = 'master.metoda'
    _rec_name = 'nama_metoda'

    nama_metoda = fields.Char('Metoda')
    kode = fields.Integer('Kode')