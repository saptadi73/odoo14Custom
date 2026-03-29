from odoo import api, fields, models


class CustomerBehaviorSegment(models.Model):
    _name = "customer.behavior.segment"
    _description = "Customer Behavior Segment"
    _order = "sequence, id"

    def init(self):
        # Hide orphan legacy rows that predate the config-based model design.
        self._cr.execute(
            """
            UPDATE customer_behavior_segment
               SET active = FALSE
             WHERE config_id IS NULL
               AND active IS TRUE
            """
        )

    name = fields.Char(required=True)
    config_id = fields.Many2one(
        "customer.behavior.config",
        string="Behavior Config",
        required=True,
        ondelete="cascade",
        index=True,
    )
    business_category_id = fields.Many2one(
        "crm.business.category",
        related="config_id.business_category_id",
        store=True,
        readonly=True,
        index=True,
    )
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
        (
            "customer_behavior_segment_code_config_uniq",
            "unique(code, config_id)",
            "Segment code must be unique per customer behavior config.",
        ),
    ]

    def name_get(self):
        result = []
        for rec in self:
            category_name = rec.business_category_id.name or "-"
            result.append((rec.id, "%s - %s" % (category_name, rec.name)))
        return result

    @api.model
    def name_search(self, name="", args=None, operator="ilike", limit=100):
        args = list(args or [])
        if name:
            domain = ["|", ("name", operator, name), ("business_category_id.name", operator, name)]
            records = self.search(domain + args, limit=limit)
            if records:
                return records.name_get()
        return super().name_search(name=name, args=args, operator=operator, limit=limit)
