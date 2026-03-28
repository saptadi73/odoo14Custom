# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle 
#
##############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

class account_move_line(models.Model):
    _inherit='account.move.line'
    
    adv_payment_id = fields.Many2one('advance.payment.line', string='Multi Payment Id')

class account_move(models.Model):
    _inherit='account.move'
    
    inv_id = fields.Many2one('account.move', string='Invoice')
    tipe_inv_id = fields.Many2one('master.tipe.invoice',string='Tipe Invoice', required=True)
    tipe_invoice = fields.Selection([('kredit_pkp', 'Kredit PKP'),('kredit_sapi', 'Kredit Sapi'),('peralatan', 'Peralatan')], string='Tipe Invoice')

    @api.model
    def default_get(self, fields):
        defaults = super(account_move, self).default_get(fields)

        # Cari record tabel.fat yang memiliki is_default = True
        default_tipe_inv_id = self.env['master.tipe.invoice'].search([('name', '=', 'Umum')], limit=1)
        if default_tipe_inv_id:
            defaults['tipe_inv_id'] = default_tipe_inv_id.id
        else:
            # Jika tidak ditemukan record, atur tipe_inv_id ke None atau handle sesuai kebutuhan
            defaults['tipe_inv_id'] = False  # Atau ganti dengan nilai yang sesuai

        return defaults

