from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class DairyCowMixin(models.Model):
    _inherit = 'sapi'

    dairy_asset_code = fields.Char(string='Kode Asset', copy=False, readonly=True, default='New')
    dairy_receipt_date = fields.Date(string='Tanggal Penerimaan')
    dairy_initial_weight = fields.Float(string='Berat Badan Awal (Kg)')
    dairy_current_weight = fields.Float(
        string='Berat Badan Terkini (Kg)',
        compute='_compute_dairy_current_weight',
        store=True,
    )
    dairy_acquisition_value = fields.Monetary(string='Nilai Perolehan', currency_field='dairy_currency_id')
    dairy_salvage_value = fields.Monetary(string='Nilai Afkir / Nilai Akhir', currency_field='dairy_currency_id')
    dairy_depreciation_months = fields.Integer(string='Lama Penyusutan (Bulan)', default=24)
    dairy_production_date = fields.Date(string='Tanggal Mulai Produksi')
    dairy_is_productive = fields.Boolean(
        string='Sudah Produksi',
        compute='_compute_dairy_is_productive',
        store=True,
    )
    dairy_lifecycle_state = fields.Selection([
        ('draft', 'Draft'),
        ('growing', 'Belum Produksi'),
        ('pregnant', 'Bunting'),
        ('production', 'Produksi'),
        ('dry', 'Kering'),
        ('disposed', 'Afkir'),
        ('dead', 'Mati'),
    ], string='Siklus Sapi', default='growing', tracking=True)
    dairy_weight_line_ids = fields.One2many(
        'dairy.cow.weight',
        'sapi_id',
        string='Riwayat Timbang',
    )
    dairy_status_history_ids = fields.One2many(
        'dairy.cow.status.history',
        'sapi_id',
        string='Riwayat Status',
    )
    dairy_birth_history_ids = fields.One2many(
        'dairy.cow.birth.history',
        'sapi_id',
        string='Riwayat Melahirkan',
    )
    dairy_feed_line_ids = fields.One2many(
        'dairy.feed.record.line',
        'sapi_id',
        string='Riwayat Pakan',
    )
    dairy_treatment_line_ids = fields.One2many(
        'dairy.treatment.record.line',
        'sapi_id',
        string='Riwayat Vitamin dan Inseminasi',
    )
    dairy_asset_id = fields.Many2one(
        'account.asset.asset',
        string='Asset Penyusutan',
        copy=False,
    )
    dairy_transition_move_id = fields.Many2one(
        'account.move',
        string='Jurnal Reklasifikasi ke Asset Produksi',
        copy=False,
        readonly=True,
    )
    dairy_currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        related='company_id.currency_id',
        readonly=True,
    )
    dairy_age_months = fields.Float(
        string='Umur (Bulan)',
        compute='_compute_dairy_age_months',
        store=True,
    )
    dairy_feed_calculation_basis = fields.Selection(
        [
            ('weight', 'Berat Badan'),
            ('age', 'Umur'),
        ],
        string='Dasar Konsumsi Pakan',
        default='weight',
        required=True,
        help='Menentukan apakah kebutuhan pakan default sapi dihitung berdasarkan berat badan atau umur.',
    )
    dairy_feed_reference_id = fields.Many2one(
        'dairy.feed.reference',
        string='Referensi Pakan',
        compute='_compute_dairy_feed_reference_id',
        store=True,
    )
    dairy_bcs_reference_id = fields.Many2one(
        'dairy.bcs.reference',
        string='BCS',
    )
    dairy_capitalized_cost_value = fields.Monetary(
        string='Biaya Kapitalisasi Pra-Produksi',
        currency_field='dairy_currency_id',
        compute='_compute_capitalization_values',
        store=True,
    )
    dairy_total_book_basis_value = fields.Monetary(
        string='Dasar Nilai Buku',
        currency_field='dairy_currency_id',
        compute='_compute_capitalization_values',
        store=True,
    )
    dairy_market_weight = fields.Float(
        string='Bobot Pasar Acuan (Kg)',
        compute='_compute_market_values',
        store=True,
    )
    dairy_market_value = fields.Monetary(
        string='Nilai Pasar',
        currency_field='dairy_currency_id',
        compute='_compute_market_values',
        store=True,
    )
    dairy_book_value = fields.Monetary(
        string='Nilai Buku',
        currency_field='dairy_currency_id',
        compute='_compute_market_values',
        store=True,
    )
    dairy_chkpn_value = fields.Monetary(
        string='CHKPN',
        currency_field='dairy_currency_id',
        compute='_compute_market_values',
        store=True,
        help='Allowance for Impairment Losses = selisih nilai buku di atas nilai pasar.',
    )
    dairy_recognized_chkpn_value = fields.Monetary(
        string='CHKPN Diakui',
        currency_field='dairy_currency_id',
        default=0.0,
        copy=False,
    )
    dairy_valuation_history_ids = fields.One2many(
        'dairy.valuation.history',
        'sapi_id',
        string='Riwayat Valuasi',
    )
    dairy_concentrate_need = fields.Float(
        string='Kebutuhan Konsentrat (Kg)',
        compute='_compute_feed_requirements',
        store=True,
    )
    dairy_grass_need = fields.Float(
        string='Kebutuhan Rumput (Kg)',
        compute='_compute_feed_requirements',
        store=True,
    )

    @api.depends('dairy_weight_line_ids.weight', 'dairy_weight_line_ids.date', 'bobot', 'dairy_initial_weight')
    def _compute_dairy_current_weight(self):
        for cow in self:
            latest_line = cow.dairy_weight_line_ids.sorted(lambda line: (line.date or fields.Date.today(), line.id), reverse=True)[:1]
            cow.dairy_current_weight = latest_line.weight if latest_line else (cow.bobot or cow.dairy_initial_weight or 0.0)

    @api.depends('date_of_birth')
    def _compute_dairy_age_months(self):
        for cow in self:
            if cow.date_of_birth:
                start = cow.date_of_birth
                today = fields.Date.context_today(cow)
                days = (today - start).days
                cow.dairy_age_months = round(days / 30.0, 2) if days >= 0 else 0.0
            else:
                cow.dairy_age_months = 0.0

    @api.depends('dairy_age_months', 'dairy_current_weight', 'dairy_feed_calculation_basis')
    def _compute_dairy_feed_reference_id(self):
        FeedRef = self.env['dairy.feed.reference']
        for cow in self:
            cow.dairy_feed_reference_id = FeedRef.find_match(
                cow.dairy_age_months,
                cow.dairy_current_weight,
                basis=cow.dairy_feed_calculation_basis or 'weight',
            ).id

    def _get_capitalization_cutoff_date(self):
        self.ensure_one()
        return self.dairy_production_date or fields.Date.context_today(self)

    def _get_capitalized_operational_amount(self):
        self.ensure_one()
        cutoff_date = self._get_capitalization_cutoff_date()
        feed_total = sum(
            self.dairy_feed_line_ids.filtered(
                lambda line: line.feed_record_id.state == 'posted' and line.feed_record_id.date and line.feed_record_id.date <= cutoff_date
            ).mapped('total_amount')
        )
        treatment_total = sum(
            self.dairy_treatment_line_ids.filtered(
                lambda line: line.treatment_record_id.state == 'posted' and line.treatment_record_id.date and line.treatment_record_id.date <= cutoff_date
            ).mapped('total_amount')
        )
        return feed_total + treatment_total

    @api.depends(
        'dairy_acquisition_value',
        'dairy_production_date',
        'dairy_feed_line_ids.total_amount',
        'dairy_feed_line_ids.feed_record_id.state',
        'dairy_feed_line_ids.feed_record_id.date',
        'dairy_treatment_line_ids.total_amount',
        'dairy_treatment_line_ids.treatment_record_id.state',
        'dairy_treatment_line_ids.treatment_record_id.date',
    )
    def _compute_capitalization_values(self):
        for cow in self:
            capitalized_cost = cow._get_capitalized_operational_amount()
            cow.dairy_capitalized_cost_value = capitalized_cost
            cow.dairy_total_book_basis_value = (cow.dairy_acquisition_value or 0.0) + capitalized_cost

    @api.depends(
        'dairy_bcs_reference_id',
        'dairy_bcs_reference_id.weight_average',
        'dairy_acquisition_value',
        'dairy_capitalized_cost_value',
        'dairy_asset_id',
        'dairy_asset_id.value_residual',
        'company_id.dairy_meat_price_per_kg',
    )
    def _compute_market_values(self):
        for cow in self:
            reference = cow.dairy_bcs_reference_id
            price_per_kg = cow.company_id.dairy_meat_price_per_kg or 0.0
            market_weight = reference.weight_average if reference else 0.0
            market_value = market_weight * price_per_kg
            if cow.dairy_asset_id and cow.dairy_asset_id.state in ('open', 'close'):
                book_value = cow.dairy_asset_id.value_residual
            else:
                book_value = cow.dairy_total_book_basis_value or 0.0
            cow.dairy_market_weight = market_weight
            cow.dairy_market_value = market_value
            cow.dairy_book_value = book_value
            cow.dairy_chkpn_value = max(book_value - market_value, 0.0)

    @api.depends('dairy_lifecycle_state', 'dairy_production_date')
    def _compute_dairy_is_productive(self):
        for cow in self:
            cow.dairy_is_productive = cow.dairy_lifecycle_state == 'production' and bool(cow.dairy_production_date)

    @api.depends(
        'dairy_current_weight',
        'dairy_age_months',
        'dairy_feed_calculation_basis',
        'dairy_feed_reference_id',
        'company_id.dairy_concentrate_ratio',
        'company_id.dairy_grass_ratio',
    )
    def _compute_feed_requirements(self):
        for cow in self:
            reference = cow.dairy_feed_reference_id
            if reference:
                cow.dairy_concentrate_need = reference.concentrate_daily_qty
                cow.dairy_grass_need = reference.grass_daily_qty
                continue
            weight = cow.dairy_current_weight or 0.0
            cow.dairy_concentrate_need = weight * (cow.company_id.dairy_concentrate_ratio or 0.0)
            cow.dairy_grass_need = weight * (cow.company_id.dairy_grass_ratio or 0.0)

    @api.model
    def create(self, vals):
        if vals.get('dairy_asset_code', 'New') == 'New':
            vals['dairy_asset_code'] = self.env['ir.sequence'].next_by_code('dairy.cow.asset.code') or 'New'
        record = super(DairyCowMixin, self).create(vals)
        if record.dairy_initial_weight and not record.bobot:
            record.bobot = record.dairy_initial_weight
        record._create_initial_status_history()
        return record

    def write(self, vals):
        result = super(DairyCowMixin, self).write(vals)
        if 'dairy_initial_weight' in vals:
            for cow in self.filtered(lambda c: not c.bobot and c.dairy_initial_weight):
                cow.bobot = cow.dairy_initial_weight
        return result

    def _create_initial_status_history(self):
        for cow in self:
            if cow.dairy_status_history_ids:
                continue
            self.env['dairy.cow.status.history'].create({
                'sapi_id': cow.id,
                'date': cow.dairy_receipt_date or cow.date_of_birth or fields.Date.context_today(cow),
                'status': cow.dairy_lifecycle_state,
                'note': _('Status awal sapi.'),
            })

    def _add_status_history(self, status, date=False, note=False):
        self.ensure_one()
        self.env['dairy.cow.status.history'].create({
            'sapi_id': self.id,
            'date': date or fields.Date.context_today(self),
            'status': status,
            'note': note,
        })

    def _get_productive_asset_target_value(self):
        self.ensure_one()
        return (self.dairy_acquisition_value or 0.0) + self._get_capitalized_operational_amount()

    def _get_capitalization_journal(self):
        self.ensure_one()
        return self.company_id.dairy_capitalization_journal_id or self.company_id.dairy_feed_journal_id or self.company_id.dairy_treatment_journal_id

    def _ensure_capitalization_move(self, asset, capitalized_amount):
        self.ensure_one()
        if not capitalized_amount:
            return self.env['account.move']
        if self.dairy_transition_move_id:
            if self.dairy_transition_move_id.state != 'posted':
                self.dairy_transition_move_id.action_post()
            return self.dairy_transition_move_id

        journal = self._get_capitalization_journal()
        if not journal:
            raise UserError(_('Jurnal kapitalisasi asset biologis belum disetting.'))
        source_account = self.company_id.dairy_feed_asset_account_id
        asset_account = asset.category_id.account_asset_id
        if not source_account:
            raise UserError(_('Akun asset biologis belum produksi belum disetting.'))
        if not asset_account:
            raise UserError(_('Akun asset pada kategori asset sapi produksi belum lengkap.'))

        move = self.env['account.move'].create({
            'date': self.dairy_production_date or fields.Date.context_today(self),
            'ref': _('Kapitalisasi asset biologis %s') % self.display_name,
            'journal_id': journal.id,
            'line_ids': [
                (0, 0, {
                    'name': self.display_name,
                    'account_id': asset_account.id,
                    'debit': capitalized_amount,
                    'credit': 0.0,
                    'analytic_account_id': self.company_id.dairy_analytic_account_id.id or False,
                }),
                (0, 0, {
                    'name': self.display_name,
                    'account_id': source_account.id,
                    'debit': 0.0,
                    'credit': capitalized_amount,
                    'analytic_account_id': self.company_id.dairy_analytic_account_id.id or False,
                }),
            ],
        })
        move.action_post()
        self.dairy_transition_move_id = move.id
        return move

    def action_mark_pregnant(self):
        for cow in self:
            cow.write({
                'dairy_lifecycle_state': 'pregnant',
                'hamil': True,
                'tdk_hamil': False,
            })
            cow._add_status_history('pregnant', note=_('Sapi dinyatakan bunting.'))

    def action_mark_dry(self):
        for cow in self:
            cow.write({
                'dairy_lifecycle_state': 'dry',
                'state': 'kering',
            })
            cow._add_status_history('dry', note=_('Sapi masuk masa kering.'))

    def action_mark_disposed(self):
        for cow in self:
            cow.write({'dairy_lifecycle_state': 'disposed'})
            cow._add_status_history('disposed', note=_('Sapi diubah menjadi afkir.'))

    def action_mark_productive(self):
        for cow in self:
            production_date = cow.dairy_production_date or fields.Date.context_today(cow)
            cow.write({
                'dairy_lifecycle_state': 'production',
                'dairy_production_date': production_date,
                'hamil': False,
                'tdk_hamil': True,
                'state': 'laktasi',
            })
            cow._add_status_history('production', date=production_date, note=_('Sapi mulai produksi.'))
            cow._ensure_production_asset()

    def action_register_calving(self):
        for cow in self:
            calving_date = fields.Date.context_today(cow)
            self.env['dairy.cow.birth.history'].create({
                'sapi_id': cow.id,
                'date': calving_date,
                'note': _('Pencatatan melahirkan dari tombol aksi cepat.'),
            })

    def action_sync_dairy_asset_value(self):
        for cow in self:
            if not cow.dairy_production_date:
                raise UserError(_('Sapi harus memiliki tanggal mulai produksi atau riwayat melahirkan sebelum sinkronisasi asset.'))
            cow._ensure_production_asset()

    def _ensure_production_asset(self):
        self.ensure_one()
        company = self.company_id
        category = company.dairy_asset_category_id
        if not category:
            raise UserError(_('Kategori asset sapi produksi belum disetting pada konfigurasi Dairy Management.'))

        target_value = self._get_productive_asset_target_value()
        capitalized_amount = self._get_capitalized_operational_amount()
        if target_value <= self.dairy_salvage_value:
            raise ValidationError(_('Nilai perolehan ditambah kapitalisasi pra-produksi harus lebih besar dari nilai afkir agar penyusutan dapat dihitung.'))
        if self.dairy_depreciation_months <= 0:
            raise ValidationError(_('Lama penyusutan harus lebih besar dari 0.'))

        asset_vals = {
            'name': self.display_name,
            'code': self.dairy_asset_code,
            'category_id': category.id,
            'value': target_value,
            'salvage_value': self.dairy_salvage_value,
            'date': self.dairy_production_date or fields.Date.context_today(self),
            'partner_id': self.partner_id.id,
            'company_id': company.id,
            'currency_id': company.currency_id.id,
            'method': category.method,
            'method_time': 'number',
            'method_number': self.dairy_depreciation_months,
            'method_period': 1,
            'method_progress_factor': category.method_progress_factor,
            'prorata': category.prorata,
            'account_analytic_id': company.dairy_analytic_account_id.id or category.account_analytic_id.id,
            'note': _('Asset biologis otomatis dari sapi %s. Nilai sudah termasuk kapitalisasi pra-produksi.') % self.display_name,
            'sapi_id': self.id,
        }

        if self.dairy_asset_id:
            asset = self.dairy_asset_id
            if asset.state == 'draft':
                asset.write(asset_vals)
                asset.validate()
            else:
                asset.write({
                    'name': asset_vals['name'],
                    'code': asset_vals['code'],
                    'value': asset_vals['value'],
                    'salvage_value': asset_vals['salvage_value'],
                    'date': asset_vals['date'],
                    'method_number': asset_vals['method_number'],
                    'method_period': asset_vals['method_period'],
                    'account_analytic_id': asset_vals['account_analytic_id'],
                    'note': asset_vals['note'],
                })
        else:
            asset = self.env['account.asset.asset'].create(asset_vals)
            asset.validate()
            self.dairy_asset_id = asset.id

        self._ensure_capitalization_move(asset, capitalized_amount)
        return asset

    def action_open_dairy_revaluation_wizard(self):
        return {
            'name': _('Revaluasi CHKPN'),
            'type': 'ir.actions.act_window',
            'res_model': 'dairy.revaluation.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_cow_ids': [(6, 0, self.ids)],
                'active_model': 'sapi',
                'active_ids': self.ids,
            },
        }

    def action_view_dairy_valuation_history(self):
        return {
            'name': _('Riwayat Valuasi'),
            'type': 'ir.actions.act_window',
            'res_model': 'dairy.valuation.history',
            'view_mode': 'tree,form',
            'domain': [('sapi_id', 'in', self.ids)],
            'context': {'default_sapi_id': self[:1].id if self else False},
        }

    @api.model
    def cron_generate_dairy_depreciation_entries(self):
        today = fields.Date.context_today(self)
        self.env['account.asset.asset'].compute_generated_entries(today)


