from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class CrmBusinessCategory(models.Model):
    _inherit = "crm.business.category"

    inventory_analytic_account_id = fields.Many2one(
        "account.analytic.account",
        string="Inventory Analytic Account",
        domain="[('company_id', '=', company_id)]",
        ondelete="restrict",
        help="Default analytic account used for stock valuation entries in this business category.",
    )

    @api.constrains("company_id", "inventory_analytic_account_id")
    def _check_inventory_analytic_account_company(self):
        for category in self:
            if not category.inventory_analytic_account_id or not category.company_id:
                continue
            if category.inventory_analytic_account_id.company_id != category.company_id:
                raise ValidationError(
                    _(
                        "Business Category '%s' must use an Inventory Analytic Account from company '%s'."
                    )
                    % (category.name, category.company_id.name)
                )
