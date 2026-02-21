from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class CrmLead(models.Model):
    _inherit = "crm.lead"

    business_category_id = fields.Many2one(
        "crm.business.category",
        string="Business Category",
        ondelete="restrict",
    )

    @api.onchange("business_category_id")
    def _onchange_business_category_id(self):
        for lead in self:
            if lead.team_id and lead.team_id.business_category_id != lead.business_category_id:
                lead.team_id = False
            lead.stage_id = False

    @api.constrains("business_category_id", "team_id")
    def _check_business_category_team(self):
        for lead in self:
            if not lead.team_id or not lead.team_id.business_category_id:
                continue
            if lead.business_category_id and lead.team_id.business_category_id != lead.business_category_id:
                raise ValidationError(
                    _(
                        "Pipeline '%s' is linked to business category '%s'. "
                        "Please select a matching business category."
                    )
                    % (lead.team_id.name, lead.team_id.business_category_id.name)
                )

    @api.constrains("type", "business_category_id")
    def _check_business_category_required(self):
        for lead in self:
            if lead.type in ("lead", "opportunity") and not lead.business_category_id:
                raise ValidationError(_("Business Category is required for both Leads and Opportunities."))
