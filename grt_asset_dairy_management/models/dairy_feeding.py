from collections import defaultdict

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class DairyFeedRecord(models.Model):
    _name = 'dairy.feed.record'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Pemberian Pakan Sapi'
    _order = 'date desc, id desc'
    _rec_name = 'name'

    name = fields.Char(string='Nomor', copy=False, readonly=True, default='New')
    date = fields.Date(string='Tanggal', required=True, default=fields.Date.context_today, tracking=True)
    barn_id = fields.Many2one('kandang.sapi.perah', string='Kandang')
    line_ids = fields.One2many('dairy.feed.record.line', 'feed_record_id', string='Detail Pakan')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company, required=True)
    journal_move_id = fields.Many2one('account.move', string='Jurnal', copy=False, readonly=True)
    stock_move_ids = fields.Many2many('stock.move', string='Stock Moves', readonly=True, copy=False)
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
            vals['name'] = self.env['ir.sequence'].next_by_code('dairy.feed.record') or 'New'
        return super(DairyFeedRecord, self).create(vals)

    @api.onchange('barn_id')
    def _onchange_barn_id(self):
        if self.barn_id and not self.line_ids:
            self.line_ids = [(0, 0, {
                'sapi_id': cow.id,
            }) for cow in self.barn_id.sapi_kandang_ids]

    def _get_required_company_settings(self):
        self.ensure_one()
        company = self.company_id
        missing = []
        if not company.dairy_feed_source_location_id:
            missing.append(_('Lokasi sumber pakan'))
        if not company.dairy_feed_consumption_location_id:
            missing.append(_('Lokasi konsumsi pakan'))
        if not company.dairy_feed_journal_id:
            missing.append(_('Jurnal pakan'))
        if not company.dairy_feed_inventory_account_id:
            missing.append(_('Akun persediaan pakan'))
        if not company.dairy_feed_asset_account_id:
            missing.append(_('Akun asset biologis belum produksi'))
        if not company.dairy_feed_expense_account_id:
            missing.append(_('Akun beban pakan produksi'))
        if missing:
            raise UserError(_('Konfigurasi Dairy Management belum lengkap:\n- %s') % '\n- '.join(missing))
        return company

    def _check_manual_journal_valuation_policy(self, company):
        self.ensure_one()
        products = self.env['product.product']
        for line in self.line_ids:
            if line.concentrate_qty:
                products |= company.dairy_concentrate_product_id
            if line.grass_qty:
                products |= company.dairy_grass_product_id

        realtime_products = products.filtered(lambda p: p and p.categ_id.property_valuation == 'real_time')
        if realtime_products:
            raise UserError(_(
                'Produk berikut memakai automated valuation (real-time): %s\n'
                'Modul ini juga membuat jurnal manual pakan, sehingga berisiko terjadi double posting.\n'
                'Gunakan kategori produk dengan manual valuation atau sesuaikan kebijakan jurnal modul.'
            ) % ', '.join(realtime_products.mapped('display_name')))

    def action_post(self):
        StockMove = self.env['stock.move']
        for record in self:
            if not record.line_ids:
                raise UserError(_('Detail pemberian pakan belum diisi.'))
            company = record._get_required_company_settings()
            record._check_manual_journal_valuation_policy(company)
            move_lines = []
            journal_totals = defaultdict(float)
            created_stock_moves = StockMove

            for line in record.line_ids:
                line._validate_line_before_post()
                created_stock_moves |= line._create_stock_moves(company)
                debit_account = company.dairy_feed_expense_account_id if line.sapi_id.dairy_is_productive else company.dairy_feed_asset_account_id
                credit_account = company.dairy_feed_inventory_account_id
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
                'journal_id': company.dairy_feed_journal_id.id,
                'line_ids': move_lines,
            })
            move.action_post()

            record.write({
                'journal_move_id': move.id,
                'stock_move_ids': [(6, 0, created_stock_moves.ids)],
                'state': 'posted',
            })

    def action_cancel(self):
        for record in self:
            if record.journal_move_id and record.journal_move_id.state == 'posted':
                raise UserError(_('Jurnal yang sudah diposting tidak dibatalkan otomatis oleh modul ini.'))
            record.state = 'cancel'

    def action_reset_to_draft(self):
        for record in self:
            if record.state == 'cancel':
                record.state = 'draft'


