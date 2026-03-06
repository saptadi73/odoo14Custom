from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class CrmStage(models.Model):
    _inherit = "crm.stage"

    def init(self):
        self._cr.execute(
            """
            UPDATE crm_stage stage
               SET company_id = COALESCE(team.company_id, %s)
              FROM crm_team team
             WHERE stage.team_id = team.id
               AND stage.company_id IS NULL
            """,
            [self.env.ref("base.main_company").id],
        )
        self._cr.execute(
            """
            UPDATE crm_stage
               SET company_id = %s
             WHERE company_id IS NULL
            """,
            [self.env.ref("base.main_company").id],
        )

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

    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    business_category_id = fields.Many2one(
        "crm.business.category",
        string="Business Category",
        default=_default_business_category_id,
        ondelete="restrict",
        index=True,
        domain="[('company_id', '=', company_id)]",
    )

    @api.onchange("team_id")
    def _onchange_team_id_business_category(self):
        for stage in self:
            if stage.team_id and stage.team_id.company_id:
                stage.company_id = stage.team_id.company_id
            if stage.team_id and stage.team_id.business_category_id:
                stage.business_category_id = stage.team_id.business_category_id

    @api.onchange("company_id")
    def _onchange_company_id_relations(self):
        for stage in self:
            if stage.team_id and stage.team_id.company_id != stage.company_id:
                stage.team_id = False
            if stage.business_category_id and stage.business_category_id.company_id != stage.company_id:
                stage.business_category_id = False

    @api.model_create_multi
    def create(self, vals_list):
        team_model = self.env["crm.team"]
        category_model = self.env["crm.business.category"]
        for vals in vals_list:
            team_id = vals.get("team_id")
            category_id = vals.get("business_category_id")
            if team_id and not vals.get("company_id"):
                team = team_model.browse(team_id)
                if team.company_id:
                    vals["company_id"] = team.company_id.id
            if category_id and not vals.get("company_id"):
                category = category_model.browse(category_id)
                if category.company_id:
                    vals["company_id"] = category.company_id.id
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
            if stage.business_category_id and stage.company_id and stage.business_category_id.company_id != stage.company_id:
                raise ValidationError(
                    _(
                        "Stage '%s' must use a Business Category from company '%s'."
                    )
                    % (stage.name, stage.company_id.name)
                )
            if not stage.team_id or not stage.team_id.business_category_id or not stage.business_category_id:
                continue
            if stage.team_id.company_id and stage.company_id and stage.team_id.company_id != stage.company_id:
                raise ValidationError(
                    _(
                        "Stage '%s' must use a Pipeline from company '%s'."
                    )
                    % (stage.name, stage.company_id.name)
                )
            if stage.team_id.business_category_id != stage.business_category_id:
                raise ValidationError(
                    _(
                        "Stage '%s' must use the same Business Category as its Pipeline '%s' (%s)."
                    )
                    % (stage.name, stage.team_id.name, stage.team_id.business_category_id.name)
                )
