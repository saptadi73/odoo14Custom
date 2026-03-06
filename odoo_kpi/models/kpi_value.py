from odoo import fields, models


class KpiValue(models.Model):
    _name = "kpi.value"
    _description = "KPI Value"
    _order = "created_at desc, id desc"

    assignment_id = fields.Many2one("kpi.assignment", required=True, ondelete="cascade", index=True)
    employee_id = fields.Many2one(
        "hr.employee",
        related="assignment_id.employee_id",
        store=True,
        readonly=True,
        index=True,
    )
    kpi_definition_id = fields.Many2one(
        "kpi.definition",
        related="assignment_id.kpi_definition_id",
        store=True,
        readonly=True,
        index=True,
    )
    period_id = fields.Many2one(
        "kpi.period",
        related="assignment_id.period_id",
        store=True,
        readonly=True,
        index=True,
    )
    value = fields.Float(required=True, default=0.0)
    source_module = fields.Char(help="Example: crm, sale, stock, mrp, manual")
    reference_model = fields.Char()
    reference_id = fields.Integer()
    created_at = fields.Datetime(default=fields.Datetime.now, required=True, readonly=True)
