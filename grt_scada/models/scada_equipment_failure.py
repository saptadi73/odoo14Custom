from odoo import fields, models


class ScadaEquipmentFailure(models.Model):
    _name = 'scada.equipment.failure'
    _description = 'SCADA Equipment Failure'
    _order = 'date desc, id desc'

    equipment_id = fields.Many2one(
        'scada.equipment',
        string='Equipment',
        required=True,
        ondelete='restrict',
    )
    equipment_code = fields.Char(
        string='Equipment Code',
        related='equipment_id.equipment_code',
        store=True,
        readonly=True,
    )
    description = fields.Text(string='Description', required=True)
    date = fields.Datetime(
        string='Date',
        required=True,
        default=fields.Datetime.now,
    )
    reported_by = fields.Many2one(
        'res.users',
        string='Reported By',
        default=lambda self: self.env.user,
        readonly=True,
    )
