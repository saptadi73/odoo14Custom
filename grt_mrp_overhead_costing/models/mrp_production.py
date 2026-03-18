from odoo import fields, models


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
