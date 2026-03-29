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
    value_ids = fields.One2many("kpi.value", "assignment_id", string="KPI Values")

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
        "period_id",
        "period_id.year",
        "kpi_definition_id",
        "kpi_definition_id.target_ids",
        "kpi_definition_id.target_ids.target_value",
        "kpi_definition_id.target_ids.weight",
        "kpi_definition_id.target_ids.history_ids",
        "kpi_definition_id.target_ids.history_ids.year",
        "kpi_definition_id.target_ids.history_ids.target_value",
    )
    def _compute_effective_values(self):
        for rec in self:
            target = rec.kpi_definition_id.target_ids[:1]
            historical_target = 0.0
            if target and rec.period_id and rec.period_id.year:
                history = target.history_ids.filtered(lambda h: h.year == rec.period_id.year)[:1]
                historical_target = history.target_value or 0.0
            base_target = historical_target or target.target_value or 0.0
            rec.effective_target = rec.target_override if rec.target_override else base_target
            rec.effective_weight = rec.weight_override if rec.weight_override else (target.weight or 0.0)

    def name_get(self):
        result = []
        for rec in self:
            employee_name = rec.employee_id.name or "-"
            kpi_name = rec.kpi_definition_id.name or "-"
            period_name = rec.period_id.name or "-"
            result.append((rec.id, "%s - %s - %s" % (employee_name, kpi_name, period_name)))
        return result

    @api.model
    def name_search(self, name="", args=None, operator="ilike", limit=100):
        args = list(args or [])
        if name:
            domain = [
                "|",
                "|",
                ("employee_id.name", operator, name),
                ("kpi_definition_id.name", operator, name),
                ("period_id.name", operator, name),
            ]
            records = self.search(domain + args, limit=limit)
            if records:
                return records.name_get()
        return super().name_search(name=name, args=args, operator=operator, limit=limit)
