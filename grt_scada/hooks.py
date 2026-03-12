from odoo import api, SUPERUSER_ID


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    scada_equipment_model = env['scada.equipment']
    if scada_equipment_model._maintenance_bridge_column_ready():
        scada_equipment_model.search([])._sync_to_maintenance_equipment()
