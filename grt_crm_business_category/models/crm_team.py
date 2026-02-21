from odoo import fields, models


class CrmTeam(models.Model):
    _inherit = "crm.team"

    business_category_id = fields.Many2one(
        "crm.business.category",
        string="Business Category",
        ondelete="restrict",
    )

