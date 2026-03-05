from odoo import fields, models


class KpiTeam(models.Model):
    _name = "kpi.team"
    _description = "KPI Team"

    name = fields.Char(required=True, index=True)
    department_id = fields.Many2one("kpi.department", required=True, ondelete="restrict")
    member_ids = fields.One2many("kpi.team.member", "team_id", string="Members")

    _sql_constraints = [
        ("kpi_team_name_department_uniq", "unique(name, department_id)", "Team name must be unique per department."),
    ]


class KpiTeamMember(models.Model):
    _name = "kpi.team.member"
    _description = "KPI Team Member"

    team_id = fields.Many2one("kpi.team", required=True, ondelete="cascade", index=True)
    employee_id = fields.Many2one("hr.employee", required=True, ondelete="cascade", index=True)

    _sql_constraints = [
        ("kpi_team_member_uniq", "unique(team_id, employee_id)", "Employee already exists in this team."),
    ]

