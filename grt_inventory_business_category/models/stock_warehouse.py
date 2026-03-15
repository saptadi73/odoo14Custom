from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class StockWarehouse(models.Model):
    _inherit = "stock.warehouse"

    business_category_id = fields.Many2one(
        "crm.business.category",
        string="Business Category",
        default=lambda self: self.env["business.category.mixin"]._default_business_category_id(),
        ondelete="restrict",
        domain="[('company_id', '=', company_id)]",
    )
    stock_team_id = fields.Many2one(
        "stock.team",
        string="Inventory Team",
        domain="[('company_id', '=', company_id), ('business_category_id', '=', business_category_id)]",
    )

    @api.onchange("business_category_id")
    def _onchange_business_category_id_reset_stock_team(self):
        for warehouse in self:
            if warehouse.stock_team_id and warehouse.stock_team_id.business_category_id != warehouse.business_category_id:
                warehouse.stock_team_id = False

    @api.onchange("stock_team_id")
    def _onchange_stock_team_id(self):
        for warehouse in self:
            if warehouse.stock_team_id and warehouse.stock_team_id.business_category_id:
                warehouse.business_category_id = warehouse.stock_team_id.business_category_id

    @api.constrains("company_id", "business_category_id", "stock_team_id")
    def _check_business_category_team(self):
        for warehouse in self:
            if warehouse.business_category_id and warehouse.business_category_id.company_id != warehouse.company_id:
                raise ValidationError(
                    _("Warehouse '%s' uses a Business Category from another company.") % warehouse.name
                )
            if warehouse.stock_team_id:
                if warehouse.stock_team_id.company_id != warehouse.company_id:
                    raise ValidationError(
                        _("Inventory Team '%s' belongs to another company.") % warehouse.stock_team_id.name
                    )
                if warehouse.stock_team_id.business_category_id != warehouse.business_category_id:
                    raise ValidationError(
                        _(
                            "Inventory Team '%s' is linked to business category '%s'. "
                            "Please select a matching business category."
                        )
                        % (warehouse.stock_team_id.name, warehouse.stock_team_id.business_category_id.name)
                    )
