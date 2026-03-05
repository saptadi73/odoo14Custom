from odoo import fields, models


class KpiDepartment(models.Model):
    _name = "kpi.department"
    _description = "KPI Department"

    name = fields.Char(required=True, index=True)
    description = fields.Text()
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ("kpi_department_name_uniq", "unique(name)", "Department name must be unique."),
    ]

