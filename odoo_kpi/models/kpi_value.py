from odoo import fields, models


class KpiValue(models.Model):
    _name = "kpi.value"
    _description = "KPI Value"
    _order = "created_at desc, id desc"

    employee_id = fields.Many2one("hr.employee", required=True, ondelete="cascade", index=True)
    kpi_definition_id = fields.Many2one("kpi.definition", required=True, ondelete="cascade", index=True)
    period_id = fields.Many2one("kpi.period", required=True, ondelete="cascade", index=True)
    value = fields.Float(required=True, default=0.0)
    source_module = fields.Char(help="Example: crm, sale, stock, mrp, manual")
    created_at = fields.Datetime(default=fields.Datetime.now, required=True, readonly=True)

