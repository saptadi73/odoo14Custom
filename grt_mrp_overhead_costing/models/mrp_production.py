from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    currency_id = fields.Many2one(
        "res.currency",
        related="company_id.currency_id",
        store=True,
        readonly=True,
    )
    overhead_allocation_line_ids = fields.One2many(
        "mrp.overhead.allocation.line",
        "production_id",
        string="Overhead Allocations",
        readonly=True,
    )
    overhead_electricity_factor = fields.Float(
        string="Electricity Factor",
        digits=(16, 4),
        default=1.0,
        help="Pengali basis overhead listrik untuk MO ini. 1.0 = normal, >1 lebih besar, <1 lebih kecil.",
    )
    overhead_labor_factor = fields.Float(
        string="Labor Factor",
        digits=(16, 4),
        default=1.0,
        help="Pengali basis overhead SDM untuk MO ini. 1.0 = normal, >1 lebih besar, <1 lebih kecil.",
    )
    overhead_applied_amount = fields.Monetary(
        string="Applied Overhead",
        compute="_compute_overhead_applied_amount",
        currency_field="currency_id",
    )
    overhead_applied_count = fields.Integer(
        string="Overhead Allocation Count",
        compute="_compute_overhead_applied_amount",
    )

    def _compute_overhead_applied_amount(self):
        for production in self:
            allocations = production.overhead_allocation_line_ids
            production.overhead_applied_amount = sum(allocations.mapped("applied_amount"))
            production.overhead_applied_count = len(allocations)

    @api.constrains("overhead_electricity_factor", "overhead_labor_factor")
    def _check_overhead_factors(self):
        for production in self:
            if production.overhead_electricity_factor < 0:
                raise ValidationError(_("Electricity Factor tidak boleh negatif."))
            if production.overhead_labor_factor < 0:
                raise ValidationError(_("Labor Factor tidak boleh negatif."))

    def _get_default_overhead_factors(self, product=None, bom=None):
        product = product or self.product_id
        bom = bom or self.bom_id
        template = product.product_tmpl_id if product else False
        electricity_factor = 1.0
        labor_factor = 1.0

        if template:
            electricity_factor = template.overhead_electricity_factor_default
            labor_factor = template.overhead_labor_factor_default

        if bom:
            electricity_factor = bom.overhead_electricity_factor_default
            labor_factor = bom.overhead_labor_factor_default

        return electricity_factor, labor_factor

    @api.onchange("product_id", "bom_id")
    def _onchange_apply_default_overhead_factors(self):
        for production in self:
            if not production.product_id:
                continue
            electricity_factor, labor_factor = production._get_default_overhead_factors()
            production.overhead_electricity_factor = electricity_factor
            production.overhead_labor_factor = labor_factor

    @api.model_create_multi
    def create(self, vals_list):
        Product = self.env["product.product"]
        Bom = self.env["mrp.bom"]
        for vals in vals_list:
            if "overhead_electricity_factor" in vals and "overhead_labor_factor" in vals:
                continue
            product = Product.browse(vals.get("product_id")) if vals.get("product_id") else False
            bom = Bom.browse(vals.get("bom_id")) if vals.get("bom_id") else False
            electricity_factor, labor_factor = self._get_default_overhead_factors(product=product, bom=bom)
            vals.setdefault("overhead_electricity_factor", electricity_factor)
            vals.setdefault("overhead_labor_factor", labor_factor)
        return super().create(vals_list)
