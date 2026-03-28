from odoo import models, fields

class master_jenis_specimen(models.Model):
    _name = "master.jenis.specimen"
    _description = "Master Jenis Specimen"
    _rec_name = 'jenis_specimen'

    jenis_specimen = fields.Char(string='Jenis Specimen')
    id_specimen = fields.Char('ID Specimen')