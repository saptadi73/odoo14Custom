from odoo import models, fields, api
class periode_setoran(models.Model):
    _name = "periode.setoran"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Peridoe Setoran"
    _rec_name = 'periode_setoran'

    periode_setoran = fields.Char('Periode Setoran')
    periode_setoran_awal = fields.Date('Tanggal Awal')
    periode_setoran_akhir = fields.Date('Tanggal Akhir')