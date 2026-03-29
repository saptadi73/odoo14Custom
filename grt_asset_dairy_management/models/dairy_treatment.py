from collections import defaultdict

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class DairyTreatmentRecord(models.Model):
    _name = 'dairy.treatment.record'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Tindakan Vitamin dan Inseminasi Sapi'
    _order = 'date desc, id desc'
    _rec_name = 'name'

    name = fields.Char(string='Nomor', copy=False, readonly=True, default='New')
    date = fields.Date(string='Tanggal', required=True, default=fields.Date.context_today, tracking=True)
    barn_id = fields.Many2one('kandang.sapi.perah', string='Kandang')
    bag_location_id = fields.Many2one('stock.location', string='Lokasi Tas Petugas', domain=[('usage', '=', 'internal')])
    person_in_charge = fields.Char(string='Petugas')
    line_ids = fields.One2many('dairy.treatment.record.line', 'treatment_record_id', string='Detail Tindakan')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company, required=True)
    journal_move_id = fields.Many2one('account.move', string='Jurnal', copy=False, readonly=True)
    reverse_journal_move_id = fields.Many2one('account.move', string='Jurnal Reverse', copy=False, readonly=True)
    stock_move_ids = fields.Many2many('stock.move', string='Stock Moves', readonly=True, copy=False)
    reverse_stock_move_ids = fields.Many2many('stock.move', 'dairy_treatment_reverse_stock_rel', 'treatment_id', 'move_id', string='Reverse Stock Moves', readonly=True, copy=False)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('posted', 'Posted'),
        ('cancel', 'Cancel'),
    ], string='Status', default='draft', tracking=True)
    note = fields.Text(string='Catatan')
    total_amount = fields.Monetary(string='Nilai Total', compute='_compute_total_amount', store=True)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', readonly=True)

    @api.depends('line_ids.total_amount')
    def _compute_total_amount(self):
        for record in self:
            record.total_amount = sum(record.line_ids.mapped('total_amount'))

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('dairy.treatment.record') or 'New'
        return super(DairyTreatmentRecord, self).create(vals)

    @api.onchange('barn_id')
    def _onchange_barn_id(self):
        if self.barn_id and not self.line_ids:
            self.line_ids = [(0, 0, {
                'sapi_id': cow.id,
                'treatment_type': 'vitamin',
            }) for cow in self.barn_id.sapi_kandang_ids]

    def action_open_bag_location_wizard(self):
        self.ensure_one()
        return {
            'name': _('Buat Lokasi Tas Petugas'),
            'type': 'ir.actions.act_window',
            'res_model': 'dairy.bag.location.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'active_model': self._name,
                'active_id': self.id,
            },
        }

    def _get_journal(self):
        self.ensure_one()
        return self.company_id.dairy_treatment_journal_id or self.company_id.dairy_feed_journal_id

    def _get_medical_consumption_location(self):
        self.ensure_one()
        return self.company_id.dairy_medical_consumption_location_id or self.company_id.dairy_vitamin_consumption_location_id

    def _get_required_company_settings(self):
        self.ensure_one()
        company = self.company_id
        missing = []
        if not self._get_journal():
            missing.append(_('Jurnal vitamin dan inseminasi'))
        if not company.dairy_feed_asset_account_id:
            missing.append(_('Akun asset biologis belum produksi'))
        if not self._get_medical_consumption_location():
            missing.append(_('Lokasi konsumsi medis'))
        if missing:
            raise UserError(_('Konfigurasi Dairy Management belum lengkap:\n- %s') % '\n- '.join(missing))
        return company

    def action_post(self):
        StockMove = self.env['stock.move']
        for record in self:
            if not record.line_ids:
                raise UserError(_('Detail vitamin/inseminasi belum diisi.'))
            company = record._get_required_company_settings()
            move_lines = []
            journal_totals = defaultdict(float)
            created_stock_moves = StockMove

            for line in record.line_ids:
                debit_account, credit_account = line._get_accounts(company)
                line._validate_line_before_post(company, debit_account, credit_account)
                created_stock_moves |= line._create_stock_moves(company)
                journal_totals[debit_account.id] += line.total_amount
                journal_totals[credit_account.id] -= line.total_amount

            for account_id, amount in journal_totals.items():
                if amount > 0:
                    move_lines.append((0, 0, {
                        'name': record.name,
                        'account_id': account_id,
                        'debit': amount,
                        'credit': 0.0,
                        'analytic_account_id': company.dairy_analytic_account_id.id or False,
                    }))
                elif amount < 0:
                    move_lines.append((0, 0, {
                        'name': record.name,
                        'account_id': account_id,
                        'debit': 0.0,
                        'credit': abs(amount),
                        'analytic_account_id': company.dairy_analytic_account_id.id or False,
                    }))

            move = self.env['account.move'].create({
                'date': record.date,
                'ref': record.name,
                'journal_id': record._get_journal().id,
                'line_ids': move_lines,
            })
            move.action_post()

            record.write({
                'journal_move_id': move.id,
                'stock_move_ids': [(6, 0, created_stock_moves.ids)],
                'state': 'posted',
            })

    def _create_reverse_stock_moves(self):
        self.ensure_one()
        StockMove = self.env['stock.move']
        created_moves = StockMove
        for move in self.stock_move_ids.filtered(lambda m: m.state == 'done'):
            reverse_move = StockMove.create({
                'name': '%s REV' % (move.name or self.name),
                'company_id': move.company_id.id,
                'date': fields.Datetime.now(),
                'product_id': move.product_id.id,
                'product_uom': move.product_uom.id,
                'product_uom_qty': move.product_uom_qty,
                'location_id': move.location_dest_id.id,
                'location_dest_id': move.location_id.id,
                'reference': '%s/REV' % self.name,
                'origin': self.name,
            })
            reverse_move._action_confirm()
            reverse_move._action_done()
            created_moves |= reverse_move
        return created_moves

    def _create_reverse_journal_move(self):
        self.ensure_one()
        move = self.journal_move_id
        if not move:
            return self.env['account.move']
        reverse = self.env['account.move'].create({
            'date': fields.Date.context_today(self),
            'ref': '%s/REV' % (move.ref or self.name),
            'journal_id': move.journal_id.id,
            'line_ids': [
                (0, 0, {
                    'name': line.name,
                    'account_id': line.account_id.id,
                    'debit': line.credit,
                    'credit': line.debit,
                    'partner_id': line.partner_id.id,
                    'analytic_account_id': line.analytic_account_id.id,
                }) for line in move.line_ids if not line.exclude_from_invoice_tab
            ],
        })
        reverse.action_post()
        return reverse

    def action_cancel(self):
        for record in self:
            if record.state != 'posted':
                record.state = 'cancel'
                continue
            reverse_stock_moves = record._create_reverse_stock_moves()
            reverse_journal = record._create_reverse_journal_move() if record.journal_move_id else self.env['account.move']
            record.write({
                'reverse_stock_move_ids': [(6, 0, reverse_stock_moves.ids)],
                'reverse_journal_move_id': reverse_journal.id or False,
                'state': 'cancel',
            })

    def action_reset_to_draft(self):
        for record in self:
            if record.state == 'cancel':
                record.state = 'draft'


