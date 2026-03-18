from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class HrExpense(models.Model):
    _inherit = "hr.expense"

    mrp_overhead_type_id = fields.Many2one(
        "mrp.overhead.type",
        string="MRP Overhead Type",
        domain="[('company_id', '=', company_id)]",
        tracking=True,
        help="Classify this expense as manufacturing overhead so it can be absorbed into production.",
    )

    @api.constrains("mrp_overhead_type_id", "company_id")
    def _check_mrp_overhead_company(self):
        for expense in self:
            if expense.mrp_overhead_type_id and expense.mrp_overhead_type_id.company_id != expense.company_id:
                raise ValidationError(
                    _("Expense '%s' uses an overhead type from another company.") % expense.name
                )


class HrExpenseSheet(models.Model):
    _inherit = "hr.expense.sheet"

    mrp_overhead_type_id = fields.Many2one(
        "mrp.overhead.type",
        string="MRP Overhead Type",
        compute="_compute_mrp_overhead_type_id",
        store=True,
        readonly=False,
    )

    @api.depends("expense_line_ids.mrp_overhead_type_id")
    def _compute_mrp_overhead_type_id(self):
        for sheet in self:
            types = sheet.expense_line_ids.mapped("mrp_overhead_type_id")
            sheet.mrp_overhead_type_id = types[:1].id if len(types) == 1 else False

    def action_sheet_move_create(self):
        result = super().action_sheet_move_create()
        for sheet in self:
            move = getattr(sheet, "account_move_id", False)
            if move and sheet.mrp_overhead_type_id:
                move.write({"mrp_overhead_type_id": sheet.mrp_overhead_type_id.id})
        return result
