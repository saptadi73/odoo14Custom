from odoo import api, fields, models, _

class master_wilayah(models.Model):
    _name = 'master.wilayah'
    _rec_name = 'wilayah_id'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    kode = fields.Char('Kode Wilayah')
    wilayah_id = fields.Char('WIlayah')