class DairyFeedRecordLine(models.Model):
    _name = 'dairy.feed.record.line'
    _description = 'Detail Pemberian Pakan'

    feed_record_id = fields.Many2one('dairy.feed.record', string='Pemberian Pakan', required=True, ondelete='cascade')
    sapi_id = fields.Many2one('sapi', string='Sapi', required=True)
    kandang_id = fields.Many2one('kandang.sapi.perah', string='Kandang', related='sapi_id.kandang_id', store=True, readonly=True)
    weight = fields.Float(string='Berat (Kg)', compute='_compute_weight', store=True)
    concentrate_qty = fields.Float(string='Konsentrat (Kg)', required=True)
    grass_qty = fields.Float(string='Rumput (Kg)', required=True)
    concentrate_cost = fields.Monetary(string='Nilai Konsentrat', compute='_compute_amounts', store=True)
    grass_cost = fields.Monetary(string='Nilai Rumput', compute='_compute_amounts', store=True)
    total_amount = fields.Monetary(string='Nilai Total', compute='_compute_amounts', store=True)
    currency_id = fields.Many2one('res.currency', related='feed_record_id.currency_id', readonly=True)
    note = fields.Char(string='Catatan')

    @api.depends('sapi_id.dairy_current_weight')
    def _compute_weight(self):
        for line in self:
            line.weight = line.sapi_id.dairy_current_weight

    @api.depends('concentrate_qty', 'grass_qty', 'feed_record_id.company_id.dairy_concentrate_product_id.standard_price', 'feed_record_id.company_id.dairy_grass_product_id.standard_price')
    def _compute_amounts(self):
        for line in self:
            concentrate_cost = line.concentrate_qty * (line.feed_record_id.company_id.dairy_concentrate_product_id.standard_price or 0.0)
            grass_cost = line.grass_qty * (line.feed_record_id.company_id.dairy_grass_product_id.standard_price or 0.0)
            line.concentrate_cost = concentrate_cost
            line.grass_cost = grass_cost
            line.total_amount = concentrate_cost + grass_cost

    @api.onchange('sapi_id')
    def _onchange_sapi_id(self):
        if self.sapi_id:
            self.concentrate_qty = self.sapi_id.dairy_concentrate_need
            self.grass_qty = self.sapi_id.dairy_grass_need

    def _validate_line_before_post(self):
        self.ensure_one()
        company = self.feed_record_id.company_id
        if not self.sapi_id:
            raise UserError(_('Sapi pada detail pakan wajib diisi.'))
        if self.concentrate_qty < 0 or self.grass_qty < 0:
            raise UserError(_('Qty pakan tidak boleh negatif.'))
        if self.concentrate_qty and not company.dairy_concentrate_product_id:
            raise UserError(_('Produk konsentrat belum disetting.'))
        if self.grass_qty and not company.dairy_grass_product_id:
            raise UserError(_('Produk rumput belum disetting.'))

    def _prepare_stock_move_vals(self, product, qty, company):
        self.ensure_one()
        return {
            'name': '%s - %s' % (self.feed_record_id.name, self.sapi_id.display_name),
            'company_id': company.id,
            'date': self.feed_record_id.date,
            'product_id': product.id,
            'product_uom': product.uom_id.id,
            'product_uom_qty': qty,
            'location_id': company.dairy_feed_source_location_id.id,
            'location_dest_id': company.dairy_feed_consumption_location_id.id,
            'reference': self.feed_record_id.name,
            'origin': self.feed_record_id.name,
        }

    def _create_stock_moves(self, company):
        self.ensure_one()
        StockMove = self.env['stock.move']
        created_moves = StockMove
        product_map = [
            (company.dairy_concentrate_product_id, self.concentrate_qty),
            (company.dairy_grass_product_id, self.grass_qty),
        ]
        for product, qty in product_map:
            if not product or not qty:
                continue
            move = StockMove.create(self._prepare_stock_move_vals(product, qty, company))
            move._action_confirm()
            move._action_done()
            created_moves |= move
        return created_moves
