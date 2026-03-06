from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class KpiCustomerBehaviorTriggerRule(models.Model):
    _name = "kpi.customer.behavior.trigger.rule"
    _description = "KPI Customer Behavior Trigger Rule"
    _order = "sequence, id"

    name = fields.Char(required=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    business_category_id = fields.Many2one("crm.business.category", required=True, ondelete="cascade", index=True)
    line_ids = fields.One2many(
        "kpi.customer.behavior.trigger.rule.line",
        "rule_id",
        string="Trigger Lines",
    )

    def _find_employee_from_user(self, user):
        if not user:
            return self.env["hr.employee"]
        return self.env["hr.employee"].search([("user_id", "=", user.id)], limit=1)

    @api.model
    def _assignment_matches_date(self, assignment, event_date):
        period = assignment.period_id
        return bool(
            period
            and period.date_start
            and period.date_end
            and period.date_start <= event_date <= period.date_end
        )

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
    def _find_sales_employee_for_analysis(self, analysis):
        partner = analysis.partner_id.commercial_partner_id
        if partner.user_id:
            employee = self._find_employee_from_user(partner.user_id)
            if employee:
                return employee

        domain = [
            ("partner_id", "child_of", partner.id),
            ("state", "=", "sale"),
            ("user_id", "!=", False),
        ]
        if analysis.business_category_id:
            domain.append(("business_category_id", "=", analysis.business_category_id.id))
        last_order = self.env["sale.order"].sudo().search(domain, order="date_order desc, id desc", limit=1)
        return self._find_employee_from_user(last_order.user_id) if last_order else self.env["hr.employee"]

    @api.model
    def process_behavior_analyses(self, analyses):
        if not analyses:
            return False

        for analysis in analyses:
            if not analysis.segment_id or not analysis.business_category_id or not analysis.partner_id:
                continue

            event_date = analysis.analysis_date or fields.Date.context_today(self)
            employee = self._find_sales_employee_for_analysis(analysis)
            if not employee:
                continue

            rules = self.search(
                [
                    ("active", "=", True),
                    ("business_category_id", "=", analysis.business_category_id.id),
                ]
            )
            for rule in rules:
                lines = rule.line_ids.filtered(
                    lambda l: l.active
                    and l.employee_id.id == employee.id
                    and l.segment_id.id == analysis.segment_id.id
                    and self._assignment_matches_date(l.assignment_id, event_date)
                )
                for line in lines:
                    self._upsert_value(
                        line=line,
                        value=line.score_value,
                        ref_model="customer.behavior.analysis.rule.line.%s" % line.id,
                        ref_id=analysis.id,
                    )
        return True


class KpiCustomerBehaviorTriggerRuleLine(models.Model):
    _name = "kpi.customer.behavior.trigger.rule.line"
    _description = "KPI Customer Behavior Trigger Rule Line"
    _order = "sequence, id"

    rule_id = fields.Many2one("kpi.customer.behavior.trigger.rule", required=True, ondelete="cascade", index=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    segment_id = fields.Many2one("customer.behavior.segment", required=True, ondelete="restrict", index=True)
    employee_id = fields.Many2one("hr.employee", required=True, ondelete="cascade", index=True)
    assignment_id = fields.Many2one("kpi.assignment", required=True, ondelete="cascade", index=True)
    score_value = fields.Float(required=True, default=0.0)
    source_module = fields.Char(default="sale.customer_behavior", required=True)
    note = fields.Char()

    @api.constrains("employee_id", "assignment_id")
    def _check_assignment_employee(self):
        for rec in self:
            if rec.assignment_id.employee_id != rec.employee_id:
                raise ValidationError(_("Employee must match KPI Assignment employee."))
