from odoo import api, fields, models, _

class master_status_laktasi(models.Model):
    _name = 'master.status.laktasi'
    _rec_name = 'nama_status_laktasi'

    nama_status_laktasi = fields.Char('Status Laktasi')
    kode = fields.Integer('Kode')