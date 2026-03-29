from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ResUsers(models.Model):
    _inherit = "res.users"

    allowed_business_category_ids = fields.Many2many(
        "crm.business.category",
        "res_users_crm_business_category_rel",
        "user_id",
        "business_category_id",
        string="Allowed Business Categories",
        domain="[('company_id', 'in', company_ids)]",
        help="Users can only access records in these business categories.",
    )
    team_business_category_ids = fields.Many2many(
        "crm.business.category",
        string="Team Business Categories",
        compute="_compute_effective_business_category_ids",
        readonly=True,
        help="Business categories inherited automatically from team membership.",
    )
    effective_business_category_ids = fields.Many2many(
        "crm.business.category",
        string="Effective Business Categories",
        compute="_compute_effective_business_category_ids",
        readonly=True,
        help="Union of manual access and team-based access.",
    )

    default_business_category_id = fields.Many2one(
        "crm.business.category",
        string="Default Business Category",
        domain="[('id', 'in', effective_business_category_ids), ('company_id', 'in', company_ids)]",
        help="Default category for new records.",
    )

    active_business_category_id = fields.Many2one(
        "crm.business.category",
        string="Active Business Category",
        domain="[('id', 'in', effective_business_category_ids), ('company_id', 'in', company_ids)]",
        help="Current user context category, similar to active company.",
    )

    def _build_or_domain(self, domain_parts):
        if not domain_parts:
            return []
        if len(domain_parts) == 1:
            return domain_parts
        return ["|"] * (len(domain_parts) - 1) + domain_parts

    def _get_team_business_categories_from_model(self, model_name, domain_parts):
        self.ensure_one()
        if model_name not in self.env:
            return self.env["crm.business.category"]

        team_model = self.env[model_name].sudo()
        user_id = self._origin.id or self.id
        if not isinstance(user_id, int):
            return self.env["crm.business.category"]
        valid_domain_parts = [
            domain_part
            for domain_part in domain_parts
            if isinstance(domain_part, (list, tuple))
            and len(domain_part) >= 1
            and domain_part[0] in team_model._fields
        ]
        if not valid_domain_parts:
            return self.env["crm.business.category"]

        domain = self._build_or_domain(valid_domain_parts)
        teams = team_model.search(domain + [("company_id", "in", self.company_ids.ids)])
        return teams.mapped("business_category_id")

    def _get_team_business_categories(self):
        self.ensure_one()
        categories = self.env["crm.business.category"]

        categories |= self._get_team_business_categories_from_model(
            "crm.team",
            [
                ("user_id", "=", self.id),
                ("member_ids", "in", self.id),
                ("sale_team_leader_id", "=", self.id),
                ("team_members_ids", "in", self.id),
            ],
        )
        categories |= self._get_team_business_categories_from_model(
            "purchase.team",
            [("user_id", "=", self.id), ("member_ids", "in", self.id)],
        )
        categories |= self._get_team_business_categories_from_model(
            "expense.team",
            [("user_id", "=", self.id), ("member_ids", "in", self.id)],
        )
        categories |= self._get_team_business_categories_from_model(
            "stock.team",
            [("user_id", "=", self.id), ("member_ids", "in", self.id)],
        )
        return categories

    def _filter_business_categories_by_company(self, categories):
        self.ensure_one()
        return categories.filtered(lambda category: category.company_id in self.company_ids)

    @api.depends("allowed_business_category_ids", "company_ids")
    def _compute_effective_business_category_ids(self):
        for user in self:
            team_categories = user._get_team_business_categories()
            allowed_categories = user._filter_business_categories_by_company(
                user.allowed_business_category_ids
            )
            user.team_business_category_ids = team_categories
            user.effective_business_category_ids = allowed_categories | team_categories

    @api.onchange("allowed_business_category_ids", "company_ids")
    def _onchange_allowed_business_category_ids(self):
        for user in self:
            effective_categories = user._filter_business_categories_by_company(
                user.allowed_business_category_ids
            ) | user._get_team_business_categories()
            if user.default_business_category_id not in effective_categories:
                user.default_business_category_id = False
            if user.active_business_category_id not in effective_categories:
                user.active_business_category_id = False
            if effective_categories and not user.default_business_category_id:
                user.default_business_category_id = effective_categories[0]
            if effective_categories and not user.active_business_category_id:
                user.active_business_category_id = user.default_business_category_id

    @api.constrains(
        "allowed_business_category_ids",
        "default_business_category_id",
        "active_business_category_id",
    )
    def _check_business_category_consistency(self):
        for user in self:
            effective_categories = user._filter_business_categories_by_company(
                user.allowed_business_category_ids
            ) | user._get_team_business_categories()
            if (
                user.default_business_category_id
                and user.default_business_category_id not in effective_categories
            ):
                raise ValidationError(
                    _("Default Business Category must be included in Effective Business Categories.")
                )
            if (
                user.default_business_category_id
                and user.default_business_category_id.company_id not in user.company_ids
            ):
                raise ValidationError(
                    _("Default Business Category must belong to one of the user's allowed companies.")
                )
            if (
                user.active_business_category_id
                and user.active_business_category_id not in effective_categories
            ):
                raise ValidationError(
                    _("Active Business Category must be included in Effective Business Categories.")
                )
            if (
                user.active_business_category_id
                and user.active_business_category_id.company_id not in user.company_ids
            ):
                raise ValidationError(
                    _("Active Business Category must belong to one of the user's allowed companies.")
                )

    def action_sync_team_business_category_access(self):
        for user in self:
            effective_categories = user._filter_business_categories_by_company(
                user.allowed_business_category_ids
            ) | user._get_team_business_categories()
            first_category = effective_categories[:1]
            vals = {}

            if user.default_business_category_id not in effective_categories:
                vals["default_business_category_id"] = first_category.id if first_category else False
            elif not user.default_business_category_id and first_category:
                vals["default_business_category_id"] = first_category.id

            default_id = vals.get("default_business_category_id") or user.default_business_category_id.id
            if user.active_business_category_id not in effective_categories:
                vals["active_business_category_id"] = default_id or (
                    first_category.id if first_category else False
                )
            elif not user.active_business_category_id:
                vals["active_business_category_id"] = default_id or (
                    first_category.id if first_category else False
                )

            if vals:
                user.write(vals)
        return {"type": "ir.actions.client", "tag": "reload"}
