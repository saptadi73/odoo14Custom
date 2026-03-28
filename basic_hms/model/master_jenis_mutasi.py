from odoo import models, fields, api, _

class master_jenis_mutasi(models.Model):
    _name = 'master.jenis.mutasi'
    _rec_name = 'jenis_mutasi'

    jenis_mutasi = fields.Char('Jenis Mutasi')
    kode = fields.Char('Kode')
