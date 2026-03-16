from odoo import _, api, fields, models
from odoo.exceptions import UserError


class ManualReconcileWizard(models.TransientModel):
    _name = "manual.reconcile.wizard"
    _description = "Manual Reconciliation Wizard"

    reconciliation_type = fields.Selection(
        [
            ("employee_expense", "Employee Advance vs Expense"),
            ("customer_sales", "Customer Advance vs Sales"),
            ("vendor_purchase", "Vendor Advance vs Purchase"),
        ],
        string="Reconciliation Type",
        required=True,
        default=lambda self: self.env.context.get("default_reconciliation_type", "employee_expense"),
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
    )
    partner_id = fields.Many2one(
        "res.partner",
        string="Partner",
        required=True,
    )
    account_internal_type = fields.Selection(
        [
            ("receivable", "Receivable"),
            ("payable", "Payable"),
        ],
        compute="_compute_account_internal_type",
    )
    account_id = fields.Many2one(
        "account.account",
        string="Account",
        domain="[('company_id', '=', company_id), ('deprecated', '=', False), ('reconcile', '=', True), ('internal_type', '=', account_internal_type)]",
    )
    line_ids = fields.One2many(
        "manual.reconcile.wizard.line",
        "wizard_id",
        string="Lines",
    )

    @api.depends("reconciliation_type")
    def _compute_account_internal_type(self):
        for wizard in self:
            wizard.account_internal_type = "receivable" if wizard.reconciliation_type == "customer_sales" else "payable"

    @api.onchange("partner_id", "reconciliation_type", "company_id")
    def _onchange_partner_id_set_account(self):
        for wizard in self:
            if not wizard.partner_id:
                wizard.account_id = False
                continue
            if wizard.reconciliation_type == "customer_sales":
                wizard.account_id = wizard.partner_id.property_account_receivable_id
            else:
                wizard.account_id = wizard.partner_id.property_account_payable_id

    def _get_line_base_domain(self):
        self.ensure_one()
        partner = self.partner_id.commercial_partner_id
        partner_ids = self.env["res.partner"].search([("id", "child_of", partner.id)]).ids
        domain = [
            ("company_id", "=", self.company_id.id),
            ("partner_id", "in", partner_ids),
            ("move_id.state", "=", "posted"),
            ("reconciled", "=", False),
            ("account_id.reconcile", "=", True),
            ("account_id.internal_type", "=", self.account_internal_type),
            ("amount_residual", "!=", 0.0),
        ]
        if self.account_id:
            domain.append(("account_id", "=", self.account_id.id))
        return domain

    def _extend_with_payment_domain(self, domain):
        self.ensure_one()
        aml_model = self.env["account.move.line"]
        if "payment_id" in aml_model._fields:
            domain.append(("payment_id", "!=", False))
        else:
            domain.append(("move_id.move_type", "=", "entry"))
        return domain

    def _get_transaction_domain(self):
        self.ensure_one()
        domain = list(self._get_line_base_domain())
        if self.reconciliation_type == "employee_expense":
            domain.extend(self._get_employee_expense_transaction_domain())
        elif self.reconciliation_type == "customer_sales":
            domain.extend(
                [
                    ("move_id.move_type", "=", "out_invoice"),
                    ("balance", ">", 0),
                ]
            )
        else:
            domain.extend(
                [
                    ("move_id.move_type", "=", "in_invoice"),
                    ("balance", "<", 0),
                ]
            )
        return domain

    def _get_counterpart_domain(self):
        self.ensure_one()
        domain = list(self._get_line_base_domain())
        if self.reconciliation_type == "customer_sales":
            domain.extend(
                [
                    ("balance", "<", 0),
                ]
            )
            self._extend_with_payment_domain(domain)
        elif self.reconciliation_type == "vendor_purchase":
            domain.extend(
                [
                    ("balance", ">", 0),
                ]
            )
            self._extend_with_payment_domain(domain)
        else:
            domain.extend(self._get_employee_expense_counterpart_domain())
        return domain

    def _get_employee_expense_transaction_domain(self):
        self.ensure_one()
        aml_model = self.env["account.move.line"]
        move_model = self.env["account.move"]
        domain = [("balance", "<", 0)]

        # Prefer explicit links to hr.expense / expense sheet journal entries when present.
        expense_move_link_fields = [
            field_name
            for field_name in ("expense_sheet_id", "expense_id")
            if field_name in move_model._fields
        ]
        expense_line_link_fields = [
            field_name
            for field_name in ("expense_sheet_id", "expense_id")
            if field_name in aml_model._fields
        ]
        if expense_move_link_fields:
            domain = ["&"] + domain + ["|"] * (len(expense_move_link_fields) - 1)
            for field_name in expense_move_link_fields:
                domain.append(("move_id.%s" % field_name, "!=", False))
        elif expense_line_link_fields:
            domain = ["&"] + domain + ["|"] * (len(expense_line_link_fields) - 1)
            for field_name in expense_line_link_fields:
                domain.append((field_name, "!=", False))
        else:
            domain.extend(
                [
                    ("move_id.move_type", "=", "entry"),
                ]
            )
            if "payment_id" in aml_model._fields:
                domain.append(("payment_id", "=", False))
        return domain

    def _get_employee_expense_counterpart_domain(self):
        self.ensure_one()
        aml_model = self.env["account.move.line"]
        move_model = self.env["account.move"]
        domain = [("balance", ">", 0)]

        expense_move_link_fields = [
            field_name
            for field_name in ("expense_sheet_id", "expense_id")
            if field_name in move_model._fields
        ]
        expense_line_link_fields = [
            field_name
            for field_name in ("expense_sheet_id", "expense_id")
            if field_name in aml_model._fields
        ]
        if expense_move_link_fields or expense_line_link_fields:
            exclude_domain = []
            for field_name in expense_move_link_fields:
                exclude_domain.append(("move_id.%s" % field_name, "=", False))
            for field_name in expense_line_link_fields:
                exclude_domain.append((field_name, "=", False))
            domain.extend(exclude_domain)
        else:
            domain.append(("move_id.move_type", "=", "entry"))

        if "payment_id" in aml_model._fields:
            domain.append(("payment_id", "!=", False))
        return domain

    def _prepare_line_vals(self, move_line, role):
        self.ensure_one()
        move = move_line.move_id
        return {
            "wizard_id": self.id,
            "role": role,
            "move_line_id": move_line.id,
            "document_type": move.move_type or "entry",
        }

    def _get_reload_action(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Manual Reconciliation"),
            "res_model": self._name,
            "view_mode": "form",
            "res_id": self.id,
            "target": "current",
            "context": dict(self.env.context),
        }

    def action_load_transactions(self):
        self.ensure_one()
        if not self.partner_id:
            raise UserError(_("Please select a partner before loading transactions."))

        transaction_lines = self.env["account.move.line"].search(
            self._get_transaction_domain(),
            order="date_maturity asc, date asc, id asc",
        )
        counterpart_lines = self.env["account.move.line"].search(
            self._get_counterpart_domain(),
            order="date_maturity asc, date asc, id asc",
        )

        self.line_ids.unlink()
        vals_list = []
        vals_list.extend(self._prepare_line_vals(line, "transaction") for line in transaction_lines)
        vals_list.extend(self._prepare_line_vals(line, "counterpart") for line in counterpart_lines)
        if vals_list:
            self.env["manual.reconcile.wizard.line"].create(vals_list)
        return self._get_reload_action()

    def action_reconcile_selected(self):
        self.ensure_one()
        transaction_lines = self.line_ids.filtered(lambda line: line.role == "transaction" and line.selected)
        counterpart_lines = self.line_ids.filtered(lambda line: line.role == "counterpart" and line.selected)
        if not transaction_lines:
            raise UserError(_("Please select at least one transaction line."))
        if not counterpart_lines:
            raise UserError(_("Please select at least one advance/payment line."))

        move_lines = (transaction_lines | counterpart_lines).mapped("move_line_id")
        if any(line.reconciled for line in move_lines):
            raise UserError(_("One of the selected journal items is already reconciled. Please reload the transactions."))

        accounts = move_lines.mapped("account_id")
        if len(accounts) != 1:
            raise UserError(_("All selected journal items must use the same account."))

        partners = move_lines.mapped("partner_id.commercial_partner_id")
        if len(partners) != 1:
            raise UserError(_("All selected journal items must belong to the same partner."))

        balances = move_lines.mapped("balance")
        if not any(balance > 0 for balance in balances) or not any(balance < 0 for balance in balances):
            raise UserError(_("Selected journal items must contain both debit and credit balances for reconciliation."))

        move_lines.reconcile()
        return self.action_load_transactions()


