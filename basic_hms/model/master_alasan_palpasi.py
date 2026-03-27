from odoo import api, fields, models, _

class master_alasan_palpasi(models.Model):
    _name = 'master.alasan.palpasi'
    _rec_name = 'nama_alasan_palpasi'

    nama_alasan_palpasi = fields.Char('Alasan Palpasi')
    kode = fields.Integer('Kode')