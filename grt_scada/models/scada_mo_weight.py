"""
SCADA MO Weight
Track target vs actual weight for OEE
"""

from odoo import models, fields


class ScadaMoWeight(models.Model):
    """MO weight tracking for OEE"""
    _name = 'scada.mo.weight'
    _description = 'SCADA MO Weight'
    _order = 'timestamp desc, id desc'

    manufacturing_order_id = fields.Many2one(
        'mrp.production',
        string='Manufacturing Order',
        required=True,
        ondelete='restrict'
    )
    target_weight = fields.Float(
        string='Target Weight (kg)',
        required=True,
        digits=(12, 3)
    )
    weight_actual = fields.Float(
        string='Actual Weight (kg)',
        required=True,
        digits=(12, 3)
    )
    timestamp = fields.Datetime(
        string='Timestamp',
        default=fields.Datetime.now,
        required=True
    )
    notes = fields.Text(string='Notes')
