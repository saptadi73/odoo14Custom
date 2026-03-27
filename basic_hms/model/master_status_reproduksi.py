from odoo import api, fields, models, _

class master_status_reproduksi(models.Model):
    _name = 'master.status.reproduksi'
    _rec_name = 'nama_status_reproduksi'

    nama_status_reproduksi = fields.Char('Status Reproduksi')
    kode = fields.Integer('Kode')