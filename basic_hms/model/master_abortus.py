from odoo import api, fields, models, _

class master_abortus(models.Model):
    _name = 'master.abortus'
    _rec_name = 'nama_abortus'

    nama_abortus = fields.Char('Abortus')
    kode = fields.Integer('Kode')