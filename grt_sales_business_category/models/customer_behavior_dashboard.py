from odoo import api, fields, models


class CustomerBehaviorDashboard(models.TransientModel):
    _name = "customer.behavior.dashboard"
    _description = "Customer Behavior Dashboard"

    analysis_date = fields.Date(default=fields.Date.context_today, readonly=True)
    total_customers = fields.Integer(readonly=True)
    repeat_customers = fields.Integer(readonly=True)
    reactivated_customers = fields.Integer(readonly=True)
    at_risk_customers = fields.Integer(readonly=True)
    inactive_customers = fields.Integer(readonly=True)
    dormant_customers = fields.Integer(readonly=True)
    lost_customers = fields.Integer(readonly=True)
    total_revenue = fields.Monetary(currency_field="currency_id", readonly=True)
    retention_rate = fields.Float(readonly=True, digits=(16, 2))
    churn_rate = fields.Float(readonly=True, digits=(16, 2))
    at_risk_rate = fields.Float(readonly=True, digits=(16, 2))
    currency_id = fields.Many2one(
        "res.currency",
        default=lambda self: self.env.company.currency_id.id,
        readonly=True,
    )

    @api.model
    def default_get(self, fields_list):
        vals = super().default_get(fields_list)
        analysis_date = vals.get("analysis_date") or fields.Date.context_today(self)
        analyses = self.env["customer.behavior.analysis"].search([("analysis_date", "=", analysis_date)])

        total_customers = len(analyses)
        segment_count = {
            "repeat": 0,
            "reactivated": 0,
            "at_risk": 0,
            "inactive": 0,
            "dormant": 0,
            "lost": 0,
        }
        for rec in analyses:
            if rec.segment_id.code in segment_count:
                segment_count[rec.segment_id.code] += 1

        retained = segment_count["repeat"] + segment_count["reactivated"]
        lost = segment_count["lost"]
        at_risk = segment_count["at_risk"]
        vals.update(
            {
                "total_customers": total_customers,
                "repeat_customers": segment_count["repeat"],
                "reactivated_customers": segment_count["reactivated"],
                "at_risk_customers": segment_count["at_risk"],
                "inactive_customers": segment_count["inactive"],
                "dormant_customers": segment_count["dormant"],
                "lost_customers": segment_count["lost"],
                "total_revenue": sum(analyses.mapped("total_amount")),
                "retention_rate": (retained / total_customers * 100.0) if total_customers else 0.0,
                "churn_rate": (lost / total_customers * 100.0) if total_customers else 0.0,
                "at_risk_rate": (at_risk / total_customers * 100.0) if total_customers else 0.0,
            }
        )
        return vals

    def _open_analysis(self, segment_codes=None):
        self.ensure_one()
        action = self.env.ref("grt_sales_business_category.action_customer_behavior_analysis").read()[0]
        domain = [("analysis_date", "=", self.analysis_date)]
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

