from odoo import models, fields

class master_jenis_kunjungan(models.Model):
    _name = "master.jenis.kunjungan"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Master Kunjungan"
    _rec_name = 'jenis_kunjungan'

    jenis_kunjungan = fields.Char('Jenis Kunjungan')
    id_kunjungan = fields.Char('ID Kunjungan')