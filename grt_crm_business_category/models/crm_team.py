from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class CrmTeam(models.Model):
    _inherit = "crm.team"

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
        if has_active and user.active_business_category_id.company_id == self.env.company:
            return user.active_business_category_id.id
        if has_default and user.default_business_category_id.company_id == self.env.company:
            return user.default_business_category_id.id
        return False

    business_category_id = fields.Many2one(
        "crm.business.category",
        string="Business Category",
        default=_default_business_category_id,
        required=True,
        ondelete="restrict",
        domain="[('company_id', '=', company_id)]",
    )

    @api.onchange("company_id")
    def _onchange_company_id_business_category(self):
        for team in self:
            if team.business_category_id and team.business_category_id.company_id != team.company_id:
                team.business_category_id = False

    @api.constrains("company_id", "business_category_id")
    def _check_business_category_company(self):
        for team in self:
            if not team.company_id or not team.business_category_id:
                continue
            if team.business_category_id.company_id != team.company_id:
                raise ValidationError(
                    _(
                        "Pipeline '%s' must use a Business Category from company '%s'."
                    )
                    % (team.name, team.company_id.name)
                )
