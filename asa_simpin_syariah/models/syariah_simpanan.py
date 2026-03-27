# -*- coding: utf-8 -*-
# Part of Akun+. See LICENSE file for full copyright and licensing details.

from datetime import datetime, timedelta, date
from functools import partial
from itertools import groupby

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.misc import formatLang
from odoo.osv import expression
from odoo.tools import float_is_zero, float_compare

from werkzeug.urls import url_encode

class AccountMove(models.Model):
    _inherit = 'account.move'

    simpanan_id = fields.Many2one('simpin_syariah.rekening', string='Simpanan')
    
    @api.depends(
        'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual',
        'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual_currency',
        'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual',
        'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual_currency',
        'line_ids.debit',
        'line_ids.credit',
        'line_ids.currency_id',
        'line_ids.amount_currency',
        'line_ids.amount_residual',
        'line_ids.amount_residual_currency',
        'line_ids.payment_id.state',
        'line_ids.full_reconcile_id')
    def _compute_amount(self):
        res = super(AccountMove, self)._compute_amount()
        for move in self :
            if move.payment_state == 'paid' :
                if move.simpanan_id :
                    if move.move_type == 'out_invoice' :
                        move.simpanan_id.member_id.cek_paid_status()
        return res

class SimPinRekening(models.Model):
    _name = "simpin_syariah.rekening"
    _description = "Rekening Anggota Simpin Syariah"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'resource.mixin']


    
    @api.depends('transaction_lines')
    def _compute_amount(self):
        self.balance = sum(line.debit - line.credit for line in self.transaction_lines)

    @api.model
    def _default_currency(self):
        return self.env.user.company_id.currency_id.id

    name = fields.Char(string='Nomor Rekening', default='/')
    member_id = fields.Many2one('simpin_syariah.member',string='Nama Anggota', required=False,
                                 domain=[('state', '=', 'done')])
    akad_id = fields.Many2one('master.akad_syariah',string='Jenis Akad', required=False,
                              domain=[('is_actived', '=', True)])
    product_id = fields.Many2one('product.product',string='Produk', required=False,
                                 domain=[('is_syariah', '=', True),
                                         '|',('product_tmpl_id.categ_id.parent_id.name', '=', 'Simpanan'),
                                         ('product_tmpl_id.categ_id.name', '=', 'Simpanan')])
    transaction_lines = fields.One2many('simpin_syariah.rekening.line','rekening_id',string='Transaction')
    invoice_ids = fields.One2many('account.move','simpanan_id',string='Tagihan')
    is_blokir = fields.Boolean('Blokir', default=False)
    currency_id = fields.Many2one('res.currency', string="Currency", readonly=True, default=_default_currency)
    balance = fields.Monetary(string='Balance', compute='_compute_amount', store=True, currency_field='currency_id')
    account_analytic_id = fields.Many2one('account.analytic.account', required=False, string='Analytic Account')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submit', 'Submitted'),
        ('check', 'Check Document'),
        ('approve', 'Approved'),
        ('active', 'Active'),
        ('close', 'Closed'),
        ('block', 'Blocked'),
        ], string='Status', copy=False, index=True, default='draft', track_visibility='onchange', readonly=True)
    mitra_id = fields.Many2one('simpin_syariah.mitra', string='Mitra Kerja', related='member_id.mitra_id',store=True)
    partner_id = fields.Many2one('res.partner',string='Customer')
    max_debit = fields.Float('Maksimal Debit', compute='_compute_amount_maxdebit', store=True)

    @api.depends('balance')
    def _compute_amount_maxdebit(self):
        for record in self:
            record.max_debit = record.balance * 0.8

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('member_id.name', '=ilike', self.member_id.name + '%'), ('name', operator, name)]
            if operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = ['&', '!'] + domain[1:]
        rek_id = self.search(domain + args, limit=limit)
        return rek_id.name_get()

    
    @api.depends('name', 'member_id.name')
    def name_get(self):
        result = []
        for rek_id in self:
            name = '[' + str(rek_id.name) + '] ' + str(rek_id.member_id.name)
            result.append((rek_id.id, name))
        return result

    
    def action_transfer(self):
        if self.balance>0:
            sandi_trx = self.env['master.kode_transaksi'].search([('kode_trx','=','TRFR')])
            view_id = self.env['ir.ui.view'].search([('name', '=', 'simpin_syariah.rekening.line.transfer')], limit=1).id
            return {
                'name': _('Transfer Simpanan'),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'view_id': view_id,
                'res_model': 'simpin_syariah.rekening.line.transient',
                'target': 'new',
                'context': {
                    'default_tanggal': date.today(),
                    'default_sandi_id': sandi_trx.id,
                    'default_rekening_id': self.id,
                    'default_name': 'Transfer',
                    'default_state': 'transfer',
                    'default_balance': self.balance,
                    }
                }
        else:
            raise UserError(_('Saldo Rekening Tidak Mencukupi'))

    
    def action_blokir(self):
        raise UserError('Sub Modul Blokir Rekening')

    
    def action_penutupan(self):
        raise UserError('Sub Modul Penutupan Rekening')

    
    def action_setor(self):
        sandi_trx = self.env['master.kode_transaksi'].search([('kode_trx','=','STT')])
        view_id = self.env['ir.ui.view'].search([('name', '=', 'simpin_syariah.rekening.line.setor')], limit=1).id
        return {
            'name': _('Setoran Simpanan'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_id': view_id,
            'res_model': 'simpin_syariah.rekening.line',
            'target': 'new',
            'context': {
                    'default_tanggal': date.today(),
                    'default_rekening_id': self.id,
                    'default_sandi_id': sandi_trx.id,
                    'default_name': 'Setoran',
                    'default_state': 'setoran',
                    'default_balance': self.balance,
                    }
                }

    
    def action_tarik(self):
        if self.balance>0:
            sandi_trx = self.env['master.kode_transaksi'].search([('kode_trx','=','TRT')])
            view_id = self.env['ir.ui.view'].search([('name', '=', 'simpin_syariah.rekening.line.tarik')], limit=1).id
            return {
                'name': _('Tarikan Simpanan'),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'view_id': view_id,
                'res_model': 'simpin_syariah.rekening.line.transient',
                'target': 'new',
                'context': {
                    'default_tanggal': date.today(),
                    'default_rekening_id': self.id,
                    'default_sandi_id': sandi_trx.id,
                    'default_name': 'Tarikan',
                    'default_state': 'tarikan',
                    'default_balance': self.balance,
                    }
                }
        else:
            raise UserError(_('Saldo Rekening Tidak Mencukupi'))

    
    def action_submit(self):
        self.write({'state': 'submit'})

    
    def action_check(self):
        self.write({'state': 'check'})

    
    def action_approve(self):
        ak_id = self.env['master.akad_syariah'].search([('id','=',self.akad_id.id)])
        akad_id = ak_id.name + " sequence"
        rekno = self.env['ir.sequence'].sudo().next_by_code(akad_id)
        if not rekno:
            cr_seq = self.env['ir.sequence'].sudo().create({
                            'name': ak_id.name,
                            'code': akad_id,
                            'implementation': 'standard',
                            'active': True,
                            'prefix': ak_id.kode + '/%(year)s/%(month)s/',
                            'padding': 5,
                            'company_id': self.env.user.company_id.id,
                            'use_date_range': False,
                            })
            if cr_seq:
                rekno = self.env['ir.sequence'].next_by_code(akad_id)
            else:
                raise UserError('Sequence Error')
        self.name = rekno
        self.write({'state': 'active'})
        # self.create_invoice()


    # def cron_create_invoice(self):
    #     simpanan = self.env['simpin_syariah.rekening'].search([('member_id.state','=', 'done'),('member_id.mitra_id','=',False)])
    #     for trans in simpanan:
    #         if trans.product_id.name == 'SIMPANAN WAJIB':
    #             for invoice in trans.invoice_ids:
    #                 # next_month = invoice.invoice_date + timedelta(days=30)
    #                 # previous_month = date.today() - timedelta(days=30)
    #                 invoice_month_year = invoice.invoice_date.strftime("%Y-%m")
    #                 today = datetime.now()
    #                 month_year = today.strftime("%Y-%m")
    #                 if invoice.state == 'posted':
    #                     if invoice_month_year != month_year:
    #                         print ("#############cron invoice cek##########", invoice.name, trans.product_id.name, invoice_month_year, month_year)
    #                         conf_sch_inv = self.env['config.schedule'].search([('tipe_schedule','=','invoice')], limit=1)
    #                         invoice_date = month_year+'-'+conf_sch_inv.date_day
    #                         invoice_vals = {
    #                                         'partner_id': trans.partner_id.id,
    #                                         'invoice_date' : invoice_date,
    #                                         'state': 'draft',
    #                                         'move_type': 'out_invoice',
    #                                         'simpanan_id' : trans.id,
    #                                         'invoice_line_ids': [{
    #                                                             'product_id': trans.product_id.id,
    #                                                             'name': trans.product_id.name,
    #                                                             'account_id': trans.product_id.property_account_income_id.id,
    #                                                             'quantity': 1,
    #                                                             'price_unit': trans.product_id.minimal_setor
    #                                                         }]
    #                                         }
    #                         invoice = self.env['account.move'].sudo().create(invoice_vals)
    #                         movelines = self.env['account.move.line'].search([('move_id','=',invoice.id),('account_id.code','=','112100321')])
    #                         if movelines:
    #                             print ("==============movelines=============", movelines.account_id.code, invoice, trans.akad_id.property_account_receivable_id.code)
    #                             movelines.write({'account_id' : trans.akad_id.property_account_receivable_id.id})
    #                         invoice.action_post()


    # def create_invoice(self):
    #     for trans in self:
    #         invoice_vals_list =[]
    #         if trans.product_id :
    #             if not trans.product_id.property_account_income_id:
    #                 raise UserError(_('You must add Income Account Product %s.')%(trans.product_id.name))
    #
    #             invoice_vals = {
    #                                 'product_id': trans.product_id.id,
    #                                 'name': trans.product_id.name,
    #                                 'account_id': trans.product_id.property_account_income_id.id,
    #                                 'quantity': 1,
    #                                 'price_unit': trans.product_id.minimal_setor
    #                                 }
    #
    #
    #             invoice_vals_list.append(invoice_vals)
    #
    #         sim_name = 'Simpanan : ' + str(trans.name) + " - " + str(trans.member_id.name)
    #         invoice_vals = {
    #                         'partner_id': trans.partner_id.id,
    #                         'state': 'draft',
    #                         #'name' : sim_name,
    #                         'payment_reference':sim_name,
    #                         'move_type': 'out_invoice',
    #                         'simpanan_id' : trans.id,
    #                         'invoice_line_ids': invoice_vals_list
    #                         }
    #         invoice = self.env['account.move'].sudo().create(invoice_vals)
    #         movelines = self.env['account.move.line'].search([('move_id','=',invoice.id),('account_id.code','=','112100321')])
    #         if movelines:
    #             print ("==============movelines=============", movelines.account_id.code, invoice, trans.akad_id.property_account_receivable_id.code)
    #             movelines.write({'account_id' : trans.akad_id.property_account_receivable_id.id})
    #         invoice.action_post()




    
    def action_close(self):
        self.write({'state': 'close'})

    
    def action_block(self):
        self.write({'state': 'block'})

class SimPinRekeningLine(models.Model):
    _name = "simpin_syariah.rekening.line"
    _description = "Transaksi Rekening Anggota Simpin Syariah"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'resource.mixin']
    _order = "id desc"


    @api.model_create_multi
    def create(self, vals_list):
        """ :context's key `check_move_validity`: check data consistency after move line creation. Eg. set to false to disable verification that the move
                debit-credit == 0 while creating the move lines composing the move.
        """
        lines = super(SimPinRekeningLine, self).create(vals_list)

        return lines

    name = fields.Char(string='Description')
    rekening_id = fields.Many2one('simpin_syariah.rekening',string='Nomor Rekening',ondelete="cascade", auto_join=True)
    sandi_id = fields.Many2one('master.kode_transaksi',string='Kode Trx')
    tanggal = fields.Date(string='Date', index=True, store=True, copy=False, readonly=False)
    currency_id = fields.Many2one('res.currency', string="Currency", readonly=True)
    debit = fields.Monetary(default=0.0, currency_field='currency_id')
    credit = fields.Monetary(default=0.0, currency_field='currency_id')
    balance = fields.Monetary(compute='_store_balance', store=True, currency_field='currency_id',
        help="Technical field holding the debit - credit in order to open meaningful graph views from reports")
    keterangan = fields.Text('Keterangan')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('setoran', 'Setoran'),
        ('tarikan', 'Tarikan'),
        ('transfer', 'Transfer'),
        ('post', 'Posted'),
        ('cancel', 'Canceled'),
        ], string='Status', copy=False, index=True, default='draft', track_visibility='onchange', readonly=True)
    is_valid = fields.Boolean(string='valid?',default=False)
    rek_asal = fields.Many2one('simpin_syariah.rekening',string='Rekening Asal')
    rek_tujuan = fields.Many2one('simpin_syariah.rekening',string='Rekening Tujuan')

    @api.onchange('debit', 'credit')
    def _onchange_trx(self):
        balance = self.rekening_id.balance
        if self.credit>balance:
            self.is_valid = False
            raise UserError(_('Tarikan/Transfer Maksimal sebesar Rp. %s')%(balance,))
        else:
            self.is_valid = True

    
    def save_trx(self):
        if not self.keterangan:
            self.write({'keterangan': self.state})

        amount = payment_type = payment_method = False
        if self.debit>0:
            amount = self.debit
            payment_type = 'inbound'
            payment_method = 1
        elif self.credit>0:
            amount = self.credit
            payment_type = 'outbound'
            payment_method = 2
            
        if self.is_valid and self.state!='transfer':
            payment = self.env['account.payment'].create({
                'amount': amount,
                'payment_date': date.today(),
                'communication': self.state + ' : ' + self.rekening_id.name,
                'partner_id': self.rekening_id.member_id.partner_id.id,
                'partner_type': 'customer',
                'payment_type': payment_type,
                'journal_id': self.sandi_id.journal_id.id,
                'payment_method_id': payment_method,
                'simpanan_line_id': self.id,
                'state': 'draft',
                'name': self.state + ' : ' + self.rekening_id.name,
                            })

            if not payment:
                self.is_valid = False
                raise UserError(_('Terjadi Kesalahan'))

        self.balance = self.balance + self.debit - self.credit

class SimPinRekeningLineTrans(models.TransientModel):
    _name = "simpin_syariah.rekening.line.transient"
    _description = "Transaksi Rekening Anggota Simpin Syariah"


    name = fields.Char(string='Description')
    rekening_id = fields.Many2one('simpin_syariah.rekening',string='Nomor Rekening',ondelete="cascade", auto_join=True)
    sandi_id = fields.Many2one('master.kode_transaksi',string='Kode Trx')
    tanggal = fields.Date(string='Date', index=True, store=True, copy=False, readonly=False)
    currency_id = fields.Many2one('res.currency', string="Currency", readonly=True)
    debit = fields.Monetary(default=0.0, currency_field='currency_id')
    credit = fields.Monetary(default=0.0, currency_field='currency_id')
    balance = fields.Monetary(compute='_store_balance', store=True, currency_field='currency_id',
        help="Technical field holding the debit - credit in order to open meaningful graph views from reports")
    keterangan = fields.Text('Keterangan')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('setoran', 'Setoran'),
        ('tarikan', 'Tarikan'),
        ('transfer', 'Transfer'),
        ('post', 'Posted'),
        ('cancel', 'Canceled'),
        ], string='Status', copy=False, index=True, default='draft', track_visibility='onchange', readonly=True)
    is_valid = fields.Boolean(string='valid?',default=False)
    rek_asal = fields.Many2one('simpin_syariah.rekening',string='Rekening Asal')
    rek_tujuan = fields.Many2one('simpin_syariah.rekening',string='Rekening Tujuan')

    
    def save_trx(self):
        if not self.keterangan:
            self.write({'keterangan': self.state})

        balance = self.rekening_id.balance
        
        amount = payment_type = payment_method = False
        if self.debit>0:
            amount = self.debit
            payment_type = 'inbound'
            payment_method = 1
        elif self.credit>0:
            amount = self.credit
            payment_type = 'outbound'
            payment_method = 2
            
        if self.credit<balance and self.state=='tarikan':
            tarikan = [(0,0,({
                    'name': 'Tarikan : ' + self.rekening_id.name,
                    'rekening_id': self.rekening_id.id,
                    'sandi_id': self.sandi_id.id,
                    'tanggal': date.today(),
                    'credit': self.credit,
                    'balance': self.rekening_id.balance - self.credit,
                    'keterangan': 'Tarikan ' + self.keterangan,
                    'state': 'tarikan',
                    'is_valid': True,
                            }))]
            self.rekening_id.update({'transaction_lines': tarikan,})
            payment = self.env['account.payment'].create({
                    'amount': amount,
                    'payment_date': date.today(),
                    'communication': self.state + ' : ' + self.rekening_id.name,
                    'partner_id': self.rekening_id.member_id.partner_id.id,
                    'partner_type': 'customer',
                    'payment_type': payment_type,
                    'journal_id': self.sandi_id.journal_id.id,
                    'payment_method_id': payment_method,
                    'simpanan_line_id': self.id,
                    'state': 'draft',
                    'name': self.state + ' : ' + self.rekening_id.name,
                            })

            if not payment:
                self.is_valid = False
                raise UserError(_('Terjadi Kesalahan'))

        elif self.credit<balance and self.state=='transfer':
            tarikan = [(0,0,({
                    'name': 'Tarikan : ' + self.rekening_id.name,
                    'rekening_id': self.rekening_id.id,
                    'sandi_id': self.sandi_id.id,
                    'tanggal': date.today(),
                    'credit': self.credit,
                    'balance': self.rekening_id.balance - self.credit,
                    'keterangan': 'Tarikan ' + self.keterangan,
                    'state': 'tarikan',
                    'is_valid': True,
                            }))]
            transfer_to = [(0,0,({
                    'name': 'Transfer to ' + self.rek_tujuan.name,
                    'rekening_id': self.rek_tujuan.id,
                    'sandi_id': self.sandi_id.id,
                    'tanggal': date.today(),
                    'debit': self.credit,
                    'rek_asal': self.rekening_id.id,
                    'balance': self.rek_tujuan.balance + self.credit,
                    'keterangan': 'Transfer dari ' + self.rek_tujuan.name + ': ' + self.keterangan,
                    'state': 'transfer',
                    'is_valid': True,
                            }))]
            self.rekening_id.update({'transaction_lines': tarikan,})
            self.rek_tujuan.update({'transaction_lines': transfer_to,})
        else:
            self.is_valid = False
            raise UserError(_('Tarikan/Transfer Maksimal sebesar Rp. %s')%(balance,))


        self.balance = self.balance + self.debit - self.credit

