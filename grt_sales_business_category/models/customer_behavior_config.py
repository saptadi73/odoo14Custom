from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class CustomerBehaviorConfig(models.Model):
    _name = "customer.behavior.config"
    _description = "Customer Behavior Configuration"
    _order = "business_category_id, id desc"

    name = fields.Char(default="Default Configuration", required=True)
    business_category_id = fields.Many2one(
        "crm.business.category",
        string="Business Category",
        required=True,
        ondelete="restrict",
        index=True,
    )
    repeat_days = fields.Integer(default=30, required=True)
    at_risk_days = fields.Integer(default=60, required=True)
    inactive_days = fields.Integer(default=90, required=True)
    dormant_days = fields.Integer(default=180, required=True)
    lost_days = fields.Integer(default=365, required=True)
    min_transaction = fields.Float(default=0.0, required=True)
    active = fields.Boolean(default=True)

    def _get_accessible_business_categories(self):
        user = self.env.user
        if user.has_group("base.group_system"):
            return self.env["crm.business.category"].search(
                [("company_id", "in", user.company_ids.ids)]
            )
        return user.effective_business_category_ids.filtered(
            lambda category: category.company_id in user.company_ids
        )

    _sql_constraints = [
        (
            "customer_behavior_config_name_category_uniq",
            "unique(name, business_category_id)",
            "Configuration name must be unique per business category.",
        )
    ]

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

    @api.constrains("active", "business_category_id")
    def _check_active_config_per_business_category(self):
        for rec in self.filtered(lambda r: r.active and r.business_category_id):
            duplicates = self.search_count(
                [
                    ("id", "!=", rec.id),
                    ("active", "=", True),
                    ("business_category_id", "=", rec.business_category_id.id),
                ]
            )
            if duplicates:
                raise ValidationError(
                    _("Only one active customer behavior config is allowed per business category.")
                )

    @api.model
    def name_get(self):
        result = []
        for rec in self:
            category_name = rec.business_category_id.name or "-"
            result.append((rec.id, "%s - %s" % (category_name, rec.name)))
        return result

    @api.model
    def get_active_config(self, business_category=None):
        domain = [("active", "=", True)]
        if business_category:
            domain.append(("business_category_id", "=", business_category.id))
        else:
            accessible_categories = self._get_accessible_business_categories()
            if self.env.user.has_group("base.group_system"):
                pass
            elif accessible_categories:
                domain.append(("business_category_id", "in", accessible_categories.ids))
            else:
                domain.append(("id", "=", 0))
        return self.search(domain, order="id desc", limit=1)

    def action_run_analysis(self):
        self.ensure_one()
        self.env["customer.behavior.analysis"].compute_customer_behavior(config=self)
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
