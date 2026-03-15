from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class CrmBusinessCategory(models.Model):
    _inherit = "crm.business.category"

    purchase_analytic_account_id = fields.Many2one(
        "account.analytic.account",
        string="Purchase Analytic Account",
        domain="[('company_id', '=', company_id)]",
        ondelete="restrict",
        help="Default analytic account used for purchasing transactions in this business category.",
    )

    @api.constrains("company_id", "purchase_analytic_account_id")
    def _check_purchase_analytic_account_company(self):
        for category in self:
            if not category.purchase_analytic_account_id or not category.company_id:
                continue
            if category.purchase_analytic_account_id.company_id != category.company_id:
                raise ValidationError(
                    _(
                        "Business Category '%s' must use a Purchase Analytic Account from company '%s'."
                    )
                    % (category.name, category.company_id.name)
                )
