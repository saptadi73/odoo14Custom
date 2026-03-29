from odoo import api, fields, models


class CustomerBehaviorDashboard(models.TransientModel):
    _name = "customer.behavior.dashboard"
    _description = "Customer Behavior Dashboard"

    @api.model
    def _default_business_category_id(self):
        user = self.env.user
        accessible_categories = user.effective_business_category_ids.filtered(
            lambda category: category.company_id in user.company_ids
        )
        config = self.env["customer.behavior.config"].sudo().search(
            [
                ("active", "=", True),
                ("business_category_id", "in", accessible_categories.ids),
            ],
            order="id desc",
            limit=1,
        )
        if config and config.business_category_id:
            return config.business_category_id.id
        category = user.active_business_category_id or user.default_business_category_id
        if category and category in user.effective_business_category_ids:
            return category.id
        return user.effective_business_category_ids[:1].id

    analysis_date = fields.Date(default=fields.Date.context_today, readonly=True)
    business_category_id = fields.Many2one(
        "crm.business.category",
        string="Business Category",
        required=True,
        default=_default_business_category_id,
    )
    total_customers = fields.Integer(readonly=True, compute="_compute_metrics")
    repeat_customers = fields.Integer(readonly=True, compute="_compute_metrics")
    reactivated_customers = fields.Integer(readonly=True, compute="_compute_metrics")
    at_risk_customers = fields.Integer(readonly=True, compute="_compute_metrics")
    inactive_customers = fields.Integer(readonly=True, compute="_compute_metrics")
    dormant_customers = fields.Integer(readonly=True, compute="_compute_metrics")
    lost_customers = fields.Integer(readonly=True, compute="_compute_metrics")
    total_revenue = fields.Monetary(currency_field="currency_id", readonly=True, compute="_compute_metrics")
    retention_rate = fields.Float(readonly=True, digits=(16, 2), compute="_compute_metrics")
    churn_rate = fields.Float(readonly=True, digits=(16, 2), compute="_compute_metrics")
    at_risk_rate = fields.Float(readonly=True, digits=(16, 2), compute="_compute_metrics")
    currency_id = fields.Many2one(
        "res.currency",
        default=lambda self: self.env.company.currency_id.id,
        readonly=True,
    )

    @api.depends("analysis_date", "business_category_id")
    def _compute_metrics(self):
        for rec in self:
            domain = [("analysis_date", "=", rec.analysis_date)]
            if rec.business_category_id:
                domain.append(("business_category_id", "=", rec.business_category_id.id))
            analyses = self.env["customer.behavior.analysis"].search(domain)

            segment_count = {
                "repeat": 0,
                "reactivated": 0,
                "at_risk": 0,
                "inactive": 0,
                "dormant": 0,
                "lost": 0,
            }
            for analysis in analyses:
                if analysis.segment_id.code in segment_count:
                    segment_count[analysis.segment_id.code] += 1

            total_customers = len(analyses.mapped("partner_id"))
            retained = segment_count["repeat"] + segment_count["reactivated"]
            lost = segment_count["lost"]
            at_risk = segment_count["at_risk"] + segment_count["inactive"] + segment_count["dormant"]

            rec.total_customers = total_customers
            rec.repeat_customers = segment_count["repeat"]
            rec.reactivated_customers = segment_count["reactivated"]
            rec.at_risk_customers = segment_count["at_risk"]
            rec.inactive_customers = segment_count["inactive"]
            rec.dormant_customers = segment_count["dormant"]
            rec.lost_customers = segment_count["lost"]
            rec.total_revenue = sum(analyses.mapped("total_amount"))
            rec.retention_rate = (retained / total_customers * 100.0) if total_customers else 0.0
            rec.churn_rate = (lost / total_customers * 100.0) if total_customers else 0.0
            rec.at_risk_rate = (at_risk / total_customers * 100.0) if total_customers else 0.0

    def _open_analysis(self, segment_codes=None):
        self.ensure_one()
        action = self.env.ref("grt_sales_business_category.action_customer_behavior_analysis").read()[0]
        domain = [("analysis_date", "=", self.analysis_date)]
        if self.business_category_id:
            domain.append(("business_category_id", "=", self.business_category_id.id))
        if segment_codes:
            domain.append(("segment_id.code", "in", segment_codes))
        action["domain"] = domain
        return action

    def action_open_all_analysis(self):
        return self._open_analysis()

    def action_open_retained(self):
        return self._open_analysis(["repeat", "reactivated"])

    def action_open_churn(self):
        return self._open_analysis(["lost"])

    def action_open_at_risk(self):
        return self._open_analysis(["at_risk", "inactive", "dormant"])
