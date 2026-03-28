from odoo import api, fields, models, _

class master_temuan_cervix(models.Model):
    _name = 'master.temuan.cervix'
    _rec_name = 'nama_temuan_cervix'

    nama_temuan_cervix = fields.Char('Temuan Cervix')
    kode = fields.Integer('Kode')