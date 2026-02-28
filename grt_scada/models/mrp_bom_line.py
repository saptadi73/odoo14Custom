"""
MRP BoM line extensions for optional SCADA equipment mapping.
"""

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'

    scada_equipment_id = fields.Many2one(
        'scada.equipment',
        string='SCADA Equipment (Optional)',
        help='Optional equipment mapping for this component.'
    )

    @api.constrains('bom_id', 'product_id', 'scada_equipment_id')
    def _check_unique_silo_equipment_per_bom(self):
        """
        In one BoM, one equipment must map to only one material/product.
        Prevent accidental assignment of the same equipment to multiple materials.
        """
        for line in self:
            equipment = line.scada_equipment_id
            if not line.bom_id or not line.product_id or not equipment:
                continue

            conflict = line.bom_id.bom_line_ids.filtered(
                lambda other: (
                    other.id != line.id
                    and other.scada_equipment_id.id == equipment.id
                    and other.product_id.id != line.product_id.id
                )
            )[:1]
            if conflict:
                raise ValidationError(
                    "Equipment '%s' sudah dipakai oleh material '%s' pada BoM ini. "
                    "Satu equipment hanya boleh untuk satu bahan."
                    % (equipment.display_name, conflict.product_id.display_name)
                )
