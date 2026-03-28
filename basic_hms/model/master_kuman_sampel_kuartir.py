from odoo import api, fields, models, _

class master_kuman_sampel_kuartir(models.Model):
    _name = 'master.kuman.sampel.kuartir'
    _rec_name = 'nama_kuman_sampel_kuartir'

    nama_kuman_sampel_kuartir = fields.Char('Kuman Sampel Kuartir')
    kode = fields.Integer('Kode')