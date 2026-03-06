from odoo import api, models


class CustomerBehaviorAnalysis(models.Model):
    _inherit = "customer.behavior.analysis"

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        self.env["kpi.customer.behavior.trigger.rule"].sudo().process_behavior_analyses(records)
        return records

    def write(self, vals):
        result = super().write(vals)
        trigger_fields = {"segment_id", "business_category_id", "partner_id", "analysis_date"}
        if trigger_fields.intersection(vals):
            self.env["kpi.customer.behavior.trigger.rule"].sudo().process_behavior_analyses(self)
        return result
