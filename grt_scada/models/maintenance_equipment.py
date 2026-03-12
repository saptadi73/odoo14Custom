from odoo import api, fields, models


class MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'

    scada_equipment_id = fields.Many2one(
        'scada.equipment',
        string='SCADA Equipment',
        ondelete='restrict',
        index=True,
        copy=False,
    )
    scada_equipment_code = fields.Char(
        string='SCADA Code',
        related='scada_equipment_id.equipment_code',
        store=True,
        readonly=True,
    )
    scada_equipment_type = fields.Selection(
        related='scada_equipment_id.equipment_type',
        string='SCADA Type',
        store=True,
        readonly=True,
    )
    scada_connection_status = fields.Selection(
        related='scada_equipment_id.connection_status',
        string='SCADA Connection',
        readonly=True,
    )

    _sql_constraints = [
        (
            'maintenance_equipment_scada_unique',
            'unique(scada_equipment_id)',
            'Each SCADA equipment can only be linked to one maintenance equipment.',
        )
    ]

    @api.onchange('scada_equipment_id')
    def _onchange_scada_equipment_id(self):
        if self.scada_equipment_id:
            self._apply_scada_equipment_values(self.scada_equipment_id)

    def _apply_scada_equipment_values(self, scada_equipment):
        self.name = scada_equipment.name
        self.model = scada_equipment.model_number or False
        self.serial_no = scada_equipment.serial_number or False

