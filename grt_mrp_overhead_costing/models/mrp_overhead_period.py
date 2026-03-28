from collections import defaultdict
from datetime import datetime, time

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_is_zero


class MrpOverheadPeriod(models.Model):
    _name = "mrp.overhead.period"
    _description = "MRP Overhead Period"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date_start desc, id desc"

    name = fields.Char(required=True, copy=False, default="New", tracking=True)
    company_id = fields.Many2one(
        "res.company",
        required=True,
        default=lambda self: self.env.company,
        tracking=True,
    )
    currency_id = fields.Many2one(
        "res.currency",
        related="company_id.currency_id",
        store=True,
        readonly=True,
    )
    date_start = fields.Date(required=True, tracking=True)
    date_end = fields.Date(required=True, tracking=True)
    journal_id = fields.Many2one(
        "account.journal",
        string="Adjustment Journal",
        required=True,
        domain="[('company_id', '=', company_id), ('type', '=', 'general')]",
        tracking=True,
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("computed", "Computed"),
            ("adjusted", "Adjustment Created"),
        ],
        default="draft",
        tracking=True,
    )
    line_ids = fields.One2many("mrp.overhead.period.line", "period_id", string="Overhead Lines")
    allocation_line_ids = fields.One2many("mrp.overhead.allocation.line", "period_id", string="Allocations")
    adjustment_move_id = fields.Many2one("account.move", copy=False, readonly=True)
    stock_valuation_layer_ids = fields.One2many(
        "stock.valuation.layer",
        "mrp_overhead_period_id",
        string="Stock Valuation Layers",
        readonly=True,
    )
    actual_amount_total = fields.Monetary(compute="_compute_amount_totals")
    absorbed_amount_total = fields.Monetary(compute="_compute_amount_totals")
    variance_amount_total = fields.Monetary(compute="_compute_amount_totals")
    note = fields.Text()

    _sql_constraints = [
        (
            "date_check",
            "CHECK(date_end >= date_start)",
            "Tanggal akhir overhead harus lebih besar atau sama dengan tanggal awal.",
        ),
    ]

    @api.depends("line_ids.actual_amount", "line_ids.absorbed_amount", "line_ids.variance_amount")
    def _compute_amount_totals(self):
        for period in self:
            period.actual_amount_total = sum(period.line_ids.mapped("actual_amount"))
            period.absorbed_amount_total = sum(period.line_ids.mapped("absorbed_amount"))
            period.variance_amount_total = sum(period.line_ids.mapped("variance_amount"))

    @api.constrains("company_id", "date_start", "date_end")
    def _check_overlapping_periods(self):
        for period in self:
            overlap = self.search(
                [
                    ("id", "!=", period.id),
                    ("company_id", "=", period.company_id.id),
                    ("date_start", "<=", period.date_end),
                    ("date_end", ">=", period.date_start),
                ],
                limit=1,
            )
            if overlap:
                raise ValidationError(
                    _("Periode overhead '%s' bertabrakan dengan periode '%s'.")
                    % (period.display_name, overlap.display_name)
                )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                date_start = vals.get("date_start")
                if date_start:
                    start = fields.Date.to_date(date_start)
                    vals["name"] = _("Overhead %s/%s") % (str(start.month).zfill(2), start.year)
        return super().create(vals_list)

    def action_initialize_lines(self):
        for period in self:
            existing_types = period.line_ids.mapped("overhead_type_id")
            types = self.env["mrp.overhead.type"].search(
                [("active", "=", True), ("company_id", "=", period.company_id.id)]
            )
            new_lines = []
            for overhead_type in types:
                if overhead_type in existing_types:
                    continue
                new_lines.append(
                    (
                        0,
                        0,
                        {
                            "overhead_type_id": overhead_type.id,
                            "allocation_basis": overhead_type.allocation_basis,
                            "capitalize_to_inventory": overhead_type.capitalize_to_inventory,
                            "source_account_id": overhead_type.default_source_account_id.id,
                            "absorption_account_id": overhead_type.absorption_account_id.id,
                            "variance_account_id": overhead_type.variance_account_id.id,
                        },
                    )
                )
            if new_lines:
                period.write({"line_ids": new_lines})
        return True

    def action_load_source_entries(self):
        for period in self:
            for line in period.line_ids:
                line._assign_source_move_lines()
        return True

    def action_compute_overhead(self):
        Allocation = self.env["mrp.overhead.allocation.line"]
        for period in self:
            if not period.line_ids:
                period.action_initialize_lines()
            period.action_load_source_entries()
            period.allocation_line_ids.unlink()

            basis_map = defaultdict(list)
            basis_totals = defaultdict(float)
            for production in period._get_done_productions():
                for line in period.line_ids:
                    base_basis_qty = line._get_basis_qty_for_production(production)
                    mo_factor = line._get_mo_factor_for_production(production)
                    basis_qty = base_basis_qty * mo_factor
                    if float_is_zero(basis_qty, precision_digits=4):
                        continue
                    basis_map[line.id].append((production.id, base_basis_qty, mo_factor, basis_qty))
                    basis_totals[line.id] += basis_qty

            values = []
            for line in period.line_ids:
                total_basis = basis_totals.get(line.id, 0.0)
                effective_rate = line.manual_rate if line.rate_mode == "manual" else (
                    line.actual_amount / total_basis if total_basis else 0.0
                )
                for production_id, base_basis_qty, mo_factor, basis_qty in basis_map.get(line.id, []):
                    values.append(
                        {
                            "period_id": period.id,
                            "period_line_id": line.id,
                            "production_id": production_id,
                            "base_basis_qty": base_basis_qty,
                            "mo_factor": mo_factor,
                            "basis_qty": basis_qty,
                            "rate": effective_rate,
                            "applied_amount": basis_qty * effective_rate,
                        }
                    )
            if values:
                Allocation.create(values)
            period.state = "computed"
        return True

    def action_create_adjustment_move(self):
        self.ensure_one()
        if self.adjustment_move_id:
            raise UserError(_("Jurnal adjustment sudah pernah dibuat untuk periode ini."))
        if not self.line_ids:
            raise UserError(_("Belum ada line overhead pada periode ini."))

        move_lines = []
        line_counter = 1
        for line in self.line_ids:
            actual_amount = line.actual_amount
            absorbed_amount = line.absorbed_amount
            variance_amount = line.variance_amount

            if float_is_zero(actual_amount, precision_rounding=self.currency_id.rounding) and float_is_zero(
                absorbed_amount, precision_rounding=self.currency_id.rounding
            ):
                continue

            line._validate_accounts_for_adjustment()
            source_distribution = line._get_source_distribution()

            for account_id, amount in source_distribution.items():
                if float_is_zero(amount, precision_rounding=self.currency_id.rounding):
                    continue
                account = self.env["account.account"].browse(account_id)
                debit = -amount if amount < 0 else 0.0
                credit = amount if amount > 0 else 0.0
                move_lines.append(
                    (0, 0, line._prepare_move_line_vals(account, debit, credit, line_counter, _("Reverse actual overhead")))
                )
                line_counter += 1

            if not float_is_zero(absorbed_amount, precision_rounding=self.currency_id.rounding):
                absorbed_lines = line._prepare_absorbed_move_line_vals(start_sequence=line_counter)
                move_lines.extend(absorbed_lines)
                line_counter += len(absorbed_lines)

            if not float_is_zero(variance_amount, precision_rounding=self.currency_id.rounding):
                debit = variance_amount if variance_amount > 0 else 0.0
                credit = -variance_amount if variance_amount < 0 else 0.0
                move_lines.append(
                    (
                        0,
                        0,
                        line._prepare_move_line_vals(
                            line.variance_account_id,
                            debit,
                            credit,
                            line_counter,
                            _("Overhead variance"),
                        ),
                    )
                )
                line_counter += 1

        if not move_lines:
            raise UserError(_("Tidak ada nominal yang perlu dibuatkan jurnal adjustment."))

        move = self.env["account.move"].create(
            {
                "move_type": "entry",
                "date": self.date_end,
                "journal_id": self.journal_id.id,
                "company_id": self.company_id.id,
                "mrp_overhead_period_id": self.id,
                "ref": self.name,
                "line_ids": move_lines,
            }
        )
        self.adjustment_move_id = move.id
        self.state = "adjusted"
        return {
            "type": "ir.actions.act_window",
            "res_model": "account.move",
            "view_mode": "form",
            "res_id": move.id,
        }

    def action_reset_to_draft(self):
        for period in self:
            if period.adjustment_move_id and period.adjustment_move_id.state == "posted":
                raise UserError(_("Unpost jurnal adjustment terlebih dahulu sebelum reset ke draft."))
            if period.stock_valuation_layer_ids:
                raise UserError(
                    _(
                        "Periode '%s' sudah memiliki stock valuation layer overhead. Reset ke draft diblokir untuk menjaga konsistensi valuation."
                    )
                    % period.display_name
                )
            if period.adjustment_move_id:
                period.adjustment_move_id.unlink()
            period.allocation_line_ids.unlink()
            period.state = "draft"
            period.adjustment_move_id = False
        return True

    def _create_stock_valuation_layers(self, adjustment_move):
        self.ensure_one()
        if "stock.valuation.layer" not in self.env:
            return

        valuation_layers = []
        for line in self.line_ids.filtered(lambda item: item.capitalize_to_inventory):
            for allocation in line.allocation_line_ids:
                existing_layer = self.env["stock.valuation.layer"].search(
                    [("mrp_overhead_allocation_line_id", "=", allocation.id)],
                    limit=1,
                )
                if existing_layer:
                    continue
                layer_vals = line._prepare_stock_valuation_layer_vals(allocation, adjustment_move)
                if layer_vals:
                    valuation_layers.append(layer_vals)

        if valuation_layers:
            self.env["stock.valuation.layer"].create(valuation_layers)

    def action_sync_posted_adjustment_valuation(self):
        for period in self:
            move = period.adjustment_move_id
            if not move or move.state != "posted":
                continue
            period._create_stock_valuation_layers(move)
        return True

    def _get_done_productions(self):
        self.ensure_one()
        start_dt = datetime.combine(fields.Date.to_date(self.date_start), time.min)
        end_dt = datetime.combine(fields.Date.to_date(self.date_end), time.max)
        return self.env["mrp.production"].search(
            [
                ("company_id", "=", self.company_id.id),
                ("state", "=", "done"),
                ("date_finished", ">=", fields.Datetime.to_string(start_dt)),
                ("date_finished", "<=", fields.Datetime.to_string(end_dt)),
            ]
        )


