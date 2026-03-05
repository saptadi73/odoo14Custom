import calendar
from datetime import date

from odoo import api, fields, models


class KpiPeriod(models.Model):
    _name = "kpi.period"
    _description = "KPI Period"
    _order = "year desc, month desc, id desc"

    year = fields.Integer(required=True, default=lambda self: fields.Date.today().year)
    month = fields.Integer(required=True, default=lambda self: fields.Date.today().month)
    date_start = fields.Date(required=True)
    date_end = fields.Date(required=True)
    status = fields.Selection(
        [("draft", "Draft"), ("open", "Open"), ("closed", "Closed")],
        default="draft",
        required=True,
        index=True,
    )

    _sql_constraints = [
        ("kpi_period_month_check", "check(month >= 1 and month <= 12)", "Month must be between 1 and 12."),
        ("kpi_period_year_month_uniq", "unique(year, month)", "Period year-month must be unique."),
    ]

    @api.onchange("year", "month")
    def _onchange_year_month(self):
        for rec in self:
            if not rec.year or not rec.month or rec.month < 1 or rec.month > 12:
                continue
            last_day = calendar.monthrange(rec.year, rec.month)[1]
            rec.date_start = date(rec.year, rec.month, 1)
            rec.date_end = date(rec.year, rec.month, last_day)

