from odoo import api, fields, models, _

class master_specimen_tes(models.Model):
    _name = 'master.specimen.tes'
    _rec_name = 'nama_specimen_tes'

    nama_specimen_tes = fields.Char('Specimen Tes')
    kode = fields.Integer('Kode')