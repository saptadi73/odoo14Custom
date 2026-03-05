from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class CrmStage(models.Model):
    _inherit = "crm.stage"

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
        index=True,
    )

    @api.onchange("team_id")
    def _onchange_team_id_business_category(self):
        for stage in self:
            if stage.team_id and stage.team_id.business_category_id:
                stage.business_category_id = stage.team_id.business_category_id

    @api.model_create_multi
    def create(self, vals_list):
        team_model = self.env["crm.team"]
        for vals in vals_list:
            team_id = vals.get("team_id")
            if team_id and not vals.get("business_category_id"):
                team = team_model.browse(team_id)
                if team.business_category_id:
                    vals["business_category_id"] = team.business_category_id.id
        return super().create(vals_list)

    def write(self, vals):
        team_model = self.env["crm.team"]
        if vals.get("team_id") and not vals.get("business_category_id"):
            team = team_model.browse(vals["team_id"])
            if team.business_category_id:
                vals["business_category_id"] = team.business_category_id.id
        return super().write(vals)

    @api.constrains("team_id", "business_category_id")
    def _check_stage_team_category(self):
        for stage in self:
            if not stage.team_id or not stage.team_id.business_category_id or not stage.business_category_id:
                continue
            if stage.team_id.business_category_id != stage.business_category_id:
                raise ValidationError(
                    _(
                        "Stage '%s' must use the same Business Category as its Pipeline '%s' (%s)."
                    )
                    % (stage.name, stage.team_id.name, stage.team_id.business_category_id.name)
                )
