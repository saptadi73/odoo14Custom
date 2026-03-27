from odoo import models, fields, api

class usaha_peternak(models.Model):
    _name = "usaha.peternak"
    _description = "Peternak Sapi"
    _rec_name = 'usaha_name'

    usaha_name = fields.Char(string='Usaha')
