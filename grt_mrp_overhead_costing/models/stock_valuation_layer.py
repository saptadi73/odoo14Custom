from odoo import fields, models


class StockValuationLayer(models.Model):
    _inherit = "stock.valuation.layer"

    mrp_overhead_period_id = fields.Many2one(
        "mrp.overhead.period",
        string="MRP Overhead Period",
        copy=False,
        index=True,
    )
    mrp_overhead_period_line_id = fields.Many2one(
        "mrp.overhead.period.line",
        string="MRP Overhead Period Line",
        copy=False,
        index=True,
    )
    mrp_overhead_allocation_line_id = fields.Many2one(
        "mrp.overhead.allocation.line",
        string="MRP Overhead Allocation Line",
        copy=False,
        index=True,
    )
    mrp_production_id = fields.Many2one(
        "mrp.production",
        string="Manufacturing Order",
        copy=False,
        index=True,
    )
