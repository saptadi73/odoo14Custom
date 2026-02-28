"""
Stock move extensions for optional SCADA equipment mapping.
"""

from odoo import models, fields, api
from odoo.exceptions import ValidationError


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

    @api.constrains('raw_material_production_id', 'product_id', 'scada_equipment_id', 'state')
    def _check_unique_silo_equipment_per_mo(self):
        """
        In one MO raw moves, one equipment must map to only one material/product.
        """
        for move in self:
            mo = move.raw_material_production_id
            equipment = move.scada_equipment_id
            if not mo or not move.product_id or not equipment:
                continue
            if move.state == 'cancel':
                continue

            conflict = mo.move_raw_ids.filtered(
                lambda other: (
                    other.id != move.id
                    and other.state != 'cancel'
                    and other.scada_equipment_id.id == equipment.id
                    and other.product_id.id != move.product_id.id
                )
            )[:1]
            if conflict:
                raise ValidationError(
                    "Equipment '%s' pada MO '%s' sudah dipakai oleh material '%s'. "
                    "Satu equipment hanya boleh untuk satu bahan."
                    % (equipment.display_name, mo.name, conflict.product_id.display_name)
                )
