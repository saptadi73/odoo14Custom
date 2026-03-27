from odoo import models, fields

class master_jenis_pakan_tambah(models.Model):
    _name = "master.jenis.pakan.tambah"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Master Jenis Pakan Tambah"
    _rec_name = 'jenis_pakan_tambah'

    jenis_pakan_tambah = fields.Char('Jenis Pakan Tambah')
    bk = fields.Float('BK')
    tdn = fields.Float('TDN')