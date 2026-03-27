from odoo import api, fields, models, _

class master_kode_kelahiran(models.Model):
    _name = 'master.kode.kelahiran'
    _rec_name = 'nama_kode_kelahiran'

    nama_kode_kelahiran = fields.Char('Kode Kelahiran')
    kode = fields.Integer('Kode')