class DairyTreatmentRecordLine(models.Model):
    _name = 'dairy.treatment.record.line'
    _description = 'Detail Tindakan Vitamin dan Inseminasi'

    treatment_record_id = fields.Many2one('dairy.treatment.record', string='Tindakan', required=True, ondelete='cascade')
    treatment_date = fields.Date(related='treatment_record_id.date', string='Tanggal', store=True, readonly=True)
    treatment_state = fields.Selection(related='treatment_record_id.state', string='Status', store=True, readonly=True)
    sapi_id = fields.Many2one('sapi', string='Sapi', required=True)
    kandang_id = fields.Many2one('kandang.sapi.perah', string='Kandang', related='sapi_id.kandang_id', store=True, readonly=True)
    treatment_type = fields.Selection([
        ('vitamin', 'Vitamin'),
        ('insemination', 'Inseminasi'),
    ], string='Jenis Tindakan', required=True, default='vitamin')
    product_id = fields.Many2one('product.product', string='Produk/Jasa', domain=[('type', 'in', ['product', 'consu', 'service'])])
    qty = fields.Float(string='Qty', default=1.0, required=True, help='Gunakan sesuai UoM produk, misalnya ml atau cc.')
    product_uom_id = fields.Many2one('uom.uom', string='Satuan', related='product_id.uom_id', readonly=True)
    unit_cost = fields.Monetary(string='Biaya Satuan', required=True, default=0.0)
    total_amount = fields.Monetary(string='Nilai Total', compute='_compute_total_amount', store=True)
    currency_id = fields.Many2one('res.currency', related='treatment_record_id.currency_id', readonly=True)
    note = fields.Char(string='Catatan')

    @api.depends('qty', 'unit_cost')
    def _compute_total_amount(self):
        for line in self:
            line.total_amount = (line.qty or 0.0) * (line.unit_cost or 0.0)

    @api.onchange('treatment_type')
    def _onchange_treatment_type(self):
        company = self.treatment_record_id.company_id or self.env.company
        if self.treatment_type == 'vitamin':
            self.product_id = company.dairy_vitamin_product_id
        elif self.treatment_type == 'insemination':
            self.product_id = company.dairy_insemination_product_id
        if self.product_id:
            self.unit_cost = self.product_id.standard_price or self.product_id.lst_price or 0.0

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.unit_cost = self.product_id.standard_price or self.product_id.lst_price or 0.0

    def _requires_inventory_link(self):
        self.ensure_one()
        return bool(self.product_id) and self.product_id.type in ('product', 'consu')

    def _get_available_bag_qty(self):
        self.ensure_one()
        bag_location = self.treatment_record_id.bag_location_id
        if not bag_location or not self.product_id:
            return 0.0
        quants = self.env['stock.quant'].read_group(
            [('location_id', 'child_of', bag_location.id), ('product_id', '=', self.product_id.id)],
            ['quantity:sum'],
            []
        )
        return quants[0]['quantity'] if quants else 0.0

    def _get_accounts(self, company):
        self.ensure_one()
        if self.treatment_type == 'vitamin':
            expense_account = company.dairy_vitamin_expense_account_id or company.dairy_feed_expense_account_id
            credit_account = company.dairy_vitamin_credit_account_id
        else:
            expense_account = company.dairy_insemination_expense_account_id or company.dairy_feed_expense_account_id
            credit_account = company.dairy_insemination_credit_account_id
        debit_account = expense_account if self.sapi_id.dairy_is_productive else company.dairy_feed_asset_account_id
        return debit_account, credit_account

    def _validate_line_before_post(self, company, debit_account, credit_account):
        self.ensure_one()
        if not self.sapi_id:
            raise UserError(_('Sapi pada detail tindakan wajib diisi.'))
        if self.qty <= 0:
            raise UserError(_('Qty tindakan harus lebih besar dari 0.'))
        if self.unit_cost < 0:
            raise UserError(_('Biaya satuan tidak boleh negatif.'))
        if self._requires_inventory_link():
            if self.product_id.categ_id.property_valuation == 'real_time':
                raise UserError(_(
                    'Produk %s memakai automated valuation (real-time).\n'
                    'Modul ini juga membuat jurnal manual treatment, sehingga berisiko double posting.\n'
                    'Gunakan kategori produk dengan manual valuation atau sesuaikan kebijakan jurnal modul.'
                ) % self.product_id.display_name)
            if not self.treatment_record_id.bag_location_id:
                raise UserError(_('Lokasi tas petugas wajib diisi untuk produk stok vitamin atau inseminasi.'))
            available_qty = self._get_available_bag_qty()
            if available_qty < self.qty:
                raise UserError(_(
                    'Stok pada tas petugas tidak mencukupi untuk produk %s. Tersedia %s %s, dibutuhkan %s %s.'
                ) % (
                    self.product_id.display_name,
                    available_qty,
                    self.product_uom_id.display_name or '',
                    self.qty,
                    self.product_uom_id.display_name or '',
                ))
        if not debit_account:
            raise UserError(_('Akun debit tindakan belum lengkap untuk jenis %s.') % dict(self._fields['treatment_type'].selection).get(self.treatment_type))
        if not credit_account:
            raise UserError(_('Akun kredit tindakan belum lengkap untuk jenis %s.') % dict(self._fields['treatment_type'].selection).get(self.treatment_type))

    def _prepare_stock_move_vals(self, product, qty, company):
        self.ensure_one()
        destination = self.treatment_record_id._get_medical_consumption_location()
        return {
            'name': '%s - %s - %s' % (self.treatment_record_id.name, self.sapi_id.display_name, dict(self._fields['treatment_type'].selection).get(self.treatment_type)),
            'company_id': company.id,
            'date': self.treatment_record_id.date,
            'product_id': product.id,
            'product_uom': product.uom_id.id,
            'product_uom_qty': qty,
            'location_id': self.treatment_record_id.bag_location_id.id,
            'location_dest_id': destination.id,
            'reference': self.treatment_record_id.name,
            'origin': self.treatment_record_id.name,
        }

    def _create_stock_moves(self, company):
        self.ensure_one()
        StockMove = self.env['stock.move']
        created_moves = StockMove
        if not self._requires_inventory_link():
            return created_moves
        move = StockMove.create(self._prepare_stock_move_vals(self.product_id, self.qty, company))
        move._action_confirm()
        move._action_done()
        created_moves |= move
        return created_moves
