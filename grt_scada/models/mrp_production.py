"""
MRP Production extensions for SCADA equipment defaults.
"""

from odoo import models, fields, api


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    scada_equipment_id = fields.Many2one(
        'scada.equipment',
        string='SCADA Equipment',
        help='Defaulted from BoM, can be changed per MO for operational needs.'
    )

    @api.onchange('bom_id')
    def _onchange_bom_id_scada_equipment(self):
        for record in self:
            if record.bom_id and not record.scada_equipment_id:
                record.scada_equipment_id = record.bom_id.scada_equipment_id

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('scada_equipment_id'):
                continue
            bom_id = vals.get('bom_id')
            if bom_id:
                bom = self.env['mrp.bom'].browse(bom_id)
                if bom and bom.scada_equipment_id:
                    vals['scada_equipment_id'] = bom.scada_equipment_id.id
        return super().create(vals_list)

    def button_mark_done(self):
        res = super().button_mark_done()
        oee_model = self.env['scada.equipment.oee']

        for mo in self:
            if mo.state != 'done':
                continue
            equipment = mo.scada_equipment_id or (mo.bom_id.scada_equipment_id if mo.bom_id else False)
            if not equipment:
                continue
            if oee_model.search([('manufacturing_order_id', '=', mo.id)], limit=1):
                continue
            vals = oee_model.prepare_from_mo(mo, equipment)
            oee_model.create(vals)

        return res
