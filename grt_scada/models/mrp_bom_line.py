"""
MRP BoM line extensions for optional SCADA equipment mapping.
"""

from odoo import models, fields


class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'

    scada_equipment_id = fields.Many2one(
        'scada.equipment',
        string='SCADA Equipment (Optional)',
        help='Optional equipment mapping for this component.'
    )
