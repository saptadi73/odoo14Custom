from odoo import fields, models


class CrmBusinessCategory(models.Model):
    _name = "crm.business.category"
    _description = "CRM Business Category"
    _order = "name"

    name = fields.Char(required=True)
    code = fields.Char()
    active = fields.Boolean(default=True)
    description = fields.Text()

    _sql_constraints = [
        ("crm_business_category_name_uniq", "unique(name)", "Business category name must be unique."),
    ]

