from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class PartnerOffsetWizard(models.TransientModel):
    _name = "partner.offset.wizard"
    _description = "Partner Receivable Payable Offset Wizard"

    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
    )
    partner_id = fields.Many2one(
        "res.partner",
        string="Member / Partner",
        required=True,
    )
    date = fields.Date(
        string="Offset Date",
        required=True,
        default=fields.Date.context_today,
    )
    journal_id = fields.Many2one(
        "account.journal",
        string="Journal",
        required=True,
        default=lambda self: self.env["account.journal"].search(
            [("company_id", "=", self.env.company.id), ("type", "=", "general")],
            limit=1,
        ),
        domain="[('company_id', '=', company_id), ('type', '=', 'general')]",
    )
    line_ids = fields.One2many(
        "partner.offset.wizard.line",
        "wizard_id",
        string="Lines",
    )
    currency_id = fields.Many2one(
        "res.currency",
        related="company_id.currency_id",
        readonly=True,
    )
    receivable_total = fields.Monetary(
        string="Customer Total",
        currency_field="currency_id",
        compute="_compute_totals",
    )
    payable_total = fields.Monetary(
        string="Vendor Total",
        currency_field="currency_id",
        compute="_compute_totals",
    )
    difference_amount = fields.Monetary(
        string="Difference",
        currency_field="currency_id",
        compute="_compute_totals",
    )
    line_count = fields.Integer(
        string="Loaded Lines",
        compute="_compute_totals",
    )
    move_id = fields.Many2one(
        "account.move",
        string="Offset Journal Entry",
        readonly=True,
    )

    @api.depends("line_ids.amount_to_offset", "line_ids.side")
    def _compute_totals(self):
        for wizard in self:
            receivable_lines = wizard.line_ids.filtered(lambda line: line.side == "receivable")
            payable_lines = wizard.line_ids.filtered(lambda line: line.side == "payable")
            wizard.receivable_total = sum(receivable_lines.mapped("amount_to_offset"))
            wizard.payable_total = sum(payable_lines.mapped("amount_to_offset"))
            wizard.difference_amount = wizard.receivable_total - wizard.payable_total
            wizard.line_count = len(wizard.line_ids)

    @api.onchange("company_id")
    def _onchange_company_id(self):
        for wizard in self:
            if wizard.journal_id.company_id != wizard.company_id:
                wizard.journal_id = False

    @api.onchange("partner_id", "company_id")
    def _onchange_partner_id(self):
        for wizard in self:
            wizard.line_ids = [(5, 0, 0)]
            wizard.move_id = False

    def _get_open_item_domain(self, internal_type, balance_operator):
        self.ensure_one()
        partner = self.partner_id.commercial_partner_id
        partner_ids = self.env["res.partner"].search([("id", "child_of", partner.id)]).ids
        return [
            ("company_id", "=", self.company_id.id),
            ("partner_id", "in", partner_ids),
            ("move_id.state", "=", "posted"),
            ("reconciled", "=", False),
            ("account_id.reconcile", "=", True),
            ("account_id.internal_type", "=", internal_type),
            ("amount_residual", "!=", 0.0),
            ("balance", balance_operator, 0.0),
        ]

    def _prepare_line_vals(self, move_line, side):
        self.ensure_one()
        return {
            "wizard_id": self.id,
            "side": side,
            "move_line_id": move_line.id,
            "amount_to_offset": abs(move_line.amount_residual),
        }

    def action_load_open_items(self):
        self.ensure_one()
        if not self.partner_id:
            raise UserError(_("Please select a member / partner first."))

        receivable_lines = self.env["account.move.line"].search(
            self._get_open_item_domain("receivable", ">"),
            order="date_maturity asc, date asc, id asc",
        )
        payable_lines = self.env["account.move.line"].search(
            self._get_open_item_domain("payable", "<"),
            order="date_maturity asc, date asc, id asc",
        )

        self.line_ids.unlink()
        vals_list = []
        vals_list.extend(self._prepare_line_vals(line, "receivable") for line in receivable_lines)
        vals_list.extend(self._prepare_line_vals(line, "payable") for line in payable_lines)
        if vals_list:
            self.env["partner.offset.wizard.line"].create(vals_list)
        self.move_id = False
        return {
            "type": "ir.actions.act_window",
            "name": _("Partner Offset"),
            "res_model": self._name,
            "view_mode": "form",
            "res_id": self.id,
            "target": "current",
            "context": dict(self.env.context),
        }

    def _validate_selected_lines(self):
        self.ensure_one()
        if not self.journal_id:
            raise UserError(_("Please select a journal."))

        selected_lines = self.line_ids.filtered(lambda line: line.amount_to_offset > 0)
        receivable_lines = selected_lines.filtered(lambda line: line.side == "receivable")
        payable_lines = selected_lines.filtered(lambda line: line.side == "payable")
        if not receivable_lines:
            raise UserError(_("Please input at least one customer amount to offset."))
        if not payable_lines:
            raise UserError(_("Please input at least one vendor amount to offset."))

        for line in selected_lines:
            if line.move_line_id.reconciled:
                raise UserError(
                    _("One of the selected open items is already reconciled. Please reload the open items first.")
                )
            line._check_amount_to_offset()

        if not self.currency_id.is_zero(self.receivable_total - self.payable_total):
            raise UserError(
                _(
                    "Customer and vendor totals must be equal before confirming the offset. "
                    "Please adjust Amount to Offset on one side."
                )
            )
        return receivable_lines, payable_lines

    def _prepare_move_line_vals(self, wizard_line):
        self.ensure_one()
        amount = wizard_line.amount_to_offset
        source_line = wizard_line.move_line_id
        line_name = "[OFFSET:%s] %s" % (source_line.id, source_line.move_id.name or source_line.name or "/")
        vals = {
            "name": line_name,
            "partner_id": source_line.partner_id.id,
            "account_id": source_line.account_id.id,
        }
        if wizard_line.side == "receivable":
            vals.update({"debit": 0.0, "credit": amount})
        else:
            vals.update({"debit": amount, "credit": 0.0})
        return vals

    def _create_offset_move(self, receivable_lines, payable_lines):
        self.ensure_one()
        move_vals = {
            "date": self.date,
            "ref": _("Partner offset - %s") % self.partner_id.display_name,
            "journal_id": self.journal_id.id,
            "company_id": self.company_id.id,
            "line_ids": [],
        }
        all_lines = receivable_lines | payable_lines
        for line in all_lines:
            move_vals["line_ids"].append((0, 0, self._prepare_move_line_vals(line)))

        move = self.env["account.move"].create(move_vals)
        move.action_post()
        self.move_id = move.id
        return move

    def _reconcile_offset_move(self, move, selected_lines):
        self.ensure_one()
        for wizard_line in selected_lines:
            source_line = wizard_line.move_line_id
            technical_name = "[OFFSET:%s] %s" % (
                source_line.id,
                source_line.move_id.name or source_line.name or "/",
            )
            offset_line = move.line_ids.filtered(
                lambda line: line.account_id == source_line.account_id
                and line.partner_id == source_line.partner_id
                and line.name == technical_name
            )[:1]
            if not offset_line:
                raise UserError(
                    _("Unable to find the generated offset entry for %s.") % (source_line.move_id.display_name,)
                )
            (source_line | offset_line).reconcile()

    def action_confirm_offset(self):
        self.ensure_one()
        receivable_lines, payable_lines = self._validate_selected_lines()
        selected_lines = receivable_lines | payable_lines
        move = self._create_offset_move(receivable_lines, payable_lines)
        self._reconcile_offset_move(move, selected_lines)
        return {
            "type": "ir.actions.act_window",
            "name": _("Offset Journal Entry"),
            "res_model": "account.move",
            "view_mode": "form",
            "res_id": move.id,
            "target": "current",
        }


