from odoo import api, fields, models, _

class master_temuan_ovarium(models.Model):
    _name = 'master.temuan.ovarium'
    _rec_name = 'nama_temuan_ovarium'

    nama_temuan_ovarium = fields.Char('Temuan Ovarium')
    kode = fields.Integer('Kode')