from odoo import fields, models


class CustomerBehaviorSegment(models.Model):
    _name = "customer.behavior.segment"
    _description = "Customer Behavior Segment"
    _order = "sequence, id"

    name = fields.Char(required=True)
    code = fields.Selection(
        [
            ("repeat", "Repeat"),
            ("at_risk", "At Risk"),
            ("inactive", "Inactive"),
            ("dormant", "Dormant"),
            ("lost", "Lost"),
            ("reactivated", "Reactivated"),
        ],
        required=True,
    )
    description = fields.Text()
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ("customer_behavior_segment_code_uniq", "unique(code)", "Segment code must be unique."),
    ]
