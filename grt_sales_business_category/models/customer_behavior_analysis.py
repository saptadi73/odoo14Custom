from collections import defaultdict

from odoo import api, fields, models


class CustomerBehaviorAnalysis(models.Model):
    _name = "customer.behavior.analysis"
    _description = "Customer Behavior Analysis"
    _order = "analysis_date desc, total_amount desc, id desc"
    _rec_name = "partner_id"

    partner_id = fields.Many2one("res.partner", required=True, ondelete="cascade", index=True)
    segment_id = fields.Many2one("customer.behavior.segment", ondelete="restrict", index=True)
    business_category_id = fields.Many2one("crm.business.category", ondelete="restrict", index=True)
    company_id = fields.Many2one(
        "res.company",
        related="business_category_id.company_id",
        store=True,
        readonly=True,
        index=True,
    )
    currency_id = fields.Many2one(
        "res.currency",
        default=lambda self: self.env.company.currency_id.id,
        required=True,
        readonly=True,
    )
    last_purchase_date = fields.Date()
    previous_purchase_date = fields.Date()
    days_since_last_purchase = fields.Integer()
    total_orders = fields.Integer()
    total_amount = fields.Monetary(currency_field="currency_id")
    avg_order_value = fields.Monetary(currency_field="currency_id")
    analysis_date = fields.Date(required=True, default=fields.Date.context_today)

    _sql_constraints = [
        (
            "customer_behavior_analysis_partner_date_category_uniq",
            "unique(partner_id, analysis_date, business_category_id)",
            "Only one analysis per customer, business category, and date is allowed.",
        ),
    ]

    @api.model
    def _get_segment_by_code(self, code, config):
        if not config:
            return self.env["customer.behavior.segment"]
        return self.env["customer.behavior.segment"].search(
            [("code", "=", code), ("config_id", "=", config.id)],
            limit=1,
        )

    @api.model
    def _determine_segment_code(self, days_since_last_purchase, previous_gap_days, total_orders, config):
        if days_since_last_purchase is None:
            return False
        if days_since_last_purchase > config.lost_days:
            return "lost"
        if days_since_last_purchase > config.dormant_days:
            return "dormant"
        if days_since_last_purchase > config.inactive_days:
            return "inactive"
        if days_since_last_purchase > config.at_risk_days:
            return "at_risk"
        if total_orders > 1 and previous_gap_days and previous_gap_days > config.inactive_days:
            return "reactivated"
        return "repeat"

    @api.model
    def _reset_partner_behavior(self, partners, analysis_date, business_category=None):
        partners = partners.commercial_partner_id
        if not partners:
            return
        domain = [
            ("partner_id", "in", partners.ids),
            ("analysis_date", "=", analysis_date),
        ]
        if business_category:
            domain.append(("business_category_id", "=", business_category.id))
        self.sudo().search(domain).unlink()

    @api.model
    def _compute_customer_behavior_for_config(self, config, partners=None):
        if not config or not config.business_category_id:
            return True

        today = fields.Date.context_today(self)
        partner_filter_ids = partners.commercial_partner_id.ids if partners else []

        domain = [
            ("state", "=", "sale"),
            ("partner_id", "!=", False),
            ("amount_total", ">=", config.min_transaction),
            ("business_category_id", "=", config.business_category_id.id),
        ]
        if partner_filter_ids:
            domain.append(("partner_id", "child_of", partner_filter_ids))

        orders = self.env["sale.order"].sudo().search(domain, order="partner_id, date_order desc, id desc")

        orders_by_partner = defaultdict(list)
        for order in orders:
            orders_by_partner[order.partner_id.commercial_partner_id.id].append(order)

        if partners:
            commercial_partners = partners.commercial_partner_id
            self._reset_partner_behavior(commercial_partners, today, business_category=config.business_category_id)
            partners_to_process = commercial_partners.filtered(lambda p: p.id in orders_by_partner)
        else:
            partners_to_process = self.env["res.partner"].sudo().browse(list(orders_by_partner.keys()))
        analysis_model = self.sudo()

        for partner in partners_to_process:
            partner_orders = orders_by_partner.get(partner.id, [])
            if not partner_orders:
                continue

            last_order = partner_orders[0]
            last_purchase_date = fields.Date.to_date(last_order.date_order)
            previous_purchase_date = fields.Date.to_date(partner_orders[1].date_order) if len(partner_orders) > 1 else False
            days_since_last_purchase = (today - last_purchase_date).days if last_purchase_date else 0
            previous_gap_days = (
                (last_purchase_date - previous_purchase_date).days
                if last_purchase_date and previous_purchase_date
                else 0
            )
            total_orders = len(partner_orders)
            total_amount = sum(partner_orders.mapped("amount_total"))
            avg_order_value = total_amount / total_orders if total_orders else 0.0
            segment_code = self._determine_segment_code(
                days_since_last_purchase=days_since_last_purchase,
                previous_gap_days=previous_gap_days,
                total_orders=total_orders,
                config=config,
            )
            segment = self._get_segment_by_code(segment_code, config) if segment_code else False
            business_category = config.business_category_id

            existing = analysis_model.search(
                [
                    ("partner_id", "=", partner.id),
                    ("analysis_date", "=", today),
                    ("business_category_id", "=", business_category.id),
                ],
                limit=1,
            )
            vals = {
                "partner_id": partner.id,
                "segment_id": segment.id if segment else False,
                "business_category_id": business_category.id,
                "last_purchase_date": last_purchase_date,
                "previous_purchase_date": previous_purchase_date,
                "days_since_last_purchase": days_since_last_purchase,
                "total_orders": total_orders,
                "total_amount": total_amount,
                "avg_order_value": avg_order_value,
                "analysis_date": today,
            }
            if existing:
                existing.write(vals)
            else:
                analysis_model.create(vals)

            if not partner.behavior_business_category_id:
                partner.behavior_business_category_id = business_category.id
        return True

    @api.model
    def compute_customer_behavior(self, config=None, partners=None):
        if config:
            return self._compute_customer_behavior_for_config(config=config, partners=partners)

        configs = self.env["customer.behavior.config"].search(
            [("active", "=", True), ("business_category_id", "!=", False)]
        )
        for rec in configs:
            self._compute_customer_behavior_for_config(config=rec, partners=partners)
        return True
