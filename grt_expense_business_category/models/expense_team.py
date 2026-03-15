from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ExpenseTeam(models.Model):
    _name = "expense.team"
    _description = "Expense Team"
    _order = "name"

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
    )
    user_id = fields.Many2one(
        "res.users",
        string="Team Leader",
        help="Responsible user for this Expense Team.",
    )
    member_ids = fields.Many2many(
        "res.users",
        "expense_team_res_users_rel",
        "team_id",
        "user_id",
        string="Members",
    )
    business_category_id = fields.Many2one(
        "crm.business.category",
        string="Business Category",
        required=True,
        default=lambda self: self.env["business.category.mixin"]._default_business_category_id(),
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
                        "Expense Team '%s' must use a Business Category from company '%s'."
                    )
                    % (team.name, team.company_id.name)
                )
