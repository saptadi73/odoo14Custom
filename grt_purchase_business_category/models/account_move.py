from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = "account.move"

    purchase_business_category_id = fields.Many2one(
        "crm.business.category",
        string="Purchase Business Category",
        domain="[('company_id', '=', company_id)]",
        ondelete="restrict",
        copy=False,
    )
    purchase_analytic_account_id = fields.Many2one(
        "account.analytic.account",
        string="Purchase Analytic Account",
        domain="[('company_id', '=', company_id)]",
        ondelete="restrict",
        copy=False,
    )

    @api.onchange("purchase_business_category_id")
    def _onchange_purchase_business_category_id_analytic(self):
        for move in self:
            move.purchase_analytic_account_id = move.purchase_business_category_id.purchase_analytic_account_id

    @api.constrains("company_id", "purchase_business_category_id", "purchase_analytic_account_id")
    def _check_purchase_business_category_analytic_company(self):
        for move in self:
            if move.purchase_business_category_id and move.purchase_business_category_id.company_id != move.company_id:
                raise ValidationError(
                    _("Vendor Bill '%s' uses a Business Category from another company.") % (move.display_name,)
                )
            if move.purchase_analytic_account_id and move.purchase_analytic_account_id.company_id != move.company_id:
                raise ValidationError(
                    _("Vendor Bill '%s' uses an Analytic Account from another company.") % (move.display_name,)
                )
            if (
                move.purchase_business_category_id
                and move.purchase_business_category_id.purchase_analytic_account_id
                and move.purchase_analytic_account_id
                and move.purchase_business_category_id.purchase_analytic_account_id != move.purchase_analytic_account_id
            ):
                raise ValidationError(
                    _(
                        "Vendor Bill '%s' must use the Purchase Analytic Account configured on its Business Category."
                    )
                    % (move.display_name,)
                )

    def action_post(self):
        result = super().action_post()
        for move in self.filtered(lambda m: m.move_type in ("in_invoice", "in_refund")):
            analytic = move.purchase_analytic_account_id
            if not analytic:
                continue
            lines = move.line_ids.filtered(
                lambda line: line.account_id.internal_type not in ("receivable", "payable")
                and not line.analytic_account_id
            )
            if lines:
                lines.write({"analytic_account_id": analytic.id})
        return result


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("analytic_account_id"):
                continue
            move_id = vals.get("move_id")
            account_id = vals.get("account_id")
            if not move_id or not account_id:
                continue
            move = self.env["account.move"].browse(move_id)
            account = self.env["account.account"].browse(account_id)
            if (
                move
                and move.move_type in ("in_invoice", "in_refund")
                and move.purchase_analytic_account_id
                and account
                and account.internal_type not in ("receivable", "payable")
            ):
                vals["analytic_account_id"] = move.purchase_analytic_account_id.id
        return super().create(vals_list)
