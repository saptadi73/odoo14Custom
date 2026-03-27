from odoo import api, fields, models, _

class master_keadaan_melahirkan(models.Model):
    _name = 'master.keadaan.melahirkan'
    _rec_name = 'nama_keadaan_melahirkan'

    nama_keadaan_melahirkan = fields.Char('Keadaan Melahirkan')
    kode = fields.Integer('Kode')