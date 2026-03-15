from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class HrExpense(models.Model):
    _inherit = "hr.expense"

    business_category_id = fields.Many2one(
        "crm.business.category",
        string="Business Category",
        default=lambda self: self.env["business.category.mixin"]._default_business_category_id(),
        domain="[('company_id', '=', company_id)]",
        ondelete="restrict",
        tracking=True,
    )
    expense_team_id = fields.Many2one(
        "expense.team",
        string="Expense Team",
        domain="[('company_id', '=', company_id), ('business_category_id', '=', business_category_id)]",
        tracking=True,
    )
    expense_analytic_account_id = fields.Many2one(
        "account.analytic.account",
        string="Expense Analytic Account",
        related="business_category_id.expense_analytic_account_id",
        store=True,
        readonly=True,
    )

    @api.onchange("business_category_id")
    def _onchange_business_category_id_reset_team(self):
        for expense in self:
            if expense.expense_team_id and expense.expense_team_id.business_category_id != expense.business_category_id:
                expense.expense_team_id = False

    @api.onchange("expense_team_id")
    def _onchange_expense_team_id(self):
        for expense in self:
            if expense.expense_team_id and expense.expense_team_id.business_category_id:
                expense.business_category_id = expense.expense_team_id.business_category_id

    @api.onchange("business_category_id")
    def _onchange_business_category_id_analytic(self):
        for expense in self:
            if "analytic_account_id" in expense._fields:
                expense.analytic_account_id = expense.business_category_id.expense_analytic_account_id

    @api.model_create_multi
    def create(self, vals_list):
        vals_list = [self._prepare_business_category_vals(vals) for vals in vals_list]
        return super().create(vals_list)

    def write(self, vals):
        vals = self._prepare_business_category_vals(vals)
        return super().write(vals)

    def _prepare_business_category_vals(self, vals):
        vals = dict(vals)
        if vals.get("expense_team_id") and not vals.get("business_category_id"):
            team = self.env["expense.team"].browse(vals["expense_team_id"])
            if team.business_category_id:
                vals["business_category_id"] = team.business_category_id.id
        if vals.get("business_category_id") and "analytic_account_id" in self._fields and not vals.get("analytic_account_id"):
            category = self.env["crm.business.category"].browse(vals["business_category_id"])
            if category.expense_analytic_account_id:
                vals["analytic_account_id"] = category.expense_analytic_account_id.id
        return vals

    @api.constrains("business_category_id", "expense_team_id", "company_id", "expense_analytic_account_id")
    def _check_business_category_team(self):
        for expense in self:
            if expense.business_category_id and expense.business_category_id.company_id != expense.company_id:
                raise ValidationError(
                    _("Expense '%s' uses a Business Category from another company.") % expense.name
                )
            if expense.expense_analytic_account_id and expense.expense_analytic_account_id.company_id != expense.company_id:
                raise ValidationError(
                    _("Expense '%s' uses an Analytic Account from another company.") % expense.name
                )
            if expense.expense_team_id:
                if expense.expense_team_id.company_id != expense.company_id:
                    raise ValidationError(
                        _("Expense Team '%s' belongs to another company.") % expense.expense_team_id.name
                    )
                if expense.expense_team_id.business_category_id != expense.business_category_id:
                    raise ValidationError(
                        _(
                            "Expense Team '%s' is linked to business category '%s'. "
                            "Please select a matching business category."
                        )
                        % (expense.expense_team_id.name, expense.expense_team_id.business_category_id.name)
                    )
            if (
                "analytic_account_id" in expense._fields
                and expense.expense_analytic_account_id
                and expense.analytic_account_id
                and expense.expense_analytic_account_id != expense.analytic_account_id
            ):
                raise ValidationError(
                    _("Expense '%s' must use the Expense Analytic Account configured on its Business Category.")
                    % expense.name
                )

    @api.constrains("business_category_id", "expense_team_id", "employee_id")
    def _check_current_user_expense_scope(self):
        current_user = self.env.user
        if current_user.has_group("base.group_system"):
            return

        effective_categories = current_user.effective_business_category_ids
        for expense in self:
            if expense.business_category_id and expense.business_category_id not in effective_categories:
                raise ValidationError(
                    _("You can only use Expenses in your registered Business Category.")
                )
            if expense.expense_team_id:
                team_users = expense.expense_team_id.user_id | expense.expense_team_id.member_ids
                if current_user not in team_users:
                    raise ValidationError(
                        _("You must be registered in the selected Expense Team before using it on an Expense.")
                    )


class HrExpenseSheet(models.Model):
    _inherit = "hr.expense.sheet"

    business_category_id = fields.Many2one(
        "crm.business.category",
        string="Business Category",
        compute="_compute_business_category_id",
        store=True,
        readonly=False,
    )
    expense_team_id = fields.Many2one(
        "expense.team",
        string="Expense Team",
        compute="_compute_expense_team_id",
        store=True,
        readonly=False,
    )
    expense_analytic_account_id = fields.Many2one(
        "account.analytic.account",
        string="Expense Analytic Account",
        compute="_compute_expense_analytic_account_id",
        store=True,
        readonly=False,
    )

    @api.depends("expense_line_ids.business_category_id")
    def _compute_business_category_id(self):
        for sheet in self:
            categories = sheet.expense_line_ids.mapped("business_category_id")
            sheet.business_category_id = categories[:1].id if len(categories) == 1 else False

    @api.depends("expense_line_ids.expense_team_id")
    def _compute_expense_team_id(self):
        for sheet in self:
            teams = sheet.expense_line_ids.mapped("expense_team_id")
            sheet.expense_team_id = teams[:1].id if len(teams) == 1 else False

    @api.depends("expense_line_ids.expense_analytic_account_id")
    def _compute_expense_analytic_account_id(self):
        for sheet in self:
            analytics = sheet.expense_line_ids.mapped("expense_analytic_account_id")
            sheet.expense_analytic_account_id = analytics[:1].id if len(analytics) == 1 else False

    @api.constrains("expense_line_ids", "business_category_id", "expense_team_id")
    def _check_expense_lines_same_business_category(self):
        for sheet in self:
            categories = sheet.expense_line_ids.mapped("business_category_id")
            if len(categories) > 1:
                raise ValidationError(
                    _("Expense Report '%s' cannot contain multiple Business Categories.") % sheet.name
                )
            teams = sheet.expense_line_ids.mapped("expense_team_id")
            if len(teams) > 1:
                raise ValidationError(
                    _("Expense Report '%s' cannot contain multiple Expense Teams.") % sheet.name
                )

    def action_sheet_move_create(self):
        result = super().action_sheet_move_create()
        for sheet in self:
            move = getattr(sheet, "account_move_id", False)
            if move and sheet.business_category_id:
                move.write(
                    {
                        "expense_business_category_id": sheet.business_category_id.id,
                        "expense_analytic_account_id": sheet.expense_analytic_account_id.id,
                    }
                )
        return result