class account_payment(models.Model):
    _inherit = 'account.payment'

    line_ids = fields.One2many('advance.payment.line', 'account_payment_id')
    payment_for = fields.Boolean('Multi Payment')
    payslip_id = fields.Many2one('hr.payslip',string='Payslip')
    effective_date = fields.Date(string='Efective Date')
    bank_reference = fields.Char(string='Bank Reference')
    cheque_reference = fields.Char(string='Cheque Reference')

    def action_post(self):
        if self.payment_for :
            if self.line_ids:
                if self.amount != sum(self.line_ids.mapped('allocation')):
                    raise UserError(_("The sum of the allocation amount of listed invoices Not Same with payment's amount."))
        res = super(account_payment, self).action_post()
        return res

    @api.onchange('amount')
    def onchnage_amount(self):
        total = 0.0
        remain = self.amount
        for line in self.line_ids:
            if line.balance_amount <= remain:
                line.allocation = line.balance_amount
                remain -= line.allocation
            else:
                line.allocation = remain
                remain -= line.allocation
            total += line.allocation

    def more_amount_payment_line(self,amount):
        if self.payment_type == 'inbound':
            counterpart_amount = -amount
        elif self.payment_type == 'outbound':
            counterpart_amount = amount
        else:
            counterpart_amount = 0.0
        
        balance = self.currency_id._convert(counterpart_amount, self.company_id.currency_id, self.company_id, self.date)
        counterpart_amount_currency = counterpart_amount
        currency_id = self.currency_id.id
        
        if self.is_internal_transfer:
            if self.payment_type == 'inbound':
                liquidity_line_name = _('Transfer to %s', self.journal_id.name)
            else: # payment.payment_type == 'outbound':
                liquidity_line_name = _('Transfer from %s', self.journal_id.name)
        else:
            liquidity_line_name = self.payment_reference

        # Compute a default label to set on the journal items.

        payment_display_name = {
            'outbound-customer': _("Customer Reimbursement"),
            'inbound-customer': _("Customer Payment"),
            'outbound-supplier': _("Vendor Payment"),
            'inbound-supplier': _("Vendor Reimbursement"),
        }

        default_line_name = self.env['account.move.line']._get_default_line_name(
            _("Internal Transfer") if self.is_internal_transfer else payment_display_name['%s-%s' % (self.payment_type, self.partner_type)],
            amount,
            self.currency_id,
            self.date,
            partner=self.partner_id,
        )
        new_lines  = []
        liq_dic = {
            'name': liquidity_line_name or default_line_name,
            'date_maturity': self.date,
            'amount_currency': -counterpart_amount_currency,
            'currency_id': currency_id,
            'debit': balance < 0.0 and -balance or 0.0,
            'credit': balance > 0.0 and balance or 0.0,
            'partner_id': self.partner_id.id,
            'account_id': self.journal_id.payment_debit_account_id.id if balance < 0.0 else self.journal_id.payment_credit_account_id.id,
        }
            # Receivable / Payable.
        rec_dict={
            'name': self.payment_reference or default_line_name,
            'date_maturity': self.date,
            'amount_currency': counterpart_amount_currency if currency_id else 0.0,
            'currency_id': currency_id,
            'debit': balance > 0.0 and balance or 0.0,
            'credit': balance < 0.0 and -balance or 0.0,
            'partner_id': self.partner_id.id,
            'account_id': self.destination_account_id.id,
        }
        new_lines.append(liq_dic)
        new_lines.append(rec_dict)
        return new_lines

        
    def dev_generate_moves(self):
        if self.payment_for :
            line_vals_list = []
            total_amount = self.amount
            for line in self.line_ids:
                total_amount = total_amount - line.allocation
                if self.payment_type == 'inbound':
                    counterpart_amount = -line.allocation
                    if line.invoice_id.move_type == 'out_refund':
                        counterpart_amount = line.allocation
                elif self.payment_type == 'outbound':
                    counterpart_amount = line.allocation
                    if line.invoice_id.move_type == 'in_refund':
                        counterpart_amount = -line.allocation
                else:
                    counterpart_amount = 0.0

                balance = self.currency_id._convert(counterpart_amount, self.company_id.currency_id, self.company_id, self.date)
                counterpart_amount_currency = counterpart_amount
                currency_id = self.currency_id.id

                if self.is_internal_transfer:
                    if self.payment_type == 'inbound':
                        liquidity_line_name = _('Transfer to %s', self.journal_id.name)
                    else: # payment.payment_type == 'outbound':
                        liquidity_line_name = _('Transfer from %s', self.journal_id.name)
                else:
                    liquidity_line_name = self.payment_reference

                # Compute a default label to set on the journal items.

                payment_display_name = {
                    'outbound-customer': _("Customer Reimbursement"),
                    'inbound-customer': _("Customer Payment"),
                    'outbound-supplier': _("Vendor Payment"),
                    'inbound-supplier': _("Vendor Reimbursement"),
                }

                default_line_name = self.env['account.move.line']._get_default_line_name(
                    _("Internal Transfer") if self.is_internal_transfer else payment_display_name['%s-%s' % (self.payment_type, self.partner_type)],
                    line.allocation,
                    self.currency_id,
                    self.date,
                    partner=self.partner_id,
                )

                
                    # Liquidity line.
                liq_dic = {
                    'name': liquidity_line_name or default_line_name,
                    'date_maturity': self.date,
                    'amount_currency': -counterpart_amount_currency,
                    'currency_id': currency_id,
                    'debit': balance < 0.0 and -balance or 0.0,
                    'credit': balance > 0.0 and balance or 0.0,
                    'partner_id': self.partner_id.id,
                    'account_id': self.journal_id.payment_debit_account_id.id if balance < 0.0 else self.journal_id.payment_credit_account_id.id,
                }
                    # Receivable / Payable.
                rec_dict={
                    'name': self.payment_reference or default_line_name,
                    'date_maturity': self.date,
                    'amount_currency': counterpart_amount_currency if currency_id else 0.0,
                    'currency_id': currency_id,
                    'debit': balance > 0.0 and balance or 0.0,
                    'credit': balance < 0.0 and -balance or 0.0,
                    'partner_id': self.partner_id.id,
                    'account_id': self.destination_account_id.id,
                    'adv_payment_id':line.id,
                }
                line_vals_list.append(liq_dic)
                line_vals_list.append(rec_dict)
            if total_amount > 0:
                n_lines = self.more_amount_payment_line(total_amount)
                for n_l in n_lines:
                    line_vals_list.append(n_l)
                    
            self.move_id.line_ids.unlink()
            self.move_id.line_ids = [(0, 0, line_vals) for line_vals in line_vals_list]
            self.move_id.action_post()
            for line in self.line_ids:
                invoice_id = line.invoice_id
                move_line = self.env['account.move.line'].search([('move_id','=',self.move_id.id),('adv_payment_id','=',line.id)])
                invoice_id.js_assign_outstanding_line(move_line.id)
            return True

    def _synchronize_from_moves(self, changed_fields):
        for payment in self:
            if payment.payment_for == True:
                return True
        return super(account_payment,self)._synchronize_from_moves(changed_fields)
        
    
    def load_payment_lines(self):
        if self.payment_for :
            self.line_ids.unlink()
            account_inv_obj = self.env['account.move']
            invoice_ids=[]
            partner_ids = self.env['res.partner'].search([('parent_id','=',self.partner_id.id)]).ids
            partner_ids.append(self.partner_id.id)
            query = """ select id from account_move where partner_id in %s and state = %s and move_type in %s and company_id = %s and payment_state != %s"""
            if self.partner_type == 'customer':
                params = (tuple(partner_ids),'posted',('out_invoice','out_refund'), self.company_id.id, 'paid')
            else:
                params = (tuple(partner_ids),'posted',('in_invoice','in_refund'), self.company_id.id, 'paid')
            self.env.cr.execute(query, params)
            result = self.env.cr.dictfetchall()
            invoice_ids = [inv.get('id') for inv in result]
            invoice_ids = account_inv_obj.browse(invoice_ids)
            curr_pool = self.env['res.currency']
            for vals in invoice_ids:
                account_id = False
                if self.partner_type == 'customer':
                    account_id = vals.partner_id and vals.partner_id.property_account_receivable_id.id or False
                else:
                    account_id = vals.partner_id and vals.partner_id.property_account_payable_id.id or False
                    
                original_amount = vals.amount_total
                balance_amount = vals.amount_residual
                allocation = vals.amount_residual
                tipe_invoice = vals.tipe_invoice

                if vals.currency_id.id != self.currency_id.id:
                    original_amount = vals.amount_total
                    balance_amount = vals.amount_residual
                    allocation = vals.amount_residual
                    if vals.currency_id.id != self.currency_id.id:
                        currency_id = self.currency_id.with_context(date=self.date)
                        original_amount = curr_pool._compute(vals.currency_id, currency_id, original_amount, round=True)
                        balance_amount = curr_pool._compute(vals.currency_id, currency_id, balance_amount, round=True)
                        allocation = curr_pool._compute(vals.currency_id, currency_id, allocation, round=True)

                query = """ INSERT INTO advance_payment_line (invoice_id, account_id, date, due_date, original_amount, balance_amount, currency_id, account_payment_id,tipe_invoice) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
                params = (vals.id,account_id, vals.invoice_date, vals.invoice_date_due, original_amount, balance_amount, self.currency_id.id, self.id, tipe_invoice)
                self.env.cr.execute(query, params)
            
    
class advance_payment_line(models.Model):
    _name = 'advance.payment.line'
    _description = 'Advance Payment Line'

    invoice_id = fields.Many2one('account.move',string='Invoice')
    account_id = fields.Many2one('account.account', string="Account")
    date = fields.Date(string="Date")
    due_date = fields.Date(string="Due Date")
    original_amount = fields.Float(string="Invoice Amount")
    balance_amount = fields.Float(string="Balance Amount")
    allocation = fields.Float(string="Allocation")
    account_payment_id = fields.Many2one('account.payment')
    diff_amt = fields.Float('Remaining Amount',compute='get_diff_amount',)
    allow_rounding = fields.Char('round')
    currency_id= fields.Many2one('res.currency',string='Currency')
    tipe_invoice = fields.Selection([('kredit_pkp', 'Kredit PKP'),('kredit_sapi', 'Kredit Sapi'),('peralatan', 'Peralatan')], string='Tipe Invoice')

    @api.depends('balance_amount','allocation')
    def get_diff_amount(self):
        for line in self: 
            line.diff_amt = line.balance_amount - line.allocation
    
        
        
