from odoo import api, fields, models


class KpiScore(models.Model):
    _name = "kpi.score"
    _description = "KPI Score"
    _order = "period_id desc, total_score desc, id desc"

    employee_id = fields.Many2one("hr.employee", required=True, ondelete="cascade", index=True)
    period_id = fields.Many2one("kpi.period", required=True, ondelete="cascade", index=True)
    total_score = fields.Float(default=0.0, required=True)
    grade = fields.Char()
    calculated_at = fields.Datetime()

    _sql_constraints = [
        ("kpi_score_uniq", "unique(employee_id, period_id)", "KPI score must be unique per employee and period."),
    ]

    @api.model
    def _grade_from_score(self, score):
        if score >= 90:
            return "A"
        if score >= 75:
            return "B"
        if score >= 60:
            return "C"
        if score >= 40:
            return "D"
        return "E"

    @api.model
    def calculate_kpi_score(self):
        assignment_model = self.env["kpi.assignment"]
        value_model = self.env["kpi.value"]
        period_model = self.env["kpi.period"]

        periods = period_model.search([("status", "in", ["open", "closed"])])
        now = fields.Datetime.now()
        for period in periods:
            assignments = assignment_model.search([("period_id", "=", period.id)])
            for employee in assignments.mapped("employee_id"):
                employee_assignments = assignments.filtered(lambda a: a.employee_id.id == employee.id)
                total = 0.0
                for assignment in employee_assignments:
                    target = assignment.effective_target or 0.0
                    weight = assignment.effective_weight or 0.0
                    if target <= 0 or weight <= 0:
                        continue
                    values = value_model.search(
                        [
                            ("employee_id", "=", employee.id),
                            ("period_id", "=", period.id),
                            ("kpi_definition_id", "=", assignment.kpi_definition_id.id),
                        ]
                    )
                    actual = sum(values.mapped("value"))
                    total += (actual / target) * weight

                vals = {
                    "employee_id": employee.id,
                    "period_id": period.id,
                    "total_score": total,
                    "grade": self._grade_from_score(total),
                    "calculated_at": now,
                }
                score = self.search(
                    [("employee_id", "=", employee.id), ("period_id", "=", period.id)],
                    limit=1,
                )
                if score:
                    score.write(vals)
                else:
                    self.create(vals)

        self.env["kpi.team.score"].calculate_team_score(periods.ids)
        return True


class KpiTeamScore(models.Model):
    _name = "kpi.team.score"
    _description = "KPI Team Score"
    _order = "period_id desc, score desc, id desc"

    team_id = fields.Many2one("kpi.team", required=True, ondelete="cascade", index=True)
    period_id = fields.Many2one("kpi.period", required=True, ondelete="cascade", index=True)
    score = fields.Float(default=0.0, required=True)
    calculated_at = fields.Datetime()

    _sql_constraints = [
        ("kpi_team_score_uniq", "unique(team_id, period_id)", "Team score must be unique per period."),
    ]

    @api.model
    def calculate_team_score(self, period_ids=None):
        score_model = self.env["kpi.score"]
        team_model = self.env["kpi.team"]
        period_model = self.env["kpi.period"]

        periods = period_model.browse(period_ids) if period_ids else period_model.search([("status", "in", ["open", "closed"])])
        now = fields.Datetime.now()
        for period in periods:
            for team in team_model.search([]):
                members = team.member_ids.mapped("employee_id")
                if not members:
                    value = 0.0
                else:
                    employee_scores = score_model.search(
                        [("period_id", "=", period.id), ("employee_id", "in", members.ids)]
                    )
                    value = (sum(employee_scores.mapped("total_score")) / len(employee_scores)) if employee_scores else 0.0

                vals = {
                    "team_id": team.id,
                    "period_id": period.id,
                    "score": value,
                    "calculated_at": now,
                }
                team_score = self.search([("team_id", "=", team.id), ("period_id", "=", period.id)], limit=1)
                if team_score:
                    team_score.write(vals)
                else:
                    self.create(vals)
        return True

