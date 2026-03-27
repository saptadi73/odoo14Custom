from odoo import api, fields, models, _

class master_pejantan(models.Model):
    _name = 'master.pejantan'
    _rec_name = 'nama_pejantan'

    nama_pejantan = fields.Char('Pejantan')
    kode = fields.Integer('Kode')