from odoo import fields, models


class CrmBusinessCategory(models.Model):
    _inherit = "crm.business.category"

    inventory_analytic_account_id = fields.Many2one(
        "account.analytic.account",
        string="Inventory Analytic Account",
        related="analytic_account_id",
        readonly=False,
        help="Alias to the shared analytic account used for this business category.",
    )