class DairyCowWeight(models.Model):
    _name = 'dairy.cow.weight'
    _description = 'Riwayat Berat Sapi'
    _order = 'date desc, id desc'

    sapi_id = fields.Many2one('sapi', string='Sapi', required=True, ondelete='cascade')
    date = fields.Date(string='Tanggal', required=True, default=fields.Date.context_today)
    weight = fields.Float(string='Berat (Kg)', required=True)
    note = fields.Char(string='Catatan')

    @api.model
    def create(self, vals):
        record = super(DairyCowWeight, self).create(vals)
        if record.sapi_id:
            record.sapi_id.write({'bobot': record.weight})
        return record

    def write(self, vals):
        result = super(DairyCowWeight, self).write(vals)
        for record in self:
            latest = record.sapi_id.dairy_weight_line_ids.sorted(lambda line: (line.date or fields.Date.today(), line.id), reverse=True)[:1]
            if latest:
                record.sapi_id.bobot = latest.weight
        return result


class DairyCowStatusHistory(models.Model):
    _name = 'dairy.cow.status.history'
    _description = 'Riwayat Status Sapi'
    _order = 'date desc, id desc'

    sapi_id = fields.Many2one('sapi', string='Sapi', required=True, ondelete='cascade')
    date = fields.Date(string='Tanggal', required=True, default=fields.Date.context_today)
    status = fields.Selection([
        ('draft', 'Draft'),
        ('growing', 'Belum Produksi'),
        ('pregnant', 'Bunting'),
        ('production', 'Produksi'),
        ('dry', 'Kering'),
        ('disposed', 'Afkir'),
        ('dead', 'Mati'),
    ], string='Status', required=True)
    note = fields.Char(string='Catatan')


