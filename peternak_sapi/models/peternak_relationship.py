from odoo import models, fields

class peternak_relationship(models.Model):
    _name = "peternak.relationship"
    _description = "Peternak Relationship"

    name = fields.Char(string='Peternak Relationship')