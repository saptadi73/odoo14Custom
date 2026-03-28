from odoo import api, fields, models, _

class master_temuan_uterus(models.Model):
    _name = 'master.temuan.uterus'
    _rec_name = 'nama_temuan_uterus'

    nama_temuan_uterus = fields.Char('Temuan Uterus')
    kode = fields.Integer('Kode')