class DairyCowBirthHistory(models.Model):
    _name = 'dairy.cow.birth.history'
    _description = 'Riwayat Melahirkan Sapi'
    _order = 'date desc, id desc'

    sapi_id = fields.Many2one('sapi', string='Induk', required=True, ondelete='cascade')
    date = fields.Date(string='Tanggal Melahirkan', required=True, default=fields.Date.context_today)
    calf_count = fields.Integer(string='Jumlah Anak', default=1)
    calf_sex = fields.Selection([
        ('m', 'Jantan'),
        ('f', 'Betina'),
        ('mix', 'Campuran'),
        ('unknown', 'Belum Diisi'),
    ], string='Jenis Kelamin Anak', default='unknown')
    note = fields.Char(string='Catatan')

    @api.model
    def create(self, vals):
        record = super(DairyCowBirthHistory, self).create(vals)
        if record.sapi_id:
            record.sapi_id.write({
                'dairy_production_date': record.date,
                'dairy_lifecycle_state': 'production',
                'hamil': False,
                'tdk_hamil': True,
                'state': 'laktasi',
            })
            record.sapi_id._add_status_history(
                'production',
                date=record.date,
                note=_('Riwayat melahirkan dicatat.'),
            )
            record.sapi_id._ensure_production_asset()
        return record


class AccountAssetAsset(models.Model):
    _inherit = 'account.asset.asset'

    sapi_id = fields.Many2one('sapi', string='Sapi')
