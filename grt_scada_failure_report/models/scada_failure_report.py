from odoo import fields, models


class ScadaFailureReport(models.Model):
    _name = 'scada.failure.report'
    _description = 'SCADA Failure Report'
    _order = 'date desc, id desc'

    equipment_code = fields.Many2one(
        'scada.equipment',
        string='Equipment Code',
        required=True,
        ondelete='restrict',
    )
    description = fields.Text(string='Description', required=True)
    date = fields.Datetime(string='Date', required=True, default=fields.Datetime.now)
