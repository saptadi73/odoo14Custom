from odoo import fields, models


class MrpOverheadType(models.Model):
    _name = "mrp.overhead.type"
    _description = "MRP Overhead Type"
    _order = "sequence, name, id"

    name = fields.Char(required=True)
    code = fields.Char()
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company",
        required=True,
        default=lambda self: self.env.company,
    )
    allocation_basis = fields.Selection(
        [
            ("kg", "Per Kg"),
            ("hour", "Per Jam"),
            ("mo", "Per MO"),
        ],
        required=True,
        default="kg",
    )
    default_source_account_id = fields.Many2one(
        "account.account",
        string="Default Source Expense Account",
        domain="[('company_id', '=', company_id), ('deprecated', '=', False)]",
        help="Fallback source account when no actual expense journal items are linked.",
    )
    absorption_account_id = fields.Many2one(
        "account.account",
        required=True,
        domain="[('company_id', '=', company_id), ('deprecated', '=', False)]",
        help="Account debited when overhead is absorbed into production.",
    )
    variance_account_id = fields.Many2one(
        "account.account",
        required=True,
        domain="[('company_id', '=', company_id), ('deprecated', '=', False)]",
        help="Account used for under/over absorption variance.",
    )
    note = fields.Text()
    period_line_ids = fields.One2many("mrp.overhead.period.line", "overhead_type_id")
