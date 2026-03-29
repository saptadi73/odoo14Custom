from odoo import _, api, fields, models
from odoo.exceptions import UserError


class DairyRevaluationWizard(models.TransientModel):
    _name = 'dairy.revaluation.wizard'
    _description = 'Wizard Revaluasi CHKPN Dairy'

    valuation_date = fields.Date(string='Tanggal Valuasi', required=True, default=fields.Date.context_today)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company, required=True)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', readonly=True)
    meat_price_per_kg = fields.Monetary(string='Harga Daging/Kg', currency_field='currency_id', required=True)
    cow_ids = fields.Many2many(
        'sapi',
        string='Sapi',
        domain="[('company_id', '=', company_id), ('active', '=', True), ('dairy_bcs_reference_id', '!=', False)]",
    )
    apply_all = fields.Boolean(string='Semua Sapi Aktif', default=False)
    create_journal = fields.Boolean(string='Buat Jurnal CHKPN', default=True)
    note = fields.Char(string='Catatan')

    @api.model
    def default_get(self, fields_list):
        res = super(DairyRevaluationWizard, self).default_get(fields_list)
        company = self.env.company
        res.setdefault('meat_price_per_kg', company.dairy_meat_price_per_kg)
        active_ids = self.env.context.get('active_ids', [])
        if active_ids and 'cow_ids' in fields_list:
            cows = self.env['sapi'].browse(active_ids).filtered(
                lambda c: c.company_id == company and c.active and c.dairy_bcs_reference_id
            )
            res['cow_ids'] = [(6, 0, cows.ids)]
        return res

    @api.onchange('company_id')
    def _onchange_company_id(self):
        self.cow_ids = self.cow_ids.filtered(
            lambda c: c.company_id == self.company_id and c.active and c.dairy_bcs_reference_id
        )

    def _get_cows(self):
        self.ensure_one()
        if self.apply_all:
            return self.env['sapi'].search([
                ('company_id', '=', self.company_id.id),
                ('active', '=', True),
                ('dairy_bcs_reference_id', '!=', False),
            ])

        invalid_cows = self.cow_ids.filtered(lambda c: c.company_id != self.company_id)
        if invalid_cows:
            raise UserError(_(
                'Terdapat sapi dari company lain pada pilihan revaluasi. Pilih sapi yang sesuai company wizard.'
            ))

        return self.cow_ids.filtered(lambda c: c.active and c.dairy_bcs_reference_id)

    def _check_configuration(self):
        self.ensure_one()
        if not self.create_journal:
            return
        company = self.company_id
        missing = []
        if not company.dairy_impairment_journal_id:
            missing.append(_('Jurnal CHKPN'))
        if not company.dairy_impairment_expense_account_id:
            missing.append(_('Akun Beban CHKPN'))
        if not company.dairy_impairment_allowance_account_id:
            missing.append(_('Akun Cadangan CHKPN'))
        if not company.dairy_impairment_recovery_account_id:
            missing.append(_('Akun Pemulihan CHKPN'))
        if missing:
            raise UserError(_('Konfigurasi CHKPN belum lengkap:\n- %s') % '\n- '.join(missing))

    def action_apply(self):
        self.ensure_one()
        self._check_configuration()
        cows = self._get_cows()
        if not cows:
            raise UserError(_('Tidak ada sapi yang dipilih untuk direvaluasi.'))

        self.company_id.dairy_meat_price_per_kg = self.meat_price_per_kg
        self.env['dairy.meat.price.history'].create({
            'date': self.valuation_date,
            'company_id': self.company_id.id,
            'price_per_kg': self.meat_price_per_kg,
            'note': self.note or _('Update harga dari wizard revaluasi.'),
        })

        move_lines = []
        histories = self.env['dairy.valuation.history']
        total_positive = 0.0
        total_negative = 0.0

        for cow in cows:
            market_weight = cow.dairy_bcs_reference_id.weight_average if cow.dairy_bcs_reference_id else 0.0
            market_value = market_weight * self.meat_price_per_kg
            if cow.dairy_asset_id and cow.dairy_asset_id.state in ('open', 'close'):
                book_value = cow.dairy_asset_id.value_residual
            else:
                # Keep non-asset CHKPN basis aligned with sapi compute logic.
                book_value = cow.dairy_total_book_basis_value or 0.0
            target_chkpn = max(book_value - market_value, 0.0)
            recognized_before = cow.dairy_recognized_chkpn_value or 0.0
            delta = target_chkpn - recognized_before
            recognized_after = recognized_before + delta

            history = self.env['dairy.valuation.history'].create({
                'sapi_id': cow.id,
                'valuation_date': self.valuation_date,
                'meat_price_per_kg': self.meat_price_per_kg,
                'bcs_reference_id': cow.dairy_bcs_reference_id.id,
                'market_weight': market_weight,
                'market_value': market_value,
                'book_value': book_value,
                'chkpn_target_value': target_chkpn,
                'recognized_before': recognized_before,
                'delta_value': delta,
                'recognized_after': recognized_after,
                'note': self.note,
            })
            histories |= history

            cow.write({
                'dairy_market_weight': market_weight,
                'dairy_market_value': market_value,
                'dairy_book_value': book_value,
                'dairy_chkpn_value': target_chkpn,
                'dairy_recognized_chkpn_value': recognized_after,
            })

            if delta > 0:
                total_positive += delta
            elif delta < 0:
                total_negative += abs(delta)

        move = self.env['account.move']
        if self.create_journal and (total_positive or total_negative):
            if total_positive:
                move_lines.extend([
                    (0, 0, {
                        'name': _('CHKPN impairment'),
                        'account_id': self.company_id.dairy_impairment_expense_account_id.id,
                        'debit': total_positive,
                        'credit': 0.0,
                        'analytic_account_id': self.company_id.dairy_analytic_account_id.id or False,
                    }),
                    (0, 0, {
                        'name': _('CHKPN allowance'),
                        'account_id': self.company_id.dairy_impairment_allowance_account_id.id,
                        'debit': 0.0,
                        'credit': total_positive,
                        'analytic_account_id': self.company_id.dairy_analytic_account_id.id or False,
                    }),
                ])
            if total_negative:
                move_lines.extend([
                    (0, 0, {
                        'name': _('Reversal CHKPN allowance'),
                        'account_id': self.company_id.dairy_impairment_allowance_account_id.id,
                        'debit': total_negative,
                        'credit': 0.0,
                        'analytic_account_id': self.company_id.dairy_analytic_account_id.id or False,
                    }),
                    (0, 0, {
                        'name': _('Recovery CHKPN'),
                        'account_id': self.company_id.dairy_impairment_recovery_account_id.id,
                        'debit': 0.0,
                        'credit': total_negative,
                        'analytic_account_id': self.company_id.dairy_analytic_account_id.id or False,
                    }),
                ])
            move = self.env['account.move'].create({
                'date': self.valuation_date,
                'ref': _('Revaluasi CHKPN %s') % self.valuation_date,
                'journal_id': self.company_id.dairy_impairment_journal_id.id,
                'line_ids': move_lines,
            })
            move.action_post()
            histories.write({'journal_move_id': move.id})

        return {
            'name': _('Riwayat Valuasi'),
            'type': 'ir.actions.act_window',
            'res_model': 'dairy.valuation.history',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', histories.ids)],
        }
