from odoo import api, fields, models, _

class master_status_kesehatan(models.Model):
    _name = 'master.status.kesehatan'
    _rec_name = 'nama_status_kesehatan'

    nama_status_kesehatan = fields.Char('Status Kesehatan')
    kode = fields.Integer('Kode')