class PartnerOffsetWizardLine(models.TransientModel):
    _name = "partner.offset.wizard.line"
    _description = "Partner Offset Wizard Line"
    _order = "side, date_maturity, date, id"

    wizard_id = fields.Many2one(
        "partner.offset.wizard",
        string="Wizard",
        required=True,
        ondelete="cascade",
    )
    side = fields.Selection(
        [
            ("receivable", "Customer Receivable"),
            ("payable", "Vendor Payable"),
        ],
        string="Side",
        required=True,
    )
    move_line_id = fields.Many2one(
        "account.move.line",
        string="Journal Item",
        required=True,
        ondelete="cascade",
    )
    move_id = fields.Many2one(
        "account.move",
        string="Document",
        related="move_line_id.move_id",
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
    journal_id = fields.Many2one(
        "account.journal",
        related="move_line_id.journal_id",
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
    ref = fields.Char(
        related="move_id.ref",
        readonly=True,
    )
    label = fields.Char(
        related="move_line_id.name",
        readonly=True,
    )
    currency_id = fields.Many2one(
        "res.currency",
        related="wizard_id.currency_id",
        readonly=True,
    )
    residual_amount = fields.Monetary(
        string="Open Amount",
        currency_field="currency_id",
        compute="_compute_residual_amount",
        readonly=True,
    )
    amount_to_offset = fields.Monetary(
        string="Amount to Offset",
        currency_field="currency_id",
    )

    @api.depends("move_line_id.amount_residual")
    def _compute_residual_amount(self):
        for line in self:
            line.residual_amount = abs(line.move_line_id.amount_residual)

    @api.constrains("amount_to_offset")
    def _check_amount_to_offset(self):
        for line in self:
            if line.amount_to_offset < 0:
                raise ValidationError(_("Amount to Offset cannot be negative."))
            if line.amount_to_offset > line.residual_amount:
                raise ValidationError(_("Amount to Offset cannot exceed the open amount."))
