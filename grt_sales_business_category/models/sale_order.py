from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    sale_order_type = fields.Selection(
        [("kering", "Kering"), ("basah", "Basah")],
        string="Sale Order Type",
        tracking=True,
    )

    def _is_sales_admin_user(self):
        self.ensure_one()
        return self.env.user.has_group("sales_team.group_sale_manager") or self.env.user.has_group("base.group_system")

    business_category_id = fields.Many2one(
        "crm.business.category",
        string="Business Category",
        domain="[('company_id', '=', company_id)]",
        ondelete="restrict",
        tracking=True,
    )
    analytic_account_id = fields.Many2one(
        "account.analytic.account",
        string="Analytic Account",
        related="business_category_id.analytic_account_id",
        store=True,
        readonly=True,
    )
    team_id = fields.Many2one(
        "crm.team",
        string="Team Sales",
        domain="[('company_id', '=', company_id), ('business_category_id', '=', business_category_id)]",
        tracking=True,
    )
    sales_team_leader_id = fields.Many2one(
        "res.users",
        string="Sales Team Leader",
        related="team_id.sale_team_leader_id",
        store=True,
        readonly=True,
    )
    approval_state = fields.Selection(
        [
            ("draft", "Draft"),
            ("waiting_sales_leader", "Waiting Sales Team Leader"),
            ("waiting_accounting", "Waiting Accounting Manager"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
        ],
        string="Approval Status",
        default="draft",
        tracking=True,
        copy=False,
    )
    sales_leader_approved_by_id = fields.Many2one(
        "res.users",
        string="Sales Leader Approved By",
        readonly=True,
        copy=False,
    )
    sales_leader_approved_date = fields.Datetime(
        string="Sales Leader Approved On",
        readonly=True,
        copy=False,
    )
    accounting_approved_by_id = fields.Many2one(
        "res.users",
        string="Accounting Approved By",
        readonly=True,
        copy=False,
    )
    accounting_approved_date = fields.Datetime(
        string="Accounting Approved On",
        readonly=True,
        copy=False,
    )
    can_approve_sales_leader = fields.Boolean(compute="_compute_approval_permissions")
    can_approve_accounting = fields.Boolean(compute="_compute_approval_permissions")

    @api.depends("sales_team_leader_id")
    def _compute_approval_permissions(self):
        has_accounting_manager = self.env.user.has_group("account.group_account_manager")
        for order in self:
            order.can_approve_sales_leader = (
                order.sales_team_leader_id == self.env.user
                or self.env.user.has_group("sales_team.group_sale_manager")
            )
            order.can_approve_accounting = has_accounting_manager

    @api.onchange("opportunity_id")
    def _onchange_opportunity_id_business_category(self):
        for order in self:
            opportunity = order.opportunity_id
            if not opportunity:
                continue
            if opportunity.business_category_id:
                order.business_category_id = opportunity.business_category_id
            if opportunity.team_id:
                order.team_id = opportunity.team_id

    @api.onchange("business_category_id")
    def _onchange_business_category_id(self):
        for order in self:
            if order.team_id and order.team_id.business_category_id != order.business_category_id:
                order.team_id = False

    @api.onchange("team_id")
    def _onchange_team_id(self):
        for order in self:
            if order.team_id and order.team_id.business_category_id:
                order.business_category_id = order.team_id.business_category_id

    @api.model_create_multi
    def create(self, vals_list):
        orders = super().create([self._prepare_business_category_vals(vals) for vals in vals_list])
        return orders

    def write(self, vals):
        vals = self._prepare_business_category_vals(vals)
        return super().write(vals)

    def _prepare_business_category_vals(self, vals):
        vals = dict(vals)
        if vals.get("team_id") and not vals.get("business_category_id"):
            team = self.env["crm.team"].browse(vals["team_id"])
            if team.business_category_id:
                vals["business_category_id"] = team.business_category_id.id
        if vals.get("opportunity_id"):
            opportunity = self.env["crm.lead"].browse(vals["opportunity_id"])
            if opportunity.business_category_id and not vals.get("business_category_id"):
                vals["business_category_id"] = opportunity.business_category_id.id
            if opportunity.team_id and not vals.get("team_id"):
                vals["team_id"] = opportunity.team_id.id
        return vals

    def _prepare_invoice(self):
        vals = super()._prepare_invoice()
        vals["business_category_id"] = self.business_category_id.id
        vals["analytic_account_id"] = self.analytic_account_id.id
        return vals

    @api.constrains("sale_order_type")
    def _check_sale_order_type(self):
        allowed = {"kering", "basah"}
        for order in self:
            if order.sale_order_type and order.sale_order_type not in allowed:
                raise ValidationError(_("Sale Order Type must be either Kering or Basah."))

    @api.constrains("business_category_id", "team_id", "company_id", "analytic_account_id")
    def _check_business_category_team(self):
        for order in self:
            if order.business_category_id and order.business_category_id.company_id != order.company_id:
                raise ValidationError(
                    _("Sales Order '%s' uses a Business Category from another company.") % order.name
                )
            if order.analytic_account_id and order.analytic_account_id.company_id != order.company_id:
                raise ValidationError(
                    _("Sales Order '%s' uses an Analytic Account from another company.") % order.name
                )
            if not order.team_id:
                continue
            if not order.team_id.business_category_id:
                raise ValidationError(
                    _("Team Sales '%s' must have a Business Category before it can be used.")
                    % order.team_id.name
                )
            if (
                order.business_category_id
                and order.team_id.business_category_id != order.business_category_id
            ):
                raise ValidationError(
                    _(
                        "Team Sales '%s' is linked to business category '%s'. "
                        "Please select a matching business category."
                    )
                    % (order.team_id.name, order.team_id.business_category_id.name)
                )

    @api.constrains("opportunity_id", "business_category_id")
    def _check_opportunity_business_category(self):
        for order in self:
            if (
                order.opportunity_id
                and order.opportunity_id.business_category_id
                and order.business_category_id
                and order.opportunity_id.business_category_id != order.business_category_id
            ):
                raise ValidationError(
                    _("Sales Order business category must match the linked CRM opportunity.")
                )

    @api.constrains("business_category_id", "team_id", "user_id")
    def _check_current_user_sales_scope(self):
        current_user = self.env.user
        if current_user.has_group("base.group_system"):
            return

        effective_categories = current_user.effective_business_category_ids
        for order in self:
            if order.business_category_id and order.business_category_id not in effective_categories:
                raise ValidationError(
                    _("You can only use Sales Orders in your registered Business Category.")
                )

            if order.team_id:
                user_in_team = False
                if "user_id" in order.team_id._fields and order.team_id.user_id == current_user:
                    user_in_team = True
                if "member_ids" in order.team_id._fields and current_user in order.team_id.member_ids:
                    user_in_team = True
                if "team_members_ids" in order.team_id._fields and current_user in order.team_id.team_members_ids:
                    user_in_team = True

                if not user_in_team:
                    raise ValidationError(
                        _("You must be registered in the selected Team Sales before using it on a Sales Order.")
                    )

    def action_submit_for_approval(self):
        for order in self:
            if order.state not in ("draft", "sent"):
                raise UserError(_("Only draft quotations can be submitted for approval."))
            if not order.business_category_id:
                raise UserError(_("Business Category is required before submitting approval."))
            if not order.team_id:
                raise UserError(_("Team Sales is required before submitting approval."))
            if not order.sales_team_leader_id:
                raise UserError(_("Sales Team Leader must be set on the selected Team Sales."))
            order.write({"approval_state": "waiting_sales_leader"})
            order.message_post(body=_("Sales Order submitted for Sales Team Leader approval."))
        return True

    def action_sales_leader_approve(self):
        for order in self:
            if order.approval_state != "waiting_sales_leader":
                raise UserError(_("This Sales Order is not waiting for Sales Team Leader approval."))
            if not order.can_approve_sales_leader:
                raise UserError(_("Only the assigned Sales Team Leader can approve this Sales Order."))
            order.write(
                {
                    "approval_state": "waiting_accounting",
                    "sales_leader_approved_by_id": self.env.user.id,
                    "sales_leader_approved_date": fields.Datetime.now(),
                }
            )
            order.message_post(body=_("Approved by Sales Team Leader. Waiting for Accounting Manager approval."))
        return True

    def action_accounting_approve(self):
        for order in self:
            if order.approval_state != "waiting_accounting":
                raise UserError(_("This Sales Order is not waiting for Accounting Manager approval."))
            if not order.can_approve_accounting:
                raise UserError(_("Only an Accounting Manager can give the final approval."))
            order.write(
                {
                    "approval_state": "approved",
                    "accounting_approved_by_id": self.env.user.id,
                    "accounting_approved_date": fields.Datetime.now(),
                }
            )
            order.message_post(body=_("Approved by Accounting Manager. Sales Order confirmed."))
            super(SaleOrder, order).action_confirm()
        return True

    def action_reject_approval(self):
        for order in self:
            if order.approval_state not in ("waiting_sales_leader", "waiting_accounting"):
                raise UserError(_("Only Sales Orders in approval process can be rejected."))
            if not (order.can_approve_sales_leader or order.can_approve_accounting):
                raise UserError(_("You are not allowed to reject this Sales Order."))
            order.write({"approval_state": "rejected"})
            order.message_post(body=_("Sales Order approval has been rejected."))
        return True

    def action_reset_approval(self):
        for order in self:
            if order.state not in ("draft", "sent"):
                raise UserError(_("Only draft quotations can be reset."))
            order.write(
                {
                    "approval_state": "draft",
                    "sales_leader_approved_by_id": False,
                    "sales_leader_approved_date": False,
                    "accounting_approved_by_id": False,
                    "accounting_approved_date": False,
                }
            )
        return True

    def action_confirm(self):
        for order in self:
            if order.state not in ("draft", "sent"):
                continue
            if order.approval_state != "approved":
                raise UserError(
                    _(
                        "Sales Order '%s' requires two-step approval before it can be confirmed."
                    )
                    % order.name
                )
        return super().action_confirm()


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _prepare_invoice_line(self, **optional_values):
        vals = super()._prepare_invoice_line(**optional_values)
        analytic = self.order_id.analytic_account_id
        if analytic:
            vals["analytic_account_id"] = analytic.id
        return vals
