from odoo import api, fields, models, _

class master_tanda_kebuntingan(models.Model):
    _name = 'master.tanda.kebuntingan'
    _rec_name = 'nama_tanda_kebuntingan'

    nama_tanda_kebuntingan = fields.Char('Tandan Kebuntingan')
    kode = fields.Integer('Kode')