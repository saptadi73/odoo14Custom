from odoo import api, fields, models, _

class master_semen_beku(models.Model):
    _name = 'master.semen.beku'
    _rec_name = 'nama_semen_beku'

    nama_semen_beku = fields.Char('Semen Beku')
    kode = fields.Char('Kode')