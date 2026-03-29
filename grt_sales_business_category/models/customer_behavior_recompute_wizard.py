from odoo import api, fields, models


class CustomerBehaviorRecomputeWizard(models.TransientModel):
    _name = "customer.behavior.recompute.wizard"
    _description = "Customer Behavior Recompute Wizard"

    @api.model
    def _default_config_id(self):
        return self.env["customer.behavior.config"].get_active_config().id

    mode = fields.Selection(
        [
            ("selected", "Selected Customers"),
            ("all", "All Customers"),
        ],
        default="selected",
        required=True,
    )
    business_category_id = fields.Many2one(
        "crm.business.category",
        string="Business Category",
        related="config_id.business_category_id",
        readonly=True,
    )
    partner_ids = fields.Many2many("res.partner", string="Customers")
    config_id = fields.Many2one(
        "customer.behavior.config",
        string="Configuration",
        default=_default_config_id,
        domain=[("active", "=", True)],
        required=True,
    )

    def action_recompute(self):
        self.ensure_one()
        analysis_model = self.env["customer.behavior.analysis"]
        partners = self.partner_ids if self.mode == "selected" else self.env["res.partner"].search([("customer_rank", ">", 0)])
        analysis_model.compute_customer_behavior(config=self.config_id, partners=partners)
        return {
            "type": "ir.actions.act_window",
            "res_model": "customer.behavior.analysis",
            "view_mode": "tree,form,pivot,graph",
            "target": "current",
        }
