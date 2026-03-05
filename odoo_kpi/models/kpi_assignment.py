from odoo import api, fields, models


class KpiAssignment(models.Model):
    _name = "kpi.assignment"
    _description = "KPI Assignment"
    _order = "period_id desc, employee_id, id"

    employee_id = fields.Many2one("hr.employee", required=True, ondelete="cascade", index=True)
    kpi_definition_id = fields.Many2one("kpi.definition", required=True, ondelete="cascade", index=True)
    period_id = fields.Many2one("kpi.period", required=True, ondelete="cascade", index=True)
    target_override = fields.Float()
    weight_override = fields.Float()
    effective_target = fields.Float(compute="_compute_effective_values", store=True)
    effective_weight = fields.Float(compute="_compute_effective_values", store=True)

    _sql_constraints = [
        (
            "kpi_assignment_uniq",
            "unique(employee_id, kpi_definition_id, period_id)",
            "Employee KPI assignment must be unique per period.",
        )
    ]

    @api.depends(
        "target_override",
        "weight_override",
        "kpi_definition_id",
        "kpi_definition_id.target_ids",
        "kpi_definition_id.target_ids.target_value",
        "kpi_definition_id.target_ids.weight",
    )
    def _compute_effective_values(self):
        for rec in self:
            target = rec.kpi_definition_id.target_ids[:1]
            rec.effective_target = rec.target_override if rec.target_override else (target.target_value or 0.0)
            rec.effective_weight = rec.weight_override if rec.weight_override else (target.weight or 0.0)

