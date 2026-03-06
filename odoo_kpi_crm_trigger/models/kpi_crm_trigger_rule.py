from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class KpiCrmTriggerRule(models.Model):
    _name = "kpi.crm.trigger.rule"
    _description = "KPI CRM Trigger Rule"
    _order = "sequence, id"

    name = fields.Char(required=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    business_category_id = fields.Many2one("crm.business.category", required=True, ondelete="cascade", index=True)
    line_ids = fields.One2many("kpi.crm.trigger.rule.line", "rule_id", string="Trigger Lines")

    def _find_employee_from_user(self, user):
        if not user:
            return self.env["hr.employee"]
        return self.env["hr.employee"].search([("user_id", "=", user.id)], limit=1)

    @api.model
    def _assignment_matches_date(self, assignment, event_date):
        period = assignment.period_id
        return bool(period and period.date_start and period.date_end and period.date_start <= event_date <= period.date_end)

    @api.model
    def _create_value_if_missing(self, line, value, ref_model, ref_id):
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
        if existing:
            return existing
        return value_model.create(
            {
                "assignment_id": line.assignment_id.id,
                "value": value,
                "source_module": line.source_module,
                "reference_model": ref_model,
                "reference_id": ref_id,
            }
        )

    @api.model
    def process_lead_stage_change(self, leads, previous_stage_map=None):
        if not leads:
            return False

        event_date = fields.Date.today()
        for lead in leads:
            if not lead.business_category_id or not lead.stage_id:
                continue
            if previous_stage_map and previous_stage_map.get(lead.id) == lead.stage_id.id:
                continue

            employee = self._find_employee_from_user(lead.user_id)
            if not employee:
                continue

            rules = self.search(
                [
                    ("active", "=", True),
                    ("business_category_id", "=", lead.business_category_id.id),
                ]
            )
            for rule in rules:
                lines = rule.line_ids.filtered(
                    lambda l: l.active
                    and l.employee_id.id == employee.id
                    and l.stage_id.id == lead.stage_id.id
                    and not l.activity_type_id
                    and self._assignment_matches_date(l.assignment_id, event_date)
                )
                for line in lines:
                    self._create_value_if_missing(
                        line=line,
                        value=line.value,
                        ref_model="crm.lead.stage.rule.line.%s" % line.id,
                        ref_id=lead.id,
                    )
        return True

    @api.model
    def process_activity_feedback_payload(self, payloads):
        if not payloads:
            return False

        lead_model = self.env["crm.lead"]
        event_date = fields.Date.today()
        for payload in payloads:
            lead = lead_model.browse(payload.get("res_id"))
            if not lead.exists() or not lead.business_category_id:
                continue

            activity_type_id = payload.get("activity_type_id")
            if not activity_type_id:
                continue

            employee = self._find_employee_from_user(self.env["res.users"].browse(payload.get("user_id")))
            if not employee and lead.user_id:
                employee = self._find_employee_from_user(lead.user_id)
            if not employee:
                continue

            rules = self.search(
                [
                    ("active", "=", True),
                    ("business_category_id", "=", lead.business_category_id.id),
                ]
            )
            for rule in rules:
                lines = rule.line_ids.filtered(
                    lambda l: l.active
                    and l.employee_id.id == employee.id
                    and l.activity_type_id.id == activity_type_id
                    and (not l.stage_id or l.stage_id.id == lead.stage_id.id)
                    and self._assignment_matches_date(l.assignment_id, event_date)
                )
                for line in lines:
                    self._create_value_if_missing(
                        line=line,
                        value=line.value,
                        ref_model="mail.activity.done.rule.line.%s" % line.id,
                        ref_id=payload.get("id"),
                    )
        return True


class KpiCrmTriggerRuleLine(models.Model):
    _name = "kpi.crm.trigger.rule.line"
    _description = "KPI CRM Trigger Rule Line"
    _order = "sequence, id"

    rule_id = fields.Many2one("kpi.crm.trigger.rule", required=True, ondelete="cascade", index=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    stage_id = fields.Many2one("crm.stage", string="Stage")
    activity_type_id = fields.Many2one("mail.activity.type", string="Activity Type")
    employee_id = fields.Many2one("hr.employee", required=True, ondelete="cascade", index=True)
    assignment_id = fields.Many2one("kpi.assignment", required=True, ondelete="cascade", index=True)
    value = fields.Float(required=True, default=1.0)
    source_module = fields.Char(default="crm", required=True)
    note = fields.Char()

    @api.constrains("stage_id", "activity_type_id")
    def _check_trigger_dimension(self):
        for rec in self:
            if rec.stage_id or rec.activity_type_id:
                continue
            raise ValidationError(_("Either Stage or Activity Type must be set."))

    @api.constrains("employee_id", "assignment_id")
    def _check_assignment_employee(self):
        for rec in self:
            if rec.assignment_id.employee_id != rec.employee_id:
                raise ValidationError(_("Employee must match KPI Assignment employee."))

    @api.constrains("rule_id", "stage_id")
    def _check_stage_business_category(self):
        for rec in self:
            if not rec.stage_id or not rec.rule_id.business_category_id:
                continue
            stage_category = rec.stage_id.business_category_id
            if stage_category and stage_category != rec.rule_id.business_category_id:
                raise ValidationError(
                    _("Stage business category must match rule business category.")
                )
