"""
SCADA Equipment Material Mapping
Store equipment-material consumption for OEE and analytics
"""

from odoo import models, fields


class ScadaEquipmentMaterial(models.Model):
    """Mapping/log for equipment and material consumption"""
    _name = 'scada.equipment.material'
    _description = 'SCADA Equipment Material Consumption'
    _order = 'timestamp desc, id desc'

    equipment_id = fields.Many2one(
        'scada.equipment',
        string='Equipment',
        required=True,
        ondelete='restrict'
    )
    product_id = fields.Many2one(
        'product.product',
        string='Product',
        required=True,
        ondelete='restrict'
    )
    manufacturing_order_id = fields.Many2one(
        'mrp.production',
        string='Manufacturing Order'
    )
    consumption_actual = fields.Float(
        string='Actual Consumption',
        required=True,
        digits=(12, 3)
    )
    consumption_bom = fields.Float(
        string='BoM Consumption',
        digits=(12, 3)
    )
    timestamp = fields.Datetime(
        string='Timestamp',
        default=fields.Datetime.now,
        required=True
    )
    active = fields.Boolean(
        string='Active',
        default=True
    )
