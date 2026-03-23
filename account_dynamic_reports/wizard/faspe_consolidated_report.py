# -*- coding: utf-8 -*-

from collections import defaultdict
from datetime import date

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class InsFaspeConsolidatedWizard(models.TransientModel):
    _name = 'ins.faspe.consolidated.wizard'
    _description = 'FASPE Consolidated Multi Company Wizard'

    title = fields.Char(
        string='Judul',
        default='Laporan Keuangan Financial Accounting Standards for Private Entitie(FASPE)',
        readonly=True,
    )
    date_from = fields.Date(
        string='Tanggal Mulai',
        required=True,
        default=lambda self: date(fields.Date.context_today(self).year, 1, 1),
    )
    date_to = fields.Date(
        string='Tanggal Akhir',
        required=True,
        default=lambda self: fields.Date.context_today(self),
    )
    target_move = fields.Selection(
        [('posted', 'All Posted Entries'), ('all', 'All Entries')],
        string='Target Moves',
        required=True,
        default='posted',
    )
    company_ids = fields.Many2many(
        'res.company',
        string='Companies',
        required=True,
        default=lambda self: self.env.company,
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company Utama',
        required=True,
        default=lambda self: self.env.company,
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        related='company_id.currency_id',
        readonly=True,
    )
    elimination_line_ids = fields.One2many(
        'ins.faspe.consolidated.elimination.line',
        'wizard_id',
        string='Akun Eliminasi per Company',
    )

    @api.onchange('company_ids')
    def _onchange_company_ids(self):
        if not self.company_ids:
            self.company_id = False
            self.elimination_line_ids = [(5, 0, 0)]
            return

        if self.company_id not in self.company_ids:
            self.company_id = self.company_ids[0]

        existing_by_company = {line.company_id.id: line for line in self.elimination_line_ids if line.company_id}
        commands = []
        for company in self.company_ids:
            line = existing_by_company.get(company.id)
            if line:
                commands.append((0, 0, {
                    'company_id': company.id,
                    'account_ids': [(6, 0, line.account_ids.ids)],
                }))
            else:
                commands.append((0, 0, {'company_id': company.id}))

        self.elimination_line_ids = commands

    def _validate_input(self):
        self.ensure_one()

        if len(self.company_ids) < 2:
            raise UserError(_('Pilih minimal 2 company untuk laporan consolidated multi company.'))

        if not self.date_from or not self.date_to:
            raise UserError(_('Tanggal Mulai dan Tanggal Akhir wajib diisi.'))

        if self.date_from > self.date_to:
            raise UserError(_('Tanggal Mulai tidak boleh lebih besar dari Tanggal Akhir.'))

        currencies = self.company_ids.mapped('currency_id')
        if len(currencies) > 1:
            raise UserError(_(
                'Semua company yang dikonsolidasikan harus menggunakan mata uang yang sama agar presisi laporan terjaga.'
            ))

    def _get_move_line_domain(self):
        self.ensure_one()
        domain = [
            ('company_id', 'in', self.company_ids.ids),
            ('account_id.internal_group', 'in', ['asset', 'liability', 'equity']),
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
        ]
        if self.target_move == 'posted':
            domain.append(('move_id.state', '=', 'posted'))
        return domain

    def _prepare_account_payload(self):
        self.ensure_one()
        aml_obj = self.env['account.move.line'].sudo()
        grouped = aml_obj.read_group(
            domain=self._get_move_line_domain(),
            fields=['balance', 'account_id', 'company_id'],
            groupby=['account_id', 'company_id'],
            lazy=False,
        )

        account_ids = [row['account_id'][0] for row in grouped if row.get('account_id')]
        account_map = {account.id: account for account in self.env['account.account'].browse(account_ids)}

        payload = {}
        balance_by_company_account = {}
        for row in grouped:
            if not row.get('account_id') or not row.get('company_id'):
                continue

            account_id = row['account_id'][0]
            company_id = row['company_id'][0]
            balance = row.get('balance', 0.0)
            account = account_map.get(account_id)
            if not account:
                continue

            balance_by_company_account[(company_id, account_id)] = balance
            if account_id not in payload:
                payload[account_id] = {
                    'code': account.code,
                    'name': account.name,
                    'internal_group': account.internal_group,
                    'balance': 0.0,
                }
            payload[account_id]['balance'] += balance

        return payload, balance_by_company_account

    def _prepare_elimination_payload(self, balance_by_company_account):
        self.ensure_one()
        elimination_by_account = defaultdict(float)
        elimination_total = 0.0

        for elimination_line in self.elimination_line_ids:
            if not elimination_line.company_id:
                continue
            for account in elimination_line.account_ids:
                amount = balance_by_company_account.get((elimination_line.company_id.id, account.id), 0.0)
                elimination_by_account[account.id] += amount
                elimination_total += amount

        return elimination_by_account, elimination_total

    def _prepare_report_lines(self, payload, elimination_by_account):
        self.ensure_one()
        currency = self.currency_id

        section_titles = {
            'asset': 'ASET',
            'liability': 'LIABILITAS',
            'equity': 'EKUITAS',
        }
        section_order = ['asset', 'liability', 'equity']

        section_data = defaultdict(list)
        for account_id, values in payload.items():
            section_key = values.get('internal_group')
            if section_key not in section_titles:
                continue
            elimination_amount = elimination_by_account.get(account_id, 0.0)
            final_amount = values.get('balance', 0.0) - elimination_amount
            if currency.is_zero(final_amount) and currency.is_zero(elimination_amount):
                continue

            section_data[section_key].append({
                'name': values.get('name'),
                'account_code': values.get('code'),
                'amount_before_elimination': values.get('balance', 0.0),
                'elimination_amount': elimination_amount,
                'amount': final_amount,
            })

        line_vals = []
        totals = {'asset': 0.0, 'liability': 0.0, 'equity': 0.0}
        sequence = 10

        for section_key in section_order:
            section_lines = sorted(
                section_data.get(section_key, []),
                key=lambda item: (item.get('account_code') or '', item.get('name') or ''),
            )
            if not section_lines:
                continue

            line_vals.append({
                'sequence': sequence,
                'line_type': 'section',
                'name': section_titles[section_key],
                'section': section_key,
            })
            sequence += 10

            for section_line in section_lines:
                totals[section_key] += section_line['amount']
                line_vals.append({
                    'sequence': sequence,
                    'line_type': 'account',
                    'name': section_line['name'],
                    'account_code': section_line['account_code'],
                    'section': section_key,
                    'amount_before_elimination': section_line['amount_before_elimination'],
                    'elimination_amount': section_line['elimination_amount'],
                    'amount': section_line['amount'],
                })
                sequence += 10

            line_vals.append({
                'sequence': sequence,
                'line_type': 'total',
                'name': 'TOTAL %s' % section_titles[section_key],
                'section': section_key,
                'amount_before_elimination': sum(line['amount_before_elimination'] for line in section_lines),
                'elimination_amount': sum(line['elimination_amount'] for line in section_lines),
                'amount': totals[section_key],
            })
            sequence += 10

        balance_difference = totals['asset'] - (totals['liability'] + totals['equity'])
        line_vals.append({
            'sequence': sequence,
            'line_type': 'check',
            'name': 'CHECK ASET - (LIABILITAS + EKUITAS)',
            'section': 'check',
            'amount': balance_difference,
        })

        return line_vals, totals, balance_difference

    def action_generate_report(self):
        self.ensure_one()
        self._validate_input()

        payload, balance_by_company_account = self._prepare_account_payload()
        if not payload:
            raise UserError(_('Tidak ada data akun neraca pada rentang tanggal dan filter yang dipilih.'))

        elimination_by_account, elimination_total = self._prepare_elimination_payload(balance_by_company_account)
        line_vals, totals, balance_difference = self._prepare_report_lines(payload, elimination_by_account)

        report = self.env['ins.faspe.consolidated.report'].create({
            'title': self.title,
            'date_from': self.date_from,
            'date_to': self.date_to,
            'target_move': self.target_move,
            'company_ids': [(6, 0, self.company_ids.ids)],
            'company_names': ', '.join(self.company_ids.mapped('name')),
            'currency_id': self.currency_id.id,
            'elimination_total': elimination_total,
            'total_assets': totals['asset'],
            'total_liabilities': totals['liability'],
            'total_equity': totals['equity'],
            'balance_difference': balance_difference,
        })

        line_commands = [(0, 0, line) for line in line_vals]
        report.write({'line_ids': line_commands})

        return {
            'type': 'ir.actions.act_window',
            'name': self.title,
            'res_model': 'ins.faspe.consolidated.report',
            'view_mode': 'form',
            'view_id': self.env.ref('account_dynamic_reports.ins_faspe_consolidated_report_form').id,
            'res_id': report.id,
            'target': 'current',
        }


