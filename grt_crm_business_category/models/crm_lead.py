from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class CrmLead(models.Model):
    _inherit = "crm.lead"

    def _default_business_category_id(self):
        cr = self.env.cr
        cr.execute(
            """
            SELECT 1
            FROM information_schema.columns
            WHERE table_name = 'res_users' AND column_name = 'active_business_category_id'
            """
        )
        has_active = bool(cr.fetchone())
        cr.execute(
            """
            SELECT 1
            FROM information_schema.columns
            WHERE table_name = 'res_users' AND column_name = 'default_business_category_id'
            """
        )
        has_default = bool(cr.fetchone())

        if not has_active and not has_default:
            return False

        user = self.env.user
        if has_active and user.active_business_category_id:
            return user.active_business_category_id.id
        if has_default and user.default_business_category_id:
            return user.default_business_category_id.id
        return False

    business_category_id = fields.Many2one(
        "crm.business.category",
        string="Business Category",
        default=_default_business_category_id,
        ondelete="restrict",
    )

    @api.onchange("business_category_id")
    def _onchange_business_category_id(self):
        for lead in self:
            if lead.team_id and lead.team_id.business_category_id != lead.business_category_id:
                lead.team_id = False
            lead.stage_id = False

    @api.onchange("team_id")
    def _onchange_team_id_business_category(self):
        for lead in self:
            if lead.team_id and lead.team_id.business_category_id:
                lead.business_category_id = lead.team_id.business_category_id

    @api.constrains("business_category_id", "team_id")
    def _check_business_category_team(self):
        for lead in self:
            if not lead.team_id:
                continue
            if not lead.team_id.business_category_id:
                raise ValidationError(
                    _("Pipeline '%s' must have a Business Category before it can be used.") % lead.team_id.name
                )
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
