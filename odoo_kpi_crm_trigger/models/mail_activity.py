from odoo import models


class MailActivity(models.Model):
    _inherit = "mail.activity"

    def action_feedback(self, feedback=False, attachment_ids=None):
        crm_payload = []
        for activity in self:
            if activity.res_model != "crm.lead" or not activity.res_id or not activity.activity_type_id:
                continue
            crm_payload.append(
                {
                    "id": activity.id,
                    "res_id": activity.res_id,
                    "activity_type_id": activity.activity_type_id.id,
                    "user_id": activity.user_id.id,
                }
            )

        result = super().action_feedback(feedback=feedback, attachment_ids=attachment_ids)

        if crm_payload:
            self.env["kpi.crm.trigger.rule"].sudo().process_activity_feedback_payload(crm_payload)
        return result
