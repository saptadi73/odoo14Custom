from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    customer_segment_id = fields.Many2one(
        "customer.behavior.segment",
        string="Customer Segment",
        ondelete="restrict",
        index=True,
    )
    behavior_business_category_id = fields.Many2one(
        "crm.business.category",
        string="Behavior Business Category",
        ondelete="restrict",
        index=True,
    )
    last_sale_date = fields.Date(string="Last Sale Date")
    behavior_currency_id = fields.Many2one(
        "res.currency",
        string="Behavior Currency",
        default=lambda self: self.env.company.currency_id.id,
        readonly=True,
    )
    total_sales_amount = fields.Monetary(string="Total Sales Amount", currency_field="behavior_currency_id")
    sales_frequency = fields.Integer(string="Sales Frequency")
    days_since_last_order = fields.Integer(string="Days Since Last Order")
    customer_behavior_analysis_ids = fields.One2many(
        "customer.behavior.analysis",
        "partner_id",
        string="Customer Behavior Analysis",
    )

    def action_recompute_customer_behavior(self):
        return {
            "type": "ir.actions.act_window",
            "name": "Recompute Customer Behavior",
            "res_model": "customer.behavior.recompute.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_mode": "selected",
                "default_partner_ids": [(6, 0, self.commercial_partner_id.ids)],
            },
        }
