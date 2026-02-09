"""
MRP BoM extensions for SCADA defaults.
"""

from odoo import models, fields


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    scada_equipment_id = fields.Many2one(
        'scada.equipment',
        string='Default SCADA Equipment',
        help='Default equipment to prefill on MO created from this BoM.'
    )