class MrpOverheadPeriodLine(models.Model):
    _name = "mrp.overhead.period.line"
    _description = "MRP Overhead Period Line"
    _order = "period_id, sequence, id"

    period_id = fields.Many2one("mrp.overhead.period", required=True, ondelete="cascade")
    sequence = fields.Integer(default=10)
    company_id = fields.Many2one(related="period_id.company_id", store=True, readonly=True)
    currency_id = fields.Many2one(related="period_id.currency_id", store=True, readonly=True)
    overhead_type_id = fields.Many2one(
        "mrp.overhead.type",
        required=True,
        domain="[('company_id', '=', company_id)]",
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
    capitalize_to_inventory = fields.Boolean(
        string="Capitalize to Inventory",
        default=True,
        help="If enabled, absorbed overhead is posted to finished product valuation account per MO allocation.",
    )
    rate_mode = fields.Selection(
        [("auto", "Auto"), ("manual", "Manual")],
        default="auto",
        required=True,
    )
    manual_rate = fields.Monetary()
    manual_actual_amount = fields.Monetary(
        help="Tambahan nominal manual di luar source journal items yang ditarik otomatis.",
    )
    source_account_id = fields.Many2one(
        "account.account",
        string="Fallback Source Account",
        domain="[('company_id', '=', company_id), ('deprecated', '=', False)]",
    )
    absorption_account_id = fields.Many2one(
        "account.account",
        required=True,
        domain="[('company_id', '=', company_id), ('deprecated', '=', False)]",
    )
    variance_account_id = fields.Many2one(
        "account.account",
        required=True,
        domain="[('company_id', '=', company_id), ('deprecated', '=', False)]",
    )
    source_move_line_ids = fields.One2many(
        "account.move.line",
        "mrp_overhead_period_line_id",
        string="Source Journal Items",
        readonly=True,
    )
    allocation_line_ids = fields.One2many(
        "mrp.overhead.allocation.line",
        "period_line_id",
        string="MO Allocations",
        readonly=True,
    )
    source_actual_amount = fields.Monetary(compute="_compute_amounts")
    actual_amount = fields.Monetary(compute="_compute_amounts")
    basis_qty = fields.Float(compute="_compute_amounts", digits=(16, 4))
    computed_rate = fields.Monetary(compute="_compute_amounts")
    rate = fields.Monetary(compute="_compute_amounts")
    absorbed_amount = fields.Monetary(compute="_compute_amounts")
    variance_amount = fields.Monetary(compute="_compute_amounts")
    source_move_count = fields.Integer(compute="_compute_counts")
    allocation_count = fields.Integer(compute="_compute_counts")

    _sql_constraints = [
        (
            "period_type_unique",
            "unique(period_id, overhead_type_id)",
            "Satu tipe overhead hanya boleh muncul satu kali dalam satu periode.",
        ),
    ]

    @api.onchange("overhead_type_id")
    def _onchange_overhead_type_id(self):
        for line in self:
            if not line.overhead_type_id:
                continue
            line.allocation_basis = line.overhead_type_id.allocation_basis
            line.capitalize_to_inventory = line.overhead_type_id.capitalize_to_inventory
            line.source_account_id = line.overhead_type_id.default_source_account_id
            line.absorption_account_id = line.overhead_type_id.absorption_account_id
            line.variance_account_id = line.overhead_type_id.variance_account_id

    @api.depends(
        "manual_actual_amount",
        "manual_rate",
        "rate_mode",
        "source_move_line_ids.balance",
        "source_move_line_ids.account_id",
        "allocation_line_ids.basis_qty",
        "allocation_line_ids.applied_amount",
    )
    def _compute_amounts(self):
        for line in self:
            source_lines = line.source_move_line_ids.filtered(
                lambda aml: aml.balance > 0
                and aml.account_id.internal_type not in ("receivable", "payable", "liquidity")
            )
            source_amount = sum(source_lines.mapped("balance"))
            basis_qty = sum(line.allocation_line_ids.mapped("basis_qty"))
            absorbed_amount = sum(line.allocation_line_ids.mapped("applied_amount"))
            actual_amount = source_amount + line.manual_actual_amount
            computed_rate = actual_amount / basis_qty if basis_qty else 0.0
            rate = line.manual_rate if line.rate_mode == "manual" else computed_rate
            if line.rate_mode == "manual" and basis_qty:
                absorbed_amount = basis_qty * line.manual_rate
            line.source_actual_amount = source_amount
            line.actual_amount = actual_amount
            line.basis_qty = basis_qty
            line.computed_rate = computed_rate
            line.rate = rate
            line.absorbed_amount = absorbed_amount
            line.variance_amount = actual_amount - absorbed_amount

    @api.depends("source_move_line_ids", "allocation_line_ids")
    def _compute_counts(self):
        for line in self:
            line.source_move_count = len(line.source_move_line_ids)
            line.allocation_count = len(line.allocation_line_ids)

    def _assign_source_move_lines(self):
        AccountMoveLine = self.env["account.move.line"]
        for line in self:
            domain = [
                ("company_id", "=", line.company_id.id),
                ("parent_state", "=", "posted"),
                ("date", ">=", line.period_id.date_start),
                ("date", "<=", line.period_id.date_end),
                ("display_type", "=", False),
                ("mrp_overhead_type_id", "=", line.overhead_type_id.id),
                ("mrp_overhead_period_line_id", "in", [False, line.id]),
                ("balance", ">", 0.0),
            ]
            move_lines = AccountMoveLine.search(domain).filtered(
                lambda aml: aml.account_id.internal_type not in ("receivable", "payable", "liquidity")
            )
            stale_lines = line.source_move_line_ids - move_lines
            if stale_lines:
                stale_lines.write(
                    {
                        "mrp_overhead_period_line_id": False,
                        "mrp_overhead_period_id": False,
                    }
                )
            if move_lines:
                move_lines.write(
                    {
                        "mrp_overhead_period_line_id": line.id,
                        "mrp_overhead_period_id": line.period_id.id,
                    }
                )

    def _get_basis_qty_for_production(self, production):
        self.ensure_one()
        if self.allocation_basis == "mo":
            return 1.0
        if self.allocation_basis == "hour":
            return self._get_hours_for_production(production)
        return self._get_weight_for_production(production)

    def _get_mo_factor_for_production(self, production):
        self.ensure_one()
        factor_mode = self.overhead_type_id.mo_factor_mode
        if factor_mode == "electricity":
            return production.overhead_electricity_factor
        if factor_mode == "labor":
            return production.overhead_labor_factor
        return 1.0

    def _get_weight_for_production(self, production):
        if "qty_produced" in production._fields and production.qty_produced:
            return production.qty_produced

        finished_qty = 0.0
        finished_moves = production.move_finished_ids.filtered(
            lambda move: move.product_id == production.product_id and move.state == "done"
        )
        if finished_moves:
            for move in finished_moves:
                finished_qty += move.quantity_done or move.product_uom_qty or 0.0
        return finished_qty or production.product_qty or 0.0

    def _get_hours_for_production(self, production):
        total_minutes = 0.0
        if "workorder_ids" in production._fields and production.workorder_ids:
            done_workorders = production.workorder_ids.filtered(lambda wo: wo.state == "done")
            workorders = done_workorders or production.workorder_ids
            for workorder in workorders:
                if "duration" in workorder._fields and workorder.duration:
                    total_minutes += workorder.duration
                elif "duration_expected" in workorder._fields and workorder.duration_expected:
                    total_minutes += workorder.duration_expected
        if not total_minutes and production.date_planned_start and production.date_finished:
            total_minutes = (production.date_finished - production.date_planned_start).total_seconds() / 60.0
        return total_minutes / 60.0

    def _validate_accounts_for_adjustment(self):
        self.ensure_one()
        missing = []
        if not self.absorption_account_id:
            missing.append(_("absorption account"))
        if not self.variance_account_id:
            missing.append(_("variance account"))
        if not self._get_source_distribution():
            missing.append(_("source account / source journal items"))
        if missing:
            raise UserError(
                _("Line overhead '%s' belum lengkap: %s.") % (self.overhead_type_id.display_name, ", ".join(missing))
            )

    def _get_source_distribution(self):
        self.ensure_one()
        distribution = defaultdict(float)
        source_lines = self.source_move_line_ids.filtered(
            lambda aml: aml.balance > 0
            and aml.account_id.internal_type not in ("receivable", "payable", "liquidity")
        )
        for aml in source_lines:
            distribution[aml.account_id.id] += aml.balance
        if not distribution and self.manual_actual_amount:
            account = self.source_account_id or self.overhead_type_id.default_source_account_id
            if account:
                distribution[account.id] += self.actual_amount
        elif distribution and self.manual_actual_amount:
            account = self.source_account_id or self.overhead_type_id.default_source_account_id
            if not account:
                raise UserError(
                    _(
                        "Fallback source account wajib diisi pada line '%s' jika memakai tambahan actual amount manual."
                    )
                    % self.overhead_type_id.display_name
                )
            distribution[account.id] += self.manual_actual_amount
        return distribution

    def _prepare_move_line_vals(self, account, debit, credit, sequence, label):
        self.ensure_one()
        return {
            "name": "%s - %s" % (self.overhead_type_id.display_name, label),
            "account_id": account.id,
            "debit": debit,
            "credit": credit,
            "sequence": sequence,
        }

    def _get_production_valuation_account(self, production):
        self.ensure_one()
        product = production.product_id
        product_account = False
        category_account = False
        if "property_stock_valuation_account_id" in product._fields:
            product_account = product.property_stock_valuation_account_id
        if "property_stock_valuation_account_id" in product.categ_id._fields:
            category_account = product.categ_id.property_stock_valuation_account_id
        return product_account or category_account

    def _prepare_absorbed_move_line_vals(self, start_sequence=1):
        self.ensure_one()
        rounding = self.currency_id.rounding
        values = []
        sequence = start_sequence

        if self.capitalize_to_inventory and self.allocation_line_ids:
            for allocation in self.allocation_line_ids.sorted(key=lambda alloc: (alloc.production_id.id, alloc.id)):
                amount = allocation.applied_amount
                if float_is_zero(amount, precision_rounding=rounding):
                    continue
                target_account = self._get_production_valuation_account(allocation.production_id) or self.absorption_account_id
                debit = amount if amount > 0 else 0.0
                credit = -amount if amount < 0 else 0.0
                label = _("Absorbed overhead (%s)") % allocation.production_id.display_name
                values.append((0, 0, self._prepare_move_line_vals(target_account, debit, credit, sequence, label)))
                sequence += 1

        if values:
            return values

        amount = self.absorbed_amount
        debit = amount if amount > 0 else 0.0
        credit = -amount if amount < 0 else 0.0
        return [
            (
                0,
                0,
                self._prepare_move_line_vals(
                    self.absorption_account_id,
                    debit,
                    credit,
                    start_sequence,
                    _("Absorbed overhead"),
                ),
            )
        ]

    def _prepare_stock_valuation_layer_vals(self, allocation, adjustment_move):
        self.ensure_one()
        amount = allocation.applied_amount
        if float_is_zero(amount, precision_rounding=self.currency_id.rounding):
            return False

        production = allocation.production_id
        product = production.product_id
        if not product:
            return False

        category = product.categ_id
        if "property_valuation" in category._fields and category.property_valuation != "real_time":
            return False

        description = _("Overhead absorption %s - %s - %s") % (
            self.period_id.display_name,
            self.overhead_type_id.display_name,
            production.display_name,
        )

        vals = {
            "company_id": self.company_id.id,
            "product_id": product.id,
            "quantity": 0.0,
            "value": amount,
            "unit_cost": amount,
            "description": description,
            "mrp_overhead_period_id": self.period_id.id,
            "mrp_overhead_period_line_id": self.id,
            "mrp_overhead_allocation_line_id": allocation.id,
            "mrp_production_id": production.id,
        }

        StockValuationLayer = self.env["stock.valuation.layer"]
        if "account_move_id" in StockValuationLayer._fields:
            vals["account_move_id"] = adjustment_move.id
        if "stock_move_id" in StockValuationLayer._fields:
            finished_move = production.move_finished_ids.filtered(lambda move: move.state == "done")[:1]
            if finished_move:
                vals["stock_move_id"] = finished_move.id
        if "remaining_qty" in StockValuationLayer._fields:
            vals["remaining_qty"] = 0.0
        if "remaining_value" in StockValuationLayer._fields:
            vals["remaining_value"] = 0.0

        return vals


class MrpOverheadAllocationLine(models.Model):
    _name = "mrp.overhead.allocation.line"
    _description = "MRP Overhead Allocation Line"
    _order = "period_id, period_line_id, production_id"

    period_id = fields.Many2one("mrp.overhead.period", required=True, ondelete="cascade")
    period_line_id = fields.Many2one("mrp.overhead.period.line", required=True, ondelete="cascade")
    company_id = fields.Many2one(related="period_id.company_id", store=True, readonly=True)
    currency_id = fields.Many2one(related="period_id.currency_id", store=True, readonly=True)
    production_id = fields.Many2one("mrp.production", required=True, ondelete="cascade")
    product_id = fields.Many2one(related="production_id.product_id", store=True, readonly=True)
    date_finished = fields.Datetime(related="production_id.date_finished", store=True, readonly=True)
    base_basis_qty = fields.Float(required=True, digits=(16, 4), default=0.0)
    mo_factor = fields.Float(required=True, digits=(16, 4), default=1.0)
    basis_qty = fields.Float(required=True, digits=(16, 4))
    rate = fields.Monetary(required=True)
    applied_amount = fields.Monetary(required=True)

    _sql_constraints = [
        (
            "period_line_production_unique",
            "unique(period_line_id, production_id)",
            "Satu MO hanya boleh mendapat satu alokasi untuk satu line overhead dalam satu periode.",
        ),
    ]
