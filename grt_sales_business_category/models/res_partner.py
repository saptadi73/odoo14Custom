from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    customer_segment_id = fields.Many2one(
        "customer.behavior.segment",
        string="Customer Segment",
        ondelete="restrict",
        index=True,
        compute="_compute_behavior_summary",
    )
    behavior_business_category_id = fields.Many2one(
        "crm.business.category",
        string="Behavior Business Category",
        ondelete="restrict",
        index=True,
    )
    last_sale_date = fields.Date(string="Last Sale Date", compute="_compute_behavior_summary")
    behavior_currency_id = fields.Many2one(
        "res.currency",
        string="Behavior Currency",
        default=lambda self: self.env.company.currency_id.id,
        readonly=True,
    )
    total_sales_amount = fields.Monetary(
        string="Total Sales Amount",
        currency_field="behavior_currency_id",
        compute="_compute_behavior_summary",
    )
    sales_frequency = fields.Integer(string="Sales Frequency", compute="_compute_behavior_summary")
    days_since_last_order = fields.Integer(string="Days Since Last Order", compute="_compute_behavior_summary")
    customer_behavior_analysis_ids = fields.One2many(
        "customer.behavior.analysis",
        "partner_id",
        string="Customer Behavior Analysis",
    )

    def _get_behavior_reference_analysis(self):
        self.ensure_one()
        analyses = self.customer_behavior_analysis_ids
        if self.behavior_business_category_id:
            analyses = analyses.filtered(
                lambda rec: rec.business_category_id == self.behavior_business_category_id
            )
        return analyses.sorted(
            key=lambda rec: (
                rec.analysis_date or fields.Date.from_string("1900-01-01"),
                rec.id,
            ),
            reverse=True,
        )[:1]

    def _compute_behavior_summary(self):
        for partner in self:
            analysis = partner._get_behavior_reference_analysis()
            partner.customer_segment_id = analysis.segment_id if analysis else False
            partner.last_sale_date = analysis.last_purchase_date if analysis else False
            partner.total_sales_amount = analysis.total_amount if analysis else 0.0
            partner.sales_frequency = analysis.total_orders if analysis else 0
            partner.days_since_last_order = analysis.days_since_last_purchase if analysis else 0

    def _ensure_behavior_business_category(self):
        for partner in self.filtered(lambda p: not p.behavior_business_category_id and p.customer_behavior_analysis_ids):
            latest = partner.customer_behavior_analysis_ids.sorted(
                key=lambda rec: (
                    rec.analysis_date or fields.Date.from_string("1900-01-01"),
                    rec.id,
                ),
                reverse=True,
            )[:1]
            if latest:
                partner.behavior_business_category_id = latest.business_category_id

    def write(self, vals):
        result = super().write(vals)
        if "customer_behavior_analysis_ids" in vals or "behavior_business_category_id" not in vals:
            self._ensure_behavior_business_category()
        return result

    def action_recompute_customer_behavior(self):
        self._ensure_behavior_business_category()
        config = self.env["customer.behavior.config"].sudo().get_active_config(self.behavior_business_category_id)
        return {
            "type": "ir.actions.act_window",
            "name": "Recompute Customer Behavior",
            "res_model": "customer.behavior.recompute.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_mode": "selected",
                "default_partner_ids": [(6, 0, self.commercial_partner_id.ids)],
                "default_config_id": config.id,
            },
        }