class InsFaspeConsolidatedEliminationLine(models.TransientModel):
    _name = 'ins.faspe.consolidated.elimination.line'
    _description = 'FASPE Consolidated Elimination Line'

    wizard_id = fields.Many2one('ins.faspe.consolidated.wizard', required=True, ondelete='cascade')
    company_id = fields.Many2one('res.company', string='Company', required=True)
    account_ids = fields.Many2many('account.account', string='Akun yang Di-eliminasi')

    @api.onchange('company_id')
    def _onchange_company_id(self):
        domain = [('internal_group', 'in', ['asset', 'liability', 'equity'])]
        if self.company_id:
            domain.append(('company_id', '=', self.company_id.id))
        return {'domain': {'account_ids': domain}}


class InsFaspeConsolidatedReport(models.TransientModel):
    _name = 'ins.faspe.consolidated.report'
    _description = 'FASPE Consolidated Report'

    title = fields.Char(string='Judul', required=True)
    generated_at = fields.Datetime(string='Dibuat Pada', default=fields.Datetime.now, readonly=True)
    date_from = fields.Date(string='Tanggal Mulai', required=True, readonly=True)
    date_to = fields.Date(string='Tanggal Akhir', required=True, readonly=True)
    target_move = fields.Selection(
        [('posted', 'All Posted Entries'), ('all', 'All Entries')],
        string='Target Moves',
        readonly=True,
    )
    company_ids = fields.Many2many('res.company', string='Companies', readonly=True)
    company_names = fields.Char(string='Company Consolidated', readonly=True)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, readonly=True)
    elimination_total = fields.Monetary(string='Total Eliminasi', currency_field='currency_id', readonly=True)
    total_assets = fields.Monetary(string='Total Aset', currency_field='currency_id', readonly=True)
    total_liabilities = fields.Monetary(string='Total Liabilitas', currency_field='currency_id', readonly=True)
    total_equity = fields.Monetary(string='Total Ekuitas', currency_field='currency_id', readonly=True)
    balance_difference = fields.Monetary(
        string='Selisih Aset - (Liabilitas + Ekuitas)',
        currency_field='currency_id',
        readonly=True,
    )
    line_ids = fields.One2many('ins.faspe.consolidated.report.line', 'report_id', string='Baris Laporan', readonly=True)


class InsFaspeConsolidatedReportLine(models.TransientModel):
    _name = 'ins.faspe.consolidated.report.line'
    _description = 'FASPE Consolidated Report Line'
    _order = 'sequence, id'

    report_id = fields.Many2one('ins.faspe.consolidated.report', required=True, ondelete='cascade')
    sequence = fields.Integer(default=10)
    line_type = fields.Selection(
        [('section', 'Section'), ('account', 'Account'), ('total', 'Total'), ('check', 'Check')],
        string='Tipe Baris',
        required=True,
    )
    section = fields.Selection(
        [('asset', 'Aset'), ('liability', 'Liabilitas'), ('equity', 'Ekuitas'), ('check', 'Check')],
        string='Section',
    )
    name = fields.Char(string='Nama', required=True)
    account_code = fields.Char(string='Kode Akun')
    amount_before_elimination = fields.Monetary(string='Sebelum Eliminasi', currency_field='currency_id')
    elimination_amount = fields.Monetary(string='Eliminasi', currency_field='currency_id')
    amount = fields.Monetary(string='Setelah Eliminasi', currency_field='currency_id')
    currency_id = fields.Many2one(related='report_id.currency_id', readonly=True)