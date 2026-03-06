from odoo import models


class CrmLead(models.Model):
    _inherit = "crm.lead"

    def write(self, vals):
        previous_stage_map = {}
        if "stage_id" in vals:
            previous_stage_map = {lead.id: lead.stage_id.id for lead in self}

        result = super().write(vals)

        if "stage_id" in vals:
            changed = self.filtered(lambda lead: lead.stage_id and previous_stage_map.get(lead.id) != lead.stage_id.id)
            if changed:
                self.env["kpi.crm.trigger.rule"].sudo().process_lead_stage_change(changed, previous_stage_map)
        return result
