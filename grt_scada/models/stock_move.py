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
                # Direct bom_line_id provided
                bom_line = self.env['mrp.bom.line'].browse(bom_line_id)
                if bom_line and bom_line.scada_equipment_id:
                    vals['scada_equipment_id'] = bom_line.scada_equipment_id.id
            elif vals.get('raw_material_production_id'):
                # Try to find bom_line through production order and product_id
                mo_id = vals.get('raw_material_production_id')
                product_id = vals.get('product_id')
                if mo_id and product_id:
                    mo = self.env['mrp.production'].browse(mo_id)
                    if mo and mo.bom_id:
                        # Find matching BoM line
                        matching_bom_lines = mo.bom_id.bom_line_ids.filtered(
                            lambda bl: bl.product_id.id == product_id
                        )
                        if matching_bom_lines:
                            bom_line = matching_bom_lines[0]
                            if bom_line.scada_equipment_id:
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