class ManualReconcileWizardLine(models.TransientModel):
    _name = "manual.reconcile.wizard.line"
    _description = "Manual Reconciliation Wizard Line"
    _order = "date_maturity, date, id"

    wizard_id = fields.Many2one(
        "manual.reconcile.wizard",
        string="Wizard",
        required=True,
        ondelete="cascade",
    )
    role = fields.Selection(
        [
            ("transaction", "Transaction"),
            ("counterpart", "Advance/Payment"),
        ],
        string="Role",
        required=True,
    )
    selected = fields.Boolean(string="Select")
    move_line_id = fields.Many2one(
        "account.move.line",
        string="Journal Item",
        required=True,
        ondelete="cascade",
    )
    move_id = fields.Many2one(
        "account.move",
        string="Journal Entry",
        related="move_line_id.move_id",
        readonly=True,
    )
    date = fields.Date(
        related="move_line_id.date",
        readonly=True,
    )
    date_maturity = fields.Date(
        related="move_line_id.date_maturity",
        readonly=True,
    )
    journal_id = fields.Many2one(
        "account.journal",
        related="move_line_id.journal_id",
        readonly=True,
    )
    partner_id = fields.Many2one(
        "res.partner",
        related="move_line_id.partner_id",
        readonly=True,
    )
    account_id = fields.Many2one(
        "account.account",
        related="move_line_id.account_id",
        readonly=True,
    )
    currency_id = fields.Many2one(
        "res.currency",
        related="move_line_id.currency_id",
        readonly=True,
    )
    company_currency_id = fields.Many2one(
        "res.currency",
        related="wizard_id.company_id.currency_id",
        readonly=True,
    )
    label = fields.Char(
        related="move_line_id.name",
        readonly=True,
    )
    ref = fields.Char(
        related="move_id.ref",
        readonly=True,
    )
    document_type = fields.Char(string="Document Type", readonly=True)
    balance = fields.Monetary(
        related="move_line_id.balance",
        currency_field="company_currency_id",
        readonly=True,
    )
    amount_residual = fields.Monetary(
        related="move_line_id.amount_residual",
        currency_field="company_currency_id",
        readonly=True,
    )
