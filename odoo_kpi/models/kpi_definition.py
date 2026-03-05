from odoo import fields, models


class KpiDefinition(models.Model):
    _name = "kpi.definition"
    _description = "KPI Definition"

    code = fields.Char(required=True, index=True)
    name = fields.Char(required=True, index=True)
    department_id = fields.Many2one("kpi.department", required=True, ondelete="restrict")
    kpi_type = fields.Selection(
        [
            ("company", "Company"),
            ("department", "Department"),
            ("employee", "Employee"),
        ],
        default="employee",
        required=True,
    )
    description = fields.Text()
    calculation_method = fields.Selection(
        [("manual", "Manual"), ("auto", "Auto")],
        default="manual",
        required=True,
    )
    source_module = fields.Char(help="Example: crm, sale, stock, mrp")
    active = fields.Boolean(default=True)
    target_ids = fields.One2many("kpi.target", "kpi_definition_id", string="Target")

    _sql_constraints = [
        ("kpi_definition_code_uniq", "unique(code)", "KPI code must be unique."),
    ]

