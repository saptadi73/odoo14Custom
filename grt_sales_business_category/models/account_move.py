from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = "account.move"

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
        for move in self:
            move.analytic_account_id = move.business_category_id.analytic_account_id

    @api.constrains("company_id", "business_category_id", "analytic_account_id")
    def _check_business_category_analytic_company(self):
        for move in self:
            if move.business_category_id and move.business_category_id.company_id != move.company_id:
                raise ValidationError(
                    _("Invoice '%s' uses a Business Category from another company.") % (move.display_name,)
                )
            if move.analytic_account_id and move.analytic_account_id.company_id != move.company_id:
                raise ValidationError(
                    _("Invoice '%s' uses an Analytic Account from another company.") % (move.display_name,)
                )
            if (
                move.business_category_id
                and move.business_category_id.analytic_account_id
                and move.analytic_account_id
                and move.business_category_id.analytic_account_id != move.analytic_account_id
            ):
                raise ValidationError(
                    _(
                        "Invoice '%s' must use the Analytic Account configured on its Business Category."
                    )
                    % (move.display_name,)
                )


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            analytic_id = vals.get("analytic_account_id")
            if analytic_id:
                continue
            move_id = vals.get("move_id")
            account_id = vals.get("account_id")
            if not move_id or not account_id:
                continue
            move = self.env["account.move"].browse(move_id)
            account = self.env["account.account"].browse(account_id)
            if (
                move
                and move.move_type in ("out_invoice", "out_refund", "in_invoice", "in_refund")
                and move.analytic_account_id
                and account
                and account.internal_type not in ("receivable", "payable")
            ):
                vals["analytic_account_id"] = move.analytic_account_id.id
        return super().create(vals_list)
