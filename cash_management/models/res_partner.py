
from odoo import fields, models, api, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    customer = fields.Boolean('Is a Customer')
    supplier = fields.Boolean('Is a Vendor')

    @api.model
    def create(self, vals):
        if vals.get('vat'):
            emp = self.env['res.partner'].search([('vat', '=', vals['vat'])])
            if emp:
                raise ValidationError('A partner with the same VAT is already exist')
        return super(ResPartner, self).create(vals)

    def write(self, vals):
        if vals.get('vat'):
            emp = self.env['res.partner'].search([('vat', '=', vals['vat'])])
            if emp:
                raise ValidationError('A partner with the same VAT is already exist')
        return super(ResPartner, self).write(vals)