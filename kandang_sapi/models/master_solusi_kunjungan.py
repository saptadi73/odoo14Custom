from odoo import models, fields

class master_solusi_kunjungan(models.Model):
    _name = "master.solusi.kunjungan"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Master Solusi Kunjungan"
    _rec_name = 'solusi_kunjungan'

    solusi_kunjungan = fields.Char('Nama Solusi')
    kode = fields.Char('Kode')