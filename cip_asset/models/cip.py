from odoo import models, fields, api
from collections import defaultdict
import math

class Cip(models.Model):
    _name = "cip"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "CIP"
    _rec_name = 'tipe_id'

    tipe_id = fields.Many2one('master.tipe.sapi', 'Tipe Sapi')
    date = fields.Date('Date')
    date_from = fields.Date('Date From')
    date_to = fields.Date('Date To')
    account_analytic_id = fields.Many2one('account.analytic.account')
    eartag_id = fields.Char('Eartag ID', compute='_compute_eartag_id')
    sapi_ids = fields.Many2many('sapi', string='Sapi')
    company_id = fields.Many2one('res.company', 'Company')
    tot_amount = fields.Float('Total Amount', store=True)
    amount_dara = fields.Float('Amount Dara', compute='_compute_amount_dara', store=True)
    amount_pedet = fields.Float('Amount Pedet', compute='_compute_amount_pedet', store=True)
    amount_induk = fields.Float('Amount Induk', compute='_compute_amount_induk', store=True)
    jum_sapi = fields.Integer('Jumlah Sapi', compute='_compute_jumlah_sapi', store=True)
    jum_sapi_dara = fields.Integer('Jumlah Sapi Dara', compute='_compute_jumlah_sapi_dara', store=True)
    jum_sapi_pedet = fields.Integer('Jumlah Sapi Pedet', compute='_compute_jumlah_sapi_pedet', store=True)
    jum_sapi_induk = fields.Integer('Jumlah Sapi Induk', compute='_compute_jumlah_sapi_induk', store=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('calculate', 'Calculate'),
        ('validate', 'Validate'),
        ('cancel', 'Cancel'),
        ('done', 'Done'),
    ], string='Status', default='draft', required=True, tracking=True)
    category_cip_id = fields.Many2one('type.cip', 'Category CIP')
    move_id = fields.Many2one('account.move', 'Journal Dara', copy=False)
    move_id_pedet = fields.Many2one('account.move', 'Journal Pedet', copy=False)
    move_id_induk = fields.Many2one('account.move', 'Journal Induk', copy=False)
    cip_expense_line_ids = fields.One2many('cip.expense.line', 'cip_asset_id', string='CIP Expense Line Ids')
    cip_hpp_line_ids = fields.One2many('cip.hpp.line', 'cip_asset_id', string='CIP HPP Line Ids')
    tot_hhp_sapi = fields.Float('Total Hhp Sapi', compute='compute_tot_hhp_sapi', store=True)

    @api.depends('cip_expense_line_ids', 'cip_expense_line_ids.hhp_sapi')
    def compute_tot_hhp_sapi(self):
        for cip in self:
            tot_hhp_sapi = sum(line.hhp_sapi for line in cip.cip_expense_line_ids)
            cip.tot_hhp_sapi = tot_hhp_sapi * cip.jum_sapi

    def func_calculate(self):
        if self.state == 'draft':
            self.state = 'calculate'

    def func_validate(self):
        if self.state == 'calculate':
            self.state = 'validate'

    def func_done(self):
        if self.state == 'validate':
            self.state = 'done'

    def func_cancel(self):
        if self.state == 'done':
            self.state = 'cancel'

    def func_set_draft(self):
        if self.state == 'cancel':
            self.state = 'draft'

    @api.depends('tot_hhp_sapi', 'jum_sapi_dara', 'jum_sapi')
    def _compute_amount_dara(self):
        for record in self:
            if record.jum_sapi_dara != 0:
                raw_amount_dara = record.tot_hhp_sapi / record.jum_sapi * record.jum_sapi_dara

                # Pembulatan sesuai dengan kondisi yang diinginkan
                decimal_part = raw_amount_dara - int(raw_amount_dara)

                # Jika nilai desimal < 0.5, roundup ke bawah; sebaliknya, roundup ke atas
                rounded_decimal = 0.0 if decimal_part <= 0.5 else 1.0

                rounded_amount_dara = int(raw_amount_dara) + rounded_decimal

                # Menyimpan nilai yang sudah dibulatkan ke dalam field amount_dara
                record.amount_dara = rounded_amount_dara
            else:
                record.amount_dara = 0.0

    @api.depends('tot_hhp_sapi', 'jum_sapi_pedet', 'jum_sapi')
    def _compute_amount_pedet(self):
        for record in self:
            if record.jum_sapi_pedet != 0:
                raw_amount_pedet = record.tot_hhp_sapi / record.jum_sapi * record.jum_sapi_pedet

                # Pembulatan sesuai dengan kondisi yang diinginkan
                decimal_part = raw_amount_pedet - int(raw_amount_pedet)

                # Jika nilai desimal < 0.5, roundup ke bawah; sebaliknya, roundup ke atas
                rounded_decimal = 0.0 if decimal_part <= 0.5 else 1.0

                rounded_amount_pedet = int(raw_amount_pedet) + rounded_decimal

                # Menyimpan nilai yang sudah dibulatkan ke dalam field amount_dara
                record.amount_pedet = rounded_amount_pedet
            else:
                record.amount_pedet = 0.0

    @api.depends('tot_hhp_sapi', 'jum_sapi_induk', 'jum_sapi')
    def _compute_amount_induk(self):
        for record in self:
            if record.jum_sapi_induk != 0:
                raw_amount_induk = record.tot_hhp_sapi / record.jum_sapi * record.jum_sapi_induk

                # Pembulatan sesuai dengan kondisi yang diinginkan
                decimal_part = raw_amount_induk - int(raw_amount_induk)

                # Jika nilai desimal < 0.5, roundup ke bawah; sebaliknya, roundup ke atas
                rounded_decimal = 0.0 if decimal_part <= 0.5 else 1.0

                rounded_amount_induk = int(raw_amount_induk) + rounded_decimal

                # Menyimpan nilai yang sudah dibulatkan ke dalam field amount_dara
                record.amount_induk = rounded_amount_induk
            else:
                record.amount_induk = 0.0

    @api.depends('sapi_ids')
    def _compute_eartag_id(self):
        for record in self:
            eartag_ids = [str(sapi.eartag_id) for sapi in record.sapi_ids if
                          sapi.eartag_id]  # konversi ke string dan hindari None atau False
            eartag_str = ', '.join(eartag_ids)
            record.eartag_id = eartag_str

    @api.depends('sapi_ids')
    def _compute_jumlah_sapi(self):
        for cip in self:
            cip.jum_sapi = len(cip.sapi_ids)

    @api.depends('sapi_ids')
    def _compute_jumlah_sapi_dara(self):
        for record in self:
            record.jum_sapi_dara = len(record.sapi_ids.filtered(lambda sapi: 'DARA' in sapi.tipe_id.mapped('nama_tipe_sapi')))

    @api.depends('sapi_ids')
    def _compute_jumlah_sapi_pedet(self):
        for record in self:
            record.jum_sapi_pedet = len(
                record.sapi_ids.filtered(lambda sapi: 'PEDET' in sapi.tipe_id.mapped('nama_tipe_sapi')))

    @api.depends('sapi_ids')
    def _compute_jumlah_sapi_induk(self):
        for record in self:
            record.jum_sapi_induk = len(
                record.sapi_ids.filtered(lambda sapi: 'INDUK' in sapi.tipe_id.mapped('nama_tipe_sapi')))

    def get_rearing_transactions(self):
        """Function to fetch rearing transactions and populate CipExpenseLine"""
        # Delete all CipExpenseLine related to the current Cip
        self.cip_expense_line_ids.unlink()

        for cip in self:
            # Replace 'account.move.line' with the appropriate model
            account_move_lines = self.env['account.move.line'].search([
                ('is_rearing', '=', True),
                ('date', '>=', cip.date_from),
                ('date', '<=', cip.date_to),
                ('move_id.state', '=', 'posted'),
                # Add other criteria as needed
            ])

            # Use defaultdict to store aggregated values based on account_id
            aggregated_values = defaultdict(lambda: {'debit': 0.0, 'credit': 0.0, 'balance': 0.0, 'count': 0})

            for move_line in account_move_lines:
                account_id = move_line.account_id.id
                aggregated_values[account_id]['debit'] += move_line.debit
                aggregated_values[account_id]['credit'] += move_line.credit
                aggregated_values[account_id]['balance'] += move_line.balance
                aggregated_values[account_id]['count'] += 1

            tot_amount = sum(values['balance'] for values in aggregated_values.values())

            def round_special(value):
                decimal_part = value - int(value)

                # Jika nilai desimal < 0.5, roundup ke bawah; sebaliknya, roundup ke atas
                if decimal_part <= 0.5:
                    rounded_decimal = 0.0
                else:
                    rounded_decimal = 1.0

                return int(value) + rounded_decimal

            for account_id, values in aggregated_values.items():
                # Check if count is greater than 0 to avoid division by zero
                if cip.jum_sapi > 0:
                    hhp_sapi = values['balance'] / cip.jum_sapi

                    # Menggunakan round_special untuk pembulatan khusus
                    hhp_sapi_rounded = round_special(hhp_sapi)
                else:
                    hhp_sapi_rounded = 0.0

                expense_line_data = {
                    'cip_asset_id': cip.id,
                    'date_from': cip.date_from,
                    'date_to': cip.date_to,
                    'account_analytic_id': cip.account_analytic_id.id,
                    'account_id': account_id,
                    'debit': values['debit'],
                    'credit': values['credit'],
                    'balance': values['balance'],
                    'hhp_sapi': hhp_sapi_rounded,
                }

                # Create a new CipExpenseLine
                self.env['cip.expense.line'].create(expense_line_data)

            # Menggunakan round_special untuk pembulatan khusus
            # tot_amount_rounded = round_special(tot_amount)

            # Change the status of Cip to 'calculate' after fetching the data
            # self.write({'state': 'calculate'})

            cip.write({'tot_amount': tot_amount})

    # Add a button to the form view
    def button_get_rearing_transactions(self):
        self.get_rearing_transactions()
        return True

    def generate_cip_hpp_lines(self):
        for record in self:
            for sapi in record.sapi_ids:
                existing_hpp_line = self.env['cip.hpp.line'].search([
                    ('cip_asset_id', '=', record.id),
                    ('sapi_id', '=', sapi.id),
                ])

                if existing_hpp_line:
                    existing_hpp_line.write({
                        'eartag_id': sapi.eartag_id,
                        'status_sapi': sapi.state,
                        'date': record.date,
                        'tipe_id': sapi.tipe_id.id if sapi.tipe_id else False,
                        'category_cip_id': sapi.category_cip_id.id if sapi.category_cip_id else False,
                    })

                    # Hitung amount berdasarkan rumus tot_amount / jum_sapi
                    if record.jum_sapi != 0:
                        amount_per_sapi = record.tot_amount / record.jum_sapi
                    else:
                        amount_per_sapi = 0.0

                    existing_hpp_line.write({
                        'amount': amount_per_sapi,
                    })
                else:
                    vals = {
                        'cip_asset_id': record.id,
                        'eartag_id': sapi.eartag_id,
                        'sapi_id': sapi.id,
                        'status_sapi': sapi.state,
                        'date': record.date,
                        'amount': 0.0,
                        'tipe_id': sapi.tipe_id.id if sapi.tipe_id else False,
                        'category_cip_id': sapi.category_cip_id.id if sapi.category_cip_id else False,
                    }
                    new_line = self.env['cip.hpp.line'].create(vals)

                    # Hitung amount berdasarkan rumus tot_amount / jum_sapi
                    if record.jum_sapi != 0:
                        amount_per_sapi = record.tot_amount / record.jum_sapi
                    else:
                        amount_per_sapi = 0.0

                    new_line.write({
                        'amount': amount_per_sapi,
                    })

    def generate_journal_entry(self):
        for cip_record in self:
            move_lines = []
            for expense_line in cip_record.cip_expense_line_ids:
                # Baris kredit menggunakan saldo dari cip_expense_line_ids
                credit_line = (0, 0, {
                    'account_id': expense_line.account_id.id,
                    'debit': 0.0,
                    'credit': round(expense_line.hhp_sapi * cip_record.jum_sapi_dara,),
                    'analytic_account_id': cip_record.account_analytic_id.id,
                })
                move_lines.append(credit_line)

            # Baris debit menggunakan amount_dara dari Cip
            debit_line = (0, 0, {
                'account_id': cip_record.journal_id_dara.default_account.id,
                'debit': round(cip_record.amount_dara),
                'credit': 0.0,
                'analytic_account_id': cip_record.account_analytic_id.id,
            })
            move_lines.append(debit_line)

            # Membuat entri jurnal
            journal_entry = cip_record.env['account.move'].create({
                'journal_id': cip_record.journal_id_dara.id,
                'date': cip_record.date,
                'line_ids': move_lines,
                'analytic_account_id': cip_record.account_analytic_id.id,
                'company_id': cip_record.company_id.id,
            })

            # Konfirmasi dan posting entri jurnal
            journal_entry.action_post()

            # Menulis move_id ke field di Cip
            cip_record.write({'move_id': journal_entry.id})

        return True

    def generate_journal_entry_pedet(self):
        for cip_record in self:
            move_lines = []
            for expense_line in cip_record.cip_expense_line_ids:
                # Baris kredit menggunakan saldo dari cip_expense_line_ids
                credit_line = (0, 0, {
                    'account_id': expense_line.account_id.id,
                    'debit': 0.0,
                    'credit': expense_line.hhp_sapi * cip_record.jum_sapi_pedet,
                    'analytic_account_id': cip_record.account_analytic_id.id,
                })
                move_lines.append(credit_line)

            # Baris debit menggunakan amount_dara dari Cip
            debit_line = (0, 0, {
                'account_id': cip_record.journal_id_pedet.default_account.id,
                'debit': cip_record.amount_pedet,
                'credit': 0.0,
                'analytic_account_id': cip_record.account_analytic_id.id,
            })
            move_lines.append(debit_line)

            # Membuat entri jurnal
            journal_entry = cip_record.env['account.move'].create({
                'journal_id': cip_record.journal_id_pedet.id,
                'date': cip_record.date,
                'line_ids': move_lines,
                'analytic_account_id': cip_record.account_analytic_id.id,
                'company_id': cip_record.company_id.id,
            })

            # Konfirmasi dan posting entri jurnal
            journal_entry.action_post()

            # Menulis move_id ke field di Cip
            cip_record.write({'move_id_pedet': journal_entry.id})

        return True


    def generate_journal_entry_induk(self):
        for cip_record in self:
            move_lines = []
            for expense_line in cip_record.cip_expense_line_ids:
                # Baris kredit menggunakan saldo dari cip_expense_line_ids
                credit_line = (0, 0, {
                    'account_id': expense_line.account_id.id,
                    'debit': 0.0,
                    'credit': expense_line.hhp_sapi * cip_record.jum_sapi_induk,
                    'analytic_account_id': cip_record.account_analytic_id.id,
                })
                move_lines.append(credit_line)

            # Baris debit menggunakan amount_dara dari Cip
            debit_line = (0, 0, {
                'account_id': cip_record.journal_id.default_account.id,
                'debit': cip_record.amount_induk,
                'credit': 0.0,
                'analytic_account_id': cip_record.account_analytic_id.id,
            })
            move_lines.append(debit_line)

            # Membuat entri jurnal
            journal_entry = cip_record.env['account.move'].create({
                'journal_id': cip_record.journal_id.id,
                'date': cip_record.date,
                'line_ids': move_lines,
                'analytic_account_id': cip_record.account_analytic_id.id,
                'company_id': cip_record.company_id.id,
            })

            # Konfirmasi dan posting entri jurnal
            journal_entry.action_post()

            # Menulis move_id ke field di Cip
            cip_record.write({'move_id_induk': journal_entry.id})

        return True


class CipExpenseLine(models.Model):
    _name = 'cip.expense.line'
    _description = 'CIP Expense Line'

    cip_asset_id = fields.Many2one('cip', 'CIP Asset Id')
    date_from = fields.Date('Date From')
    date_to = fields.Date('Date To')
    account_id = fields.Many2one('account.account', 'Account')
    debit = fields.Float('Debit')
    credit = fields.Float('Credit')
    balance = fields.Float('Balance')
    hhp_sapi = fields.Float('HPP Per Sapi')
    account_analytic_id = fields.Many2one('account.analytic.account')

class CipHppLine(models.Model):
    _name = 'cip.hpp.line'
    _description = 'CIP HPP Line'

    cip_asset_id = fields.Many2one('cip', 'CIP Asset Id')
    eartag_id = fields.Char('Eartag ID')
    sapi_id = fields.Many2one('sapi', 'Sapi')
    category_cip_id = fields.Many2one('type.cip', 'Category CIP')
    status_sapi = fields.Selection([
        ('tdk_ada', 'Tidak Ada'),
        ('kering', 'Kering'),
        ('laktasi', 'Laktasi'),
    ], string='Status Sapi')
    date = fields.Date('Date')
    amount = fields.Float('Amount')


class TypeCip(models.Model):
    _name = "type.cip"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Tipe CIP"
    _rec_name = 'name'

    kode = fields.Char('Kode')
    name = fields.Char('Category Name')
    account_id = fields.Many2one('account.account', 'Account')
    company_id = fields.Many2one('res.company', 'Company')