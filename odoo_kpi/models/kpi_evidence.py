from odoo import fields, models


class KpiEvidence(models.Model):
    _name = "kpi.evidence"
    _description = "KPI Evidence"
    _order = "id desc"

    kpi_value_id = fields.Many2one("kpi.value", required=True, ondelete="cascade", index=True)
    attachment = fields.Char(string="Attachment")
    note = fields.Text()

