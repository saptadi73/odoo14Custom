from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AccountPayment(models.Model):
    _inherit = "account.payment"

    business_category_id = fields.Many2one(
        "crm.business.category",
        string="Business Category",
        domain="[('company_id', '=', company_id)]",
        ondelete="restrict",
        copy=False,
    )
    analytic_account_id = fields.Many2one(
        "account.analytic.account",
        string="Analytic Account",
        domain="[('company_id', '=', company_id)]",
        ondelete="restrict",
        copy=False,
    )

    @api.onchange("business_category_id")
    def _onchange_business_category_id_analytic(self):
        for payment in self:
            payment.analytic_account_id = payment.business_category_id.analytic_account_id

    @api.constrains("company_id", "business_category_id", "analytic_account_id")
    def _check_business_category_analytic_company(self):
        for payment in self:
            if payment.business_category_id and payment.business_category_id.company_id != payment.company_id:
                raise ValidationError(
                    _("Payment '%s' uses a Business Category from another company.") % (payment.display_name,)
                )
            if payment.analytic_account_id and payment.analytic_account_id.company_id != payment.company_id:
                raise ValidationError(
                    _("Payment '%s' uses an Analytic Account from another company.") % (payment.display_name,)
                )
            if (
                payment.business_category_id
                and payment.business_category_id.analytic_account_id
                and payment.analytic_account_id
                and payment.business_category_id.analytic_account_id != payment.analytic_account_id
            ):
                raise ValidationError(
                    _(
                        "Payment '%s' must use the Analytic Account configured on its Business Category."
                    )
                    % (payment.display_name,)
                )

    def action_post(self):
        result = super().action_post()
        for payment in self:
            analytic = payment.analytic_account_id
            if not analytic or not payment.move_id:
                continue
            lines = payment.move_id.line_ids.filtered(
                lambda line: line.account_id.internal_type in ("receivable", "payable")
                and not line.analytic_account_id
            )
            if lines:
                lines.write({"analytic_account_id": analytic.id})
        return result
