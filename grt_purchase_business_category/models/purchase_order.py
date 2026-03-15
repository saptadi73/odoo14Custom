from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    business_category_id = fields.Many2one(
        "crm.business.category",
        string="Business Category",
        default=lambda self: self.env["business.category.mixin"]._default_business_category_id(),
        domain="[('company_id', '=', company_id)]",
        ondelete="restrict",
        tracking=True,
    )
    analytic_account_id = fields.Many2one(
        "account.analytic.account",
        string="Purchase Analytic Account",
        related="business_category_id.purchase_analytic_account_id",
        store=True,
        readonly=True,
    )
    purchase_team_id = fields.Many2one(
        "purchase.team",
        string="Purchase Team",
        domain="[('company_id', '=', company_id), ('business_category_id', '=', business_category_id)]",
        tracking=True,
    )

    def _is_purchase_admin_user(self):
        self.ensure_one()
        return self.env.user.has_group("purchase.group_purchase_manager") or self.env.user.has_group("base.group_system")

    @api.onchange("business_category_id")
    def _onchange_business_category_id(self):
        for order in self:
            if (
                order.purchase_team_id
                and order.purchase_team_id.business_category_id != order.business_category_id
            ):
                order.purchase_team_id = False

    @api.onchange("purchase_team_id")
    def _onchange_purchase_team_id(self):
        for order in self:
            if order.purchase_team_id and order.purchase_team_id.business_category_id:
                order.business_category_id = order.purchase_team_id.business_category_id

    @api.model_create_multi
    def create(self, vals_list):
        vals_list = [self._prepare_business_category_vals(vals) for vals in vals_list]
        return super().create(vals_list)

    def write(self, vals):
        vals = self._prepare_business_category_vals(vals)
        return super().write(vals)

    def _prepare_business_category_vals(self, vals):
        vals = dict(vals)
        if vals.get("purchase_team_id") and not vals.get("business_category_id"):
            team = self.env["purchase.team"].browse(vals["purchase_team_id"])
            if team.business_category_id:
                vals["business_category_id"] = team.business_category_id.id
        return vals

    @api.constrains("business_category_id", "purchase_team_id", "company_id", "analytic_account_id")
    def _check_business_category_team(self):
        for order in self:
            if order.business_category_id and order.business_category_id.company_id != order.company_id:
                raise ValidationError(
                    _("Purchase Order '%s' uses a Business Category from another company.") % order.name
                )
            if order.analytic_account_id and order.analytic_account_id.company_id != order.company_id:
                raise ValidationError(
                    _("Purchase Order '%s' uses an Analytic Account from another company.") % order.name
                )
            if not order.purchase_team_id:
                continue
            if order.purchase_team_id.company_id != order.company_id:
                raise ValidationError(
                    _("Purchase Team '%s' belongs to another company.") % order.purchase_team_id.name
                )
            if not order.purchase_team_id.business_category_id:
                raise ValidationError(
                    _("Purchase Team '%s' must have a Business Category before it can be used.")
                    % order.purchase_team_id.name
                )
            if (
                order.business_category_id
                and order.purchase_team_id.business_category_id != order.business_category_id
            ):
                raise ValidationError(
                    _(
                        "Purchase Team '%s' is linked to business category '%s'. "
                        "Please select a matching business category."
                    )
                    % (order.purchase_team_id.name, order.purchase_team_id.business_category_id.name)
                )

    @api.constrains("business_category_id", "purchase_team_id", "user_id")
    def _check_current_user_purchase_scope(self):
        current_user = self.env.user
        if current_user.has_group("base.group_system"):
            return

        effective_categories = current_user.effective_business_category_ids
        for order in self:
            if order.business_category_id and order.business_category_id not in effective_categories:
                raise ValidationError(
                    _("You can only use Purchase Orders in your registered Business Category.")
                )

            if order.purchase_team_id and current_user not in (order.purchase_team_id.user_id | order.purchase_team_id.member_ids):
                raise ValidationError(
                    _("You must be registered in the selected Purchase Team before using it on a Purchase Order.")
                )

    def button_confirm(self):
        for order in self:
            if order.state not in ("draft", "sent", "to approve"):
                continue
            if not order.business_category_id:
                raise ValidationError(
                    _("Purchase Order '%s' requires a Business Category before confirmation.") % order.name
                )
            if not order.purchase_team_id:
                raise ValidationError(
                    _("Purchase Order '%s' requires a Purchase Team before confirmation.") % order.name
                )
        return super().button_confirm()

    def _prepare_invoice(self):
        vals = super()._prepare_invoice()
        vals["purchase_business_category_id"] = self.business_category_id.id
        vals["purchase_analytic_account_id"] = self.analytic_account_id.id
        return vals


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.onchange("order_id")
    def _onchange_order_id_set_analytic(self):
        for line in self:
            if "account_analytic_id" in line._fields and line.order_id.analytic_account_id:
                line.account_analytic_id = line.order_id.analytic_account_id

    @api.onchange("product_id")
    def _onchange_product_id_set_analytic(self):
        for line in self:
            if "account_analytic_id" in line._fields and line.order_id.analytic_account_id:
                line.account_analytic_id = line.order_id.analytic_account_id

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("account_analytic_id") or not vals.get("order_id"):
                continue
            order = self.env["purchase.order"].browse(vals["order_id"])
            if order.analytic_account_id:
                vals["account_analytic_id"] = order.analytic_account_id.id
        return super().create(vals_list)

    def write(self, vals):
        vals = dict(vals)
        if "account_analytic_id" not in vals:
            analytic = self[:1].order_id.analytic_account_id
            if analytic:
                vals["account_analytic_id"] = analytic.id
        return super().write(vals)

    def _prepare_account_move_line(self, move=False):
        vals = super()._prepare_account_move_line(move=move)
        analytic = self.order_id.analytic_account_id
        if analytic and not vals.get("analytic_account_id"):
            vals["analytic_account_id"] = analytic.id
        return vals
