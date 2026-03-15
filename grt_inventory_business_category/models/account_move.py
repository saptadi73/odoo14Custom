from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = "account.move"

    inventory_business_category_id = fields.Many2one(
        "crm.business.category",
        string="Inventory Business Category",
        domain="[('company_id', '=', company_id)]",
        ondelete="restrict",
        copy=False,
    )
    inventory_analytic_account_id = fields.Many2one(
        "account.analytic.account",
        string="Inventory Analytic Account",
        domain="[('company_id', '=', company_id)]",
        ondelete="restrict",
        copy=False,
    )

    @api.onchange("inventory_business_category_id")
    def _onchange_inventory_business_category_id_analytic(self):
        for move in self:
            move.inventory_analytic_account_id = move.inventory_business_category_id.inventory_analytic_account_id

    @api.model_create_multi
    def create(self, vals_list):
        vals_list = [self._prepare_inventory_business_category_vals(vals) for vals in vals_list]
        return super().create(vals_list)

    def write(self, vals):
        vals = self._prepare_inventory_business_category_vals(vals)
        return super().write(vals)

    def _prepare_inventory_business_category_vals(self, vals):
        vals = dict(vals)
        if vals.get("inventory_business_category_id") and not vals.get("inventory_analytic_account_id"):
            category = self.env["crm.business.category"].browse(vals["inventory_business_category_id"])
            if category.inventory_analytic_account_id:
                vals["inventory_analytic_account_id"] = category.inventory_analytic_account_id.id
        return vals

    @api.constrains("company_id", "inventory_business_category_id", "inventory_analytic_account_id")
    def _check_inventory_business_category_analytic_company(self):
        for move in self:
            if move.inventory_business_category_id and move.inventory_business_category_id.company_id != move.company_id:
                raise ValidationError(
                    _("Journal Entry '%s' uses an Inventory Business Category from another company.") % move.display_name
                )
            if move.inventory_analytic_account_id and move.inventory_analytic_account_id.company_id != move.company_id:
                raise ValidationError(
                    _("Journal Entry '%s' uses an Inventory Analytic Account from another company.") % move.display_name
                )
            if (
                move.inventory_business_category_id
                and move.inventory_business_category_id.inventory_analytic_account_id
                and move.inventory_analytic_account_id
                and move.inventory_business_category_id.inventory_analytic_account_id
                != move.inventory_analytic_account_id
            ):
                raise ValidationError(
                    _(
                        "Journal Entry '%s' must use the Inventory Analytic Account configured on its Business Category."
                    )
                    % move.display_name
                )


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
                and move.inventory_analytic_account_id
                and account
                and account.internal_type not in ("receivable", "payable")
            ):
                vals["analytic_account_id"] = move.inventory_analytic_account_id.id
        return super().create(vals_list)
