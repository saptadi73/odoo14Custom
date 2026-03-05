from odoo import fields, models


class KpiTarget(models.Model):
    _name = "kpi.target"
    _description = "KPI Target"

    kpi_definition_id = fields.Many2one("kpi.definition", required=True, ondelete="cascade", index=True)
    target_value = fields.Float(required=True, default=0.0)
    weight = fields.Float(required=True, default=0.0)
    history_ids = fields.One2many("kpi.target.history", "kpi_target_id", string="History")

    _sql_constraints = [
        ("kpi_target_definition_uniq", "unique(kpi_definition_id)", "Only one active target is allowed per KPI."),
    ]


class KpiTargetHistory(models.Model):
    _name = "kpi.target.history"
    _description = "KPI Target History"
    _order = "year desc, id desc"

    kpi_target_id = fields.Many2one("kpi.target", required=True, ondelete="cascade", index=True)
    year = fields.Integer(required=True, default=lambda self: fields.Date.today().year)
    target_value = fields.Float(required=True, default=0.0)

    _sql_constraints = [
        ("kpi_target_history_year_uniq", "unique(kpi_target_id, year)", "Target history year must be unique."),
    ]

