from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class KpiSalesTriggerRule(models.Model):
    _name = "kpi.sales.trigger.rule"
    _description = "KPI Sales Trigger Rule"
    _order = "sequence, id"

    name = fields.Char(required=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    business_category_id = fields.Many2one("crm.business.category", required=True, ondelete="cascade", index=True)
    line_ids = fields.One2many("kpi.sales.trigger.rule.line", "rule_id", string="Trigger Lines")

    def _find_employee_from_user(self, user):
        if not user:
            return self.env["hr.employee"]
        return self.env["hr.employee"].search([("user_id", "=", user.id)], limit=1)

    @api.model
    def _assignment_matches_date(self, assignment, event_date):
        period = assignment.period_id
        return bool(period and period.date_start and period.date_end and period.date_start <= event_date <= period.date_end)

    @api.model
    def _calculate_line_score(self, line, order, late_days):
        score = line.on_time_score
        if late_days > 0:
            score -= late_days * line.late_penalty_per_day
        score = max(score, line.minimum_score)
        if line.transaction_amount_threshold and order.amount_total >= line.transaction_amount_threshold:
            score += line.transaction_bonus_score
        return score

    @api.model
    def _upsert_value(self, line, value, ref_model, ref_id):
        value_model = self.env["kpi.value"].sudo()
        existing = value_model.search(
            [
                ("assignment_id", "=", line.assignment_id.id),
                ("reference_model", "=", ref_model),
                ("reference_id", "=", ref_id),
                ("source_module", "=", line.source_module),
            ],
            limit=1,
        )
        vals = {
            "assignment_id": line.assignment_id.id,
            "value": value,
            "source_module": line.source_module,
            "reference_model": ref_model,
            "reference_id": ref_id,
        }
        if existing:
            existing.write({"value": value})
            return existing
        return value_model.create(vals)

    @api.model
    def process_paid_orders(self, orders):
        if not orders:
            return False

        for order in orders:
            if not order.business_category_id or not order.user_id or not order._is_kpi_sales_fully_paid():
                continue

            payment_date = order._get_kpi_sales_payment_completion_date()
            if not payment_date:
                continue

            employee = self._find_employee_from_user(order.user_id)
            if not employee:
                continue

            rules = self.search(
                [
                    ("active", "=", True),
                    ("business_category_id", "=", order.business_category_id.id),
                ]
            )
            late_days = order._get_kpi_sales_late_days(payment_date)
            for rule in rules:
                lines = rule.line_ids.filtered(
                    lambda l: l.active
                    and l.employee_id.id == employee.id
                    and self._assignment_matches_date(l.assignment_id, payment_date)
                )
                for line in lines:
                    score = self._calculate_line_score(line, order, late_days)
                    self._upsert_value(
                        line=line,
                        value=score,
                        ref_model="sale.order.payment.rule.line.%s" % line.id,
                        ref_id=order.id,
                    )
        return True


class KpiSalesTriggerRuleLine(models.Model):
    _name = "kpi.sales.trigger.rule.line"
    _description = "KPI Sales Trigger Rule Line"
    _order = "sequence, id"

    rule_id = fields.Many2one("kpi.sales.trigger.rule", required=True, ondelete="cascade", index=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    employee_id = fields.Many2one("hr.employee", required=True, ondelete="cascade", index=True)
    assignment_id = fields.Many2one("kpi.assignment", required=True, ondelete="cascade", index=True)
    on_time_score = fields.Float(required=True, default=1.0)
    late_penalty_per_day = fields.Float(default=0.0)
    minimum_score = fields.Float(default=0.0)
    transaction_amount_threshold = fields.Float(default=0.0)
    transaction_bonus_score = fields.Float(default=0.0)
    source_module = fields.Char(default="sale", required=True)
    note = fields.Char()

    @api.constrains("employee_id", "assignment_id")
    def _check_assignment_employee(self):
        for rec in self:
            if rec.assignment_id.employee_id != rec.employee_id:
                raise ValidationError(_("Employee must match KPI Assignment employee."))

    @api.constrains("on_time_score", "late_penalty_per_day", "minimum_score", "transaction_amount_threshold", "transaction_bonus_score")
    def _check_score_values(self):
        for rec in self:
            if rec.on_time_score < 0:
                raise ValidationError(_("On-time score must be zero or greater."))
            if rec.late_penalty_per_day < 0:
                raise ValidationError(_("Late penalty per day must be zero or greater."))
            if rec.minimum_score < 0:
                raise ValidationError(_("Minimum score must be zero or greater."))
            if rec.transaction_amount_threshold < 0:
                raise ValidationError(_("Transaction amount threshold must be zero or greater."))
            if rec.transaction_bonus_score < 0:
                raise ValidationError(_("Transaction bonus score must be zero or greater."))
