from odoo import api, fields, models, _

class master_vaksin(models.Model):
    _name = 'master.vaksin'
    _inherit = 'image.mixin'
    _rec_name = 'jns_vaksin'

    jns_vaksin = fields.Char('Jenis Vaksin')
    kode = fields.Integer('Kode')