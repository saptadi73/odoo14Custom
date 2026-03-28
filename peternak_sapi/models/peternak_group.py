from odoo import models, fields
class peternak_group(models.Model):
    _name = "peternak.group"
    _description = "Peternak Group"

    name = fields.Char('Group Peternak')

class jabatan_group(models.Model):
    _name = "jabatan.group"
    _rec_name = 'jabatan'
    _description = "Jabatan Group"

    jabatan = fields.Char('Nama Jabatan')
