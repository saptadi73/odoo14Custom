# -*- coding: utf-8 -*-
# Author: BISPRO

from odoo import _, api, fields, models, SUPERUSER_ID
from odoo.exceptions import UserError, AccessError
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'

    customer = fields.Boolean(string='Is a Customer',
                              help="Check this box if this contact is a customer.")
    supplier = fields.Boolean(string='Is a Vendor',
                              help="Check this box if this contact is a vendor. "
                                   "If it's not checked, purchase people will not see it when encoding a purchase order.")



