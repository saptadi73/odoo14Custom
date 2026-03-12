from odoo import api, fields, models


class ScadaEquipment(models.Model):
    _inherit = 'scada.equipment'

    maintenance_equipment_ids = fields.One2many(
        'maintenance.equipment',
        'scada_equipment_id',
        string='Maintenance Equipments',
    )
    maintenance_request_ids = fields.One2many(
        'maintenance.request',
        'scada_equipment_id',
        string='Maintenance Requests',
    )
    maintenance_equipment_count = fields.Integer(
        compute='_compute_maintenance_counts',
        string='Maintenance Equipment Count',
    )
    maintenance_request_count = fields.Integer(
        compute='_compute_maintenance_counts',
        string='Maintenance Request Count',
    )

    def _compute_maintenance_counts(self):
        for record in self:
            record.maintenance_equipment_count = len(record.maintenance_equipment_ids)
            record.maintenance_request_count = len(record.maintenance_request_ids)

    def _register_hook(self):
        result = super()._register_hook()
        if self._maintenance_bridge_column_ready():
            self.sudo().search([])._sync_to_maintenance_equipment()
        return result

    @api.model
    def _maintenance_bridge_column_ready(self):
        self.env.cr.execute(
            """
            SELECT 1
            FROM information_schema.columns
            WHERE table_name = 'maintenance_equipment'
              AND column_name = 'scada_equipment_id'
            """
        )
        return bool(self.env.cr.fetchone())

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._sync_to_maintenance_equipment()
        return records

    def write(self, vals):
        result = super().write(vals)
        if any(
            field in vals
            for field in ('name', 'model_number', 'serial_number', 'is_active')
        ):
            self._sync_to_maintenance_equipment()
        return result

    def _prepare_maintenance_equipment_vals(self):
        self.ensure_one()
        return {
            'name': self.name,
            'model': self.model_number or False,
            'serial_no': self.serial_number or False,
            'scada_equipment_id': self.id,
            'active': self.is_active,
        }

    def _sync_to_maintenance_equipment(self):
        if not self._maintenance_bridge_column_ready():
            return
        maintenance_equipment_model = self.env['maintenance.equipment']
        for record in self:
            maintenance_equipment = maintenance_equipment_model.search(
                [('scada_equipment_id', '=', record.id)],
                limit=1,
            )
            vals = record._prepare_maintenance_equipment_vals()
            if maintenance_equipment:
                maintenance_equipment.write(vals)
            else:
                maintenance_equipment_model.create(vals)

    def action_view_maintenance_equipment(self):
        self.ensure_one()
        action = self.env.ref('maintenance.hr_equipment_action').read()[0]
        action['domain'] = [('scada_equipment_id', '=', self.id)]
        action['context'] = {'default_scada_equipment_id': self.id}
        return action

    def action_view_maintenance_requests(self):
        self.ensure_one()
        action = self.env.ref('maintenance.maintenance_request_action').read()[0]
        action['domain'] = [('scada_equipment_id', '=', self.id)]
        action['context'] = {'default_scada_equipment_id': self.id}
        return action
