from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    business_category_id = fields.Many2one(
        "crm.business.category",
        string="Business Category",
        default=lambda self: self._default_business_category_from_context(),
        domain="[('company_id', '=', company_id)]",
        ondelete="restrict",
        tracking=True,
    )
    stock_team_id = fields.Many2one(
        "stock.team",
        string="Inventory Team",
        domain="[('company_id', '=', company_id), ('business_category_id', '=', business_category_id)]",
        tracking=True,
    )
    inventory_analytic_account_id = fields.Many2one(
        "account.analytic.account",
        string="Inventory Analytic Account",
        related="business_category_id.inventory_analytic_account_id",
        store=True,
        readonly=True,
    )

    @api.model
    def _default_business_category_from_context(self):
        picking_type_id = self.env.context.get("default_picking_type_id")
        if picking_type_id:
            picking_type = self.env["stock.picking.type"].browse(picking_type_id)
            if picking_type.warehouse_id and picking_type.warehouse_id.business_category_id:
                return picking_type.warehouse_id.business_category_id.id
        return self.env["business.category.mixin"]._default_business_category_id()

    @api.onchange("business_category_id")
    def _onchange_business_category_id_reset_team(self):
        for picking in self:
            if picking.stock_team_id and picking.stock_team_id.business_category_id != picking.business_category_id:
                picking.stock_team_id = False

    @api.onchange("stock_team_id")
    def _onchange_stock_team_id(self):
        for picking in self:
            if picking.stock_team_id and picking.stock_team_id.business_category_id:
                picking.business_category_id = picking.stock_team_id.business_category_id

    @api.onchange("picking_type_id")
    def _onchange_picking_type_id_business_category(self):
        for picking in self:
            warehouse = picking.picking_type_id.warehouse_id
            if warehouse and warehouse.business_category_id:
                picking.business_category_id = warehouse.business_category_id
            if warehouse and warehouse.stock_team_id and not picking.stock_team_id:
                picking.stock_team_id = warehouse.stock_team_id

    @api.model_create_multi
    def create(self, vals_list):
        vals_list = [self._prepare_business_category_vals(vals) for vals in vals_list]
        return super().create(vals_list)

    def write(self, vals):
        vals = self._prepare_business_category_vals(vals)
        return super().write(vals)

    def _prepare_business_category_vals(self, vals):
        vals = dict(vals)
        if vals.get("stock_team_id") and not vals.get("business_category_id"):
            team = self.env["stock.team"].browse(vals["stock_team_id"])
            if team.business_category_id:
                vals["business_category_id"] = team.business_category_id.id
        if vals.get("picking_type_id") and not vals.get("business_category_id"):
            picking_type = self.env["stock.picking.type"].browse(vals["picking_type_id"])
            if picking_type.warehouse_id and picking_type.warehouse_id.business_category_id:
                vals["business_category_id"] = picking_type.warehouse_id.business_category_id.id
        return vals

    @api.constrains("business_category_id", "stock_team_id", "company_id")
    def _check_business_category_team(self):
        for picking in self:
            if picking.business_category_id and picking.business_category_id.company_id != picking.company_id:
                raise ValidationError(
                    _("Transfer '%s' uses a Business Category from another company.") % picking.name
                )
            if picking.stock_team_id:
                if picking.stock_team_id.company_id != picking.company_id:
                    raise ValidationError(
                        _("Inventory Team '%s' belongs to another company.") % picking.stock_team_id.name
                    )
                if picking.stock_team_id.business_category_id != picking.business_category_id:
                    raise ValidationError(
                        _(
                            "Inventory Team '%s' is linked to business category '%s'. "
                            "Please select a matching business category."
                        )
                        % (picking.stock_team_id.name, picking.stock_team_id.business_category_id.name)
                    )
            warehouse = picking.picking_type_id.warehouse_id
            if warehouse and warehouse.business_category_id and picking.business_category_id:
                if warehouse.business_category_id != picking.business_category_id:
                    raise ValidationError(
                        _("Transfer '%s' must use the same Business Category as its warehouse.") % picking.name
                    )

    @api.constrains("business_category_id", "stock_team_id")
    def _check_current_user_inventory_scope(self):
        current_user = self.env.user
        if current_user.has_group("base.group_system"):
            return

        effective_categories = current_user.effective_business_category_ids
        for picking in self:
            if picking.business_category_id and picking.business_category_id not in effective_categories:
                raise ValidationError(
                    _("You can only use Inventory Transfers in your registered Business Category.")
                )
            if picking.stock_team_id:
                team_users = picking.stock_team_id.user_id | picking.stock_team_id.member_ids
                if current_user not in team_users:
                    raise ValidationError(
                        _("You must be registered in the selected Inventory Team before using it on a Transfer.")
                    )

    def button_validate(self):
        for picking in self:
            if not picking.business_category_id:
                raise ValidationError(
                    _("Transfer '%s' requires a Business Category before validation.") % picking.name
                )
        return super().button_validate()


class StockMove(models.Model):
    _inherit = "stock.move"

    business_category_id = fields.Many2one(
        "crm.business.category",
        string="Business Category",
        related="picking_id.business_category_id",
        store=True,
        readonly=True,
    )
    stock_team_id = fields.Many2one(
        "stock.team",
        string="Inventory Team",
        related="picking_id.stock_team_id",
        store=True,
        readonly=True,
    )
    inventory_analytic_account_id = fields.Many2one(
        "account.analytic.account",
        string="Inventory Analytic Account",
        related="picking_id.inventory_analytic_account_id",
        store=True,
        readonly=True,
    )

    def _get_new_picking_values(self):
        vals = super()._get_new_picking_values()
        sale_order = self.sale_line_id.order_id if "sale_line_id" in self._fields else self.env["sale.order"]
        purchase_order = (
            self.purchase_line_id.order_id if "purchase_line_id" in self._fields else self.env["purchase.order"]
        )
        business_category = False
        if sale_order and sale_order.business_category_id:
            business_category = sale_order.business_category_id
        elif purchase_order and purchase_order.business_category_id:
            business_category = purchase_order.business_category_id
        elif self.picking_type_id.warehouse_id and self.picking_type_id.warehouse_id.business_category_id:
            business_category = self.picking_type_id.warehouse_id.business_category_id
        if business_category:
            vals["business_category_id"] = business_category.id
        warehouse = self.picking_type_id.warehouse_id
        if warehouse and warehouse.stock_team_id:
            vals.setdefault("stock_team_id", warehouse.stock_team_id.id)
        return vals

    def _prepare_account_move_line(self, qty, cost, credit_account_id, debit_account_id, description):
        res = super()._prepare_account_move_line(qty, cost, credit_account_id, debit_account_id, description)
        analytic = self.inventory_analytic_account_id
        if not analytic:
            return res
        for line_vals in res:
            if isinstance(line_vals, dict) and not line_vals.get("analytic_account_id"):
                line_vals["analytic_account_id"] = analytic.id
        return res
