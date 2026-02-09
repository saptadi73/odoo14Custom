"""
Stock move extensions for optional SCADA equipment mapping.
"""

from odoo import models, fields, api


class StockMove(models.Model):
    _inherit = 'stock.move'

    scada_equipment_id = fields.Many2one(
        'scada.equipment',
        string='SCADA Equipment (Optional)',
        help='Optional equipment mapping for this component move.'
    )

    @api.onchange('bom_line_id')
    def _onchange_bom_line_id_scada_equipment(self):
        for record in self:
            if record.bom_line_id and not record.scada_equipment_id:
                record.scada_equipment_id = record.bom_line_id.scada_equipment_id

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('scada_equipment_id'):
                continue
            bom_line_id = vals.get('bom_line_id')
            if bom_line_id:
                bom_line = self.env['mrp.bom.line'].browse(bom_line_id)
                if bom_line and bom_line.scada_equipment_id:
                    vals['scada_equipment_id'] = bom_line.scada_equipment_id.id
        return super().create(vals_list)
