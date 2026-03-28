from odoo import api, fields, models, _

class master_specimen(models.Model):
    _name = 'master.specimen'
    _rec_name = 'nama_specimen'

    nama_specimen = fields.Char('Specimen')
    kode = fields.Integer('Kode')