from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class CustomerBehaviorConfig(models.Model):
    _name = "customer.behavior.config"
    _description = "Customer Behavior Configuration"
    _order = "id desc"

    name = fields.Char(default="Default Configuration", required=True)
    repeat_days = fields.Integer(default=30, required=True)
    at_risk_days = fields.Integer(default=60, required=True)
    inactive_days = fields.Integer(default=90, required=True)
    dormant_days = fields.Integer(default=180, required=True)
    lost_days = fields.Integer(default=365, required=True)
    min_transaction = fields.Float(default=0.0, required=True)
    active = fields.Boolean(default=True)

    @api.constrains("repeat_days", "at_risk_days", "inactive_days", "dormant_days", "lost_days")
    def _check_day_thresholds(self):
        for rec in self:
            if not (
                rec.repeat_days <= rec.at_risk_days <= rec.inactive_days <= rec.dormant_days <= rec.lost_days
            ):
                raise ValidationError(
                    _(
                        "Threshold days must be ordered as Repeat <= At Risk <= Inactive <= Dormant <= Lost."
                    )
                )

    @api.model
    def get_active_config(self):
        return self.search([("active", "=", True)], order="id desc", limit=1) or self.create({})

    def action_run_analysis(self):
        self.ensure_one()
        self.env["customer.behavior.analysis"].sudo().compute_customer_behavior(config=self)
        return {"type": "ir.actions.client", "tag": "reload"}

    def action_open_recompute_wizard(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Recompute Customer Behavior",
            "res_model": "customer.behavior.recompute.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_mode": "all",
                "default_config_id": self.id,
            },
        }
