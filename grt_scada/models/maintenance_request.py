from odoo import fields, models


class MaintenanceRequest(models.Model):
    _inherit = 'maintenance.request'

    scada_equipment_id = fields.Many2one(
        'scada.equipment',
        related='equipment_id.scada_equipment_id',
        string='SCADA Equipment',
        store=True,
        readonly=True,
    )

