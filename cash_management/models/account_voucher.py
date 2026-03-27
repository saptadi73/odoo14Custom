# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import fields, models, api, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, ValidationError


class AccountVoucher(models.Model):
    _name = 'account.voucher'
    _description = 'Accounting Voucher'
    _inherit = ['mail.thread']
    _order = "date desc, id desc"

    @api.model
    def _default_journal(self):
        voucher_type = self._context.get('voucher_type', 'sale')
        company_id = self._context.get('company_id', self.env.user.company_id.id)
        domain = [
            ('type', '=', 'cash'),
            ('company_id', '=', company_id),
        ]
        return self.env['account.journal'].search(domain, limit=1)

    @api.model
    def _default_payment_journal(self):
        company_id = self._context.get('company_id', self.env.user.company_id.id)
        domain = [
            ('type', 'in', ('bank', 'cash')),
            ('company_id', '=', company_id),
        ]
        return self.env['account.journal'].search(domain, limit=1)

    voucher_type = fields.Selection([
        ('sale', 'Sale'),
        ('purchase', 'Purchase')
        ], string='Type', readonly=True, states={'draft': [('readonly', False)]}, oldname="type")
    name = fields.Char('Payment Memo',
        readonly=True, states={'draft': [('readonly', False)]}, default='',copy=False)
    date = fields.Date("Bill Date", readonly=True,
        index=True, states={'draft': [('readonly', False)]},
        copy=False, default=fields.Date.context_today)
    account_date = fields.Date("Accounting Date",
        readonly=True, index=True, states={'draft': [('readonly', False)]},
        help="Effective date for accounting entries", copy=False, default=fields.Date.context_today)
    journal_id = fields.Many2one('account.journal', 'Journal',
                    domain="[('type', 'in', ['cash', 'bank'])]",
        required=True, readonly=True, states={'draft': [('readonly', False)]}, default=_default_journal)
    payment_journal_id = fields.Many2one('account.journal', string='Payment Method', readonly=True,
        states={'draft': [('readonly', False)]}, domain="[('type', 'in', ['cash', 'bank'])]", default=_default_payment_journal)
    account_id = fields.Many2one('account.account', 'Account',
        required=True, readonly=True, states={'draft': [('readonly', False)]},
        domain="[('deprecated', '=', False), ('internal_type','=', (voucher_type == 'purchase' and 'payable' or 'receivable'))]")
    line_ids = fields.One2many('account.voucher.line', 'voucher_id', 'Voucher Lines',
        readonly=True, copy=True,
        states={'draft': [('readonly', False)]})
    narration = fields.Text('Notes', readonly=True, states={'draft': [('readonly', False)]})
    currency_id = fields.Many2one('res.currency', compute='_get_journal_currency',
        string='Currency', readonly=True, store=True, default=lambda self: self._get_currency())
    company_id = fields.Many2one('res.company', 'Company',
        store=True, readonly=True, states={'draft': [('readonly', False)]},
        related='journal_id.company_id', default=lambda self: self._get_company())
    state = fields.Selection([
        ('draft', 'Draft'),
        ('cancel', 'Cancelled'),
        ('setdraft', 'Set To Draft'),
        ('proforma', 'Pro-forma'),
        ('posted', 'Posted')
        ], 'Status', readonly=True, track_visibility='onchange', copy=False, default='draft',
        help=" * The 'Draft' status is used when a user is encoding a new and unconfirmed Voucher.\n"
             " * The 'Pro-forma' status is used when the voucher does not have a voucher number.\n"
             " * The 'Posted' status is used when user create voucher,a voucher number is generated and voucher entries are created in account.\n"
             " * The 'Cancelled' status is used when user cancel voucher.")
    reference = fields.Char('Keterangan', readonly=True, states={'draft': [('readonly', False)]},
                                 help="The partner reference of this document.", copy=False)
    amount = fields.Monetary(string='Total', store=True, readonly=True, compute='_compute_total')
    tax_amount = fields.Monetary(readonly=True, store=True, compute='_compute_total')
    tax_correction = fields.Monetary(readonly=True, states={'draft': [('readonly', False)]},
        help='In case we have a rounding problem in the tax, use this field to correct it')
    number = fields.Char(readonly=True, copy=False)
    move_id = fields.Many2one('account.move', 'Journal Entry', copy=False)
    partner_id = fields.Many2one('res.partner', 'Partner', change_default=1, states={'posted': [('readonly', True)]})
    paid = fields.Boolean(compute='_check_paid', help="The Voucher has been totally paid.")
    pay_now = fields.Selection([
            ('pay_now', 'Pay Directly'),
            ('pay_later', 'Pay Later'),
        ], 'Payment', index=True, readonly=True, states={'draft': [('readonly', False)]}, default='pay_later')
    date_due = fields.Date('Due Date', readonly=True, index=True, states={'draft': [('readonly', False)]})
    currency_rate_id = fields.Many2one('res.currency',
        string='Currency', store=True, default=lambda self: self._get_currency())
    currency_name = fields.Char('Currency Name', related='currency_rate_id.name', store=True)
    currency_rate = fields.Float('Rate')
    journal_currency_name = fields.Char('Journal Currency', store=True, related='journal_id.currency_id.name')
    show_amount_currency = fields.Boolean('Show Currency', compute='_compute_show_amount_currency')
    account_analytic_id = fields.Many2one('account.analytic.account', string="Analytic Account", required=True)

    @api.onchange("line_ids", "account_analytic_id")
    def _onchange_line_ids(self):
        if self.account_analytic_id:
            for line in self.line_ids:
                line.account_analytic_id = self.account_analytic_id

    @api.depends('move_id.line_ids.reconciled', 'move_id.line_ids.account_id.internal_type')
    def _check_paid(self):
        self.paid = any([((line.account_id.internal_type, 'in', ('receivable', 'payable')) and line.reconciled) for line in self.move_id.line_ids])

    @api.model
    def _get_currency(self):
        journal = self.env['account.journal'].browse(self.env.context.get('default_journal_id', False))
        if journal.currency_id:
            return journal.currency_id.id
        return self.env.user.company_id.currency_id.id

    @api.model
    def _get_company(self):
        return self._context.get('company_id', self.env.user.company_id.id)

    @api.constrains('company_id', 'currency_id')
    def _check_company_id(self):
        for voucher in self:
            if not voucher.company_id:
                raise ValidationError(_("Missing Company"))
            if not voucher.currency_id:
                raise ValidationError(_("Missing Currency"))

    
    @api.depends('name', 'number')
    def name_get(self):
        return [(r.id, (r.number or _('Voucher'))) for r in self]

    
    @api.depends('journal_id', 'company_id')
    def _get_journal_currency(self):
        self.currency_id = self.journal_id.currency_id.id or self.company_id.currency_id.id
        self.currency_rate_id = self.journal_id.currency_id.id or self.company_id.currency_id.id

    
    @api.depends('tax_correction', 'line_ids.price_subtotal')
    def _compute_total(self):
        tax_calculation_rounding_method = self.env.user.company_id.tax_calculation_rounding_method
        for voucher in self:
            total = 0
            tax_amount = 0
            tax_lines_vals_merged = {}
            for line in voucher.line_ids:
                tax_info = line.tax_ids.compute_all(line.price_unit, voucher.currency_id, line.quantity, line.product_id, voucher.partner_id)
                if tax_calculation_rounding_method == 'round_globally':
                    total += tax_info.get('total_excluded', 0.0)
                    for t in tax_info.get('taxes', False):
                        key = (
                            t['id'],
                            t['account_id'],
                        )
                        if key not in tax_lines_vals_merged:
                            tax_lines_vals_merged[key] = t.get('amount', 0.0)
                        else:
                            tax_lines_vals_merged[key] += t.get('amount', 0.0)
                else:
                    total += tax_info.get('total_included', 0.0)
                    tax_amount += sum([t.get('amount', 0.0) for t in tax_info.get('taxes', False)])
            if tax_calculation_rounding_method == 'round_globally':
                tax_amount = sum([voucher.currency_id.round(t) for t in tax_lines_vals_merged.values()])
                voucher.amount = total + tax_amount + voucher.tax_correction
            else:
                voucher.amount = total + voucher.tax_correction
            voucher.tax_amount = tax_amount

    @api.onchange('date')
    def onchange_date(self):
        self.account_date = self.date

# mardin buat -->
    @api.onchange('journal_id')
    def change_account_id(self):
        if self.journal_id:
            self.account_id=self.journal_id.default_account_id.id
            if self.journal_id.currency_id.name == 'USD':
                self.currency_rate_id = self.journal_id.currency_id.id
            else:
                self.currency_rate_id = self.company_id.currency_id.id

#    @api.onchange('partner_id', 'pay_now')
#    def onchange_partner_id(self):
#        pay_journal_domain = [('type', 'in', ['cash', 'bank'])]
#        if self.partner_id:
#            self.account_id = self.partner_id.property_account_receivable_id \
#                if not self.voucher_type or self.voucher_type != 'purchase' else self.partner_id.property_account_payable_id
#        else:
#            if self.voucher_type == 'purchase':
#                pay_journal_domain.append(('outbound_payment_method_ids', '!=', False))
#            else:
#                pay_journal_domain.append(('inbound_payment_method_ids', '!=', False))
#        return {'domain': {'payment_journal_id': pay_journal_domain}}

    
    def proforma_voucher(self):
        self.action_move_line_create()

    
    def action_cancel_draft(self):
        self.write({'state': 'draft'})

    
    def cancel_voucher(self):
        for voucher in self:
            voucher.move_id.button_draft()
            voucher.move_id.button_cancel()
        self.write({'state': 'cancel', 'move_id': False})

    
    def unlink(self):
        for voucher in self:
            if voucher.state not in ('draft', 'cancel'):
                raise UserError(_('Cannot delete voucher(s) which are already opened or paid.'))
        return super(AccountVoucher, self).unlink()

    
    def first_move_line_get(self, move_id, company_currency, current_currency):
        debit = credit = 0.0
        if self.voucher_type == 'purchase':
            credit = self._convert(self.amount)
        elif not self.voucher_type or self.voucher_type != 'purchase':
            debit = self._convert(self.amount)

        if debit < 0.0: debit = 0.0
        if credit < 0.0: credit = 0.0
        if self.currency_rate > 0.0:
            if self.currency_id.name == self.currency_name:
                debit = debit * self.currency_rate
                credit = credit * self.currency_rate

        sign = debit - credit < 0 and -1 or 1
        #set the first line of the voucher
        move_line = {
                'name': self.name or '/',
                'debit': debit,
                'credit': credit,
                'account_id': self.account_id.id,
                'move_id': move_id,
                'journal_id': self.journal_id.id,
                'partner_id': self.partner_id.commercial_partner_id.id,
                'currency_id': company_currency != current_currency and current_currency or False,
                'amount_currency': (sign * abs(self.amount)  # amount < 0 for refunds
                    if company_currency != current_currency else 0.0),
                'date': self.account_date,
                'date_maturity': self.date_due,
                'analytic_account_id': self.account_analytic_id.id or False,
            }
        return move_line


    def account_move_get(self):
        if self.number:
            name = self.number
        elif self.journal_id.sequence_id:
            if not self.journal_id.sequence_id.active:
                raise UserError(_('Please activate the sequence of selected journal !'))
            name = self.journal_id.sequence_id.with_context(ir_sequence_date=self.date).next_by_id()
        else:
            raise UserError(_('Please define a sequence on the journal.'))

        move = {
            'name': name,
            'journal_id': self.journal_id.id,
            'narration': self.narration,
            'date': self.account_date,
            'ref': self.reference,
        }
        return move

    
    def _convert(self, amount):
        '''
        This function convert the amount given in company currency. It takes either the rate in the voucher (if the
        payment_rate_currency_id is relevant) either the rate encoded in the system.
        :param amount: float. The amount to convert
        :param voucher: id of the voucher on which we want the conversion
        :param context: to context to use for the conversion. It may contain the key 'date' set to the voucher date
            field in order to select the good rate to use.
        :return: the amount in the currency of the voucher's company
        :rtype: float
        '''
        for voucher in self:
            if voucher.currency_id != voucher.currency_rate_id: #idr != usd => run
                return voucher.currency_id._convert(amount, voucher.company_id.currency_id, voucher.company_id, voucher.account_date)
            # if voucher.journal_id.currency_id.name == 'USD' and voucher.currency_rate > 0.0:
            #     return voucher.currency_id._convert(amount, voucher.currency_rate_id, voucher.company_id,voucher.account_date)
            else:
                return voucher.currency_id._convert(amount, voucher.currency_rate_id, voucher.company_id, voucher.account_date)

    
    def voucher_pay_now_payment_create(self):
        if not self.voucher_type or self.voucher_type != 'purchase':
            payment_methods = self.journal_id.inbound_payment_method_ids
            payment_type = 'inbound'
            partner_type = 'customer'
            sequence_code = 'account.payment.customer.invoice'
        else:
            payment_methods = self.journal_id.outbound_payment_method_ids
            payment_type = 'outbound'
            partner_type = 'supplier'
            sequence_code = 'account.payment.supplier.invoice'

        return {
            'payment_type': payment_type,
            'payment_method_id': payment_methods and payment_methods[0].id or False,
            'partner_type': partner_type,
            'partner_id': self.partner_id.commercial_partner_id.id,
            'amount': self.amount,
            'currency_id': self.currency_id.id,
            'payment_date': self.date,
            'journal_id': self.payment_journal_id.id,
            'communication': self.name,
        }



    
    def voucher_move_line_create(self, line_total, move_id, company_currency, current_currency):
        '''
        Create one account move line, on the given account move, per voucher line where amount is not 0.0.
        It returns Tuple with tot_line what is total of difference between debit and credit and
        a list of lists with ids to be reconciled with this format (total_deb_cred,list_of_lists).

        :param voucher_id: Voucher id what we are working with
        :param line_total: Amount of the first line, which correspond to the amount we should totally split among all voucher lines.
        :param move_id: Account move wher those lines will be joined.
        :param company_currency: id of currency of the company to which the voucher belong
        :param current_currency: id of currency of the voucher
        :return: Tuple build as (remaining amount not allocated on voucher lines, list of account_move_line created in this method)
        :rtype: tuple(float, list of int)
        '''
        tax_calculation_rounding_method = self.env.user.company_id.tax_calculation_rounding_method
        tax_lines_vals = []
        for line in self.line_ids:
            #create one move line per voucher line where amount is not 0.0
            if not line.price_subtotal:
                continue
            line_subtotal = line.price_subtotal
            if not self.voucher_type or self.voucher_type != 'purchase':
                line_subtotal = -1 * line.price_subtotal
            # convert the amount set on the voucher line into the currency of the voucher's company
            amount = self._convert(line.price_unit*line.quantity)
            if self.journal_id.currency_id.name == 'USD':
                if self.currency_rate > 0:
                    # amount = self._convert(amount * self.currency_rate)
                    amount = amount * self.currency_rate
            move_line = {
                'journal_id': self.journal_id.id,
                'name': line.name or '/',
                'account_id': line.account_id.id,
                'move_id': move_id,
                'quantity': line.quantity,
                'product_id': line.product_id.id,
                'partner_id': self.partner_id.commercial_partner_id.id,
                'analytic_account_id': line.account_analytic_id and line.account_analytic_id.id or False,
                'analytic_tag_ids': [(6, 0, line.analytic_tag_ids.ids)],
                'credit': abs(amount) if not self.voucher_type or self.voucher_type != 'purchase' else 0.0,
                'debit': abs(amount) if self.voucher_type == 'purchase' else 0.0,
                'date': self.account_date,
                'tax_ids': [(4,t.id) for t in line.tax_ids],
                'amount_currency': line_subtotal if current_currency != company_currency else 0.0,
                'currency_id': company_currency != current_currency and current_currency or False,
                'payment_id': self._context.get('payment_id'),
            }
            # Create one line per tax and fix debit-credit for the move line if there are tax included
            if (line.tax_ids and tax_calculation_rounding_method == 'round_per_line'):
                tax_group = line.tax_ids.compute_all(self._convert(line.price_unit), self.company_id.currency_id, line.quantity, line.product_id, self.partner_id)
                if move_line['debit']: move_line['debit'] = tax_group['total_excluded']
                if move_line['credit']: move_line['credit'] = tax_group['total_excluded']
                if self.journal_id.currency_id.name == 'USD':
                    if self.currency_rate > 0.0:
                        if move_line['debit']: move_line['debit'] = tax_group['total_excluded'] * self.currency_rate
                        if move_line['credit']: move_line['credit'] = tax_group['total_excluded'] * self.currency_rate
                Currency = self.env['res.currency']
                company_cur = Currency.browse(company_currency)
                current_cur = Currency.browse(current_currency)
                for tax_vals in tax_group['taxes']:
                    if tax_vals['amount']:
                        tax = self.env['account.tax'].browse([tax_vals['id']])
                        account_id = (amount > 0 and tax_vals['account_id'] or tax_vals['refund_account_id'])
                        if not account_id: account_id = line.account_id.id
                        if tax_vals['amount'] > 0:
                            tax_vals_amount = tax_vals['amount']
                            if self.journal_id.currency_id.name == 'USD':
                                if self.currency_rate > 0.0:
                                    tax_vals_amount = tax_vals['amount'] * self.currency_rate
                            temp = {
                                'account_id': account_id,
                                'name': line.name + ' ' + tax_vals['name'],
                                'tax_line_id': tax_vals['id'],
                                'move_id': move_id,
                                'date': self.account_date,
                                'partner_id': self.partner_id.id,
                                'debit': self.voucher_type == 'purchase' and tax_vals_amount or 0.0, #--self.voucher_type != 'sale' and tax_vals['amount'] or 0.0,
                                'credit': self.voucher_type == False and tax_vals_amount or 0.0,
                                'analytic_account_id': line.account_analytic_id and line.account_analytic_id.id or False,
                            }
                        else:
                            temp = {
                                'account_id': account_id,
                                'name': line.name + ' ' + tax_vals['name'],
                                'tax_line_id': tax_vals['id'],
                                'move_id': move_id,
                                'date': self.account_date,
                                'partner_id': self.partner_id.id,
                                'debit': not self.voucher_type or self.voucher_type != 'purchase' and tax_vals[
                                    'amount'] or 0.0,
                                'credit': self.voucher_type != 'sale' and tax_vals['amount']*-1 or 0.0,
                                'analytic_account_id': line.account_analytic_id and line.account_analytic_id.id or False,
                            }
                        if company_currency != current_currency:
                            ctx = {}
                            sign = temp['credit'] and -1 or 1
                            amount_currency = company_cur._convert(tax_vals['amount'], current_cur, line.company_id,
                                                 self.account_date or fields.Date.today(), round=True)

                            if self.currency_rate > 0.0:
                                amount_currency = amount_currency * self.currency_rate
                                # amount_currency = tax_vals['amount'] * self.currency_rate

                            if self.account_date:
                                ctx['date'] = self.account_date
                            temp['currency_id'] = current_currency
                            temp['amount_currency'] = sign * abs(amount_currency)
                        self.env['account.move.line'].create(temp)

            # When global rounding is activated, we must wait until all tax lines are computed to
            # merge them.
            if tax_calculation_rounding_method == 'round_globally':
                # _apply_taxes modifies the dict move_line in place to account for included/excluded taxes
                tax_lines_vals += self.env['account.move.line'].with_context(round=False)._apply_taxes(
                    move_line,
                    move_line.get('debit', 0.0) - move_line.get('credit', 0.0)
                )
                # rounding False means the move_line's amount are not rounded
                currency = self.env['res.currency'].browse(company_currency)
                move_line['debit'] = currency.round(move_line['debit'])
                move_line['credit'] = currency.round(move_line['credit'])
            self.env['account.move.line'].create(move_line)

        # When round globally is set, we merge the tax lines
        if tax_calculation_rounding_method == 'round_globally':
            tax_lines_vals_merged = {}
            for tax_line_vals in tax_lines_vals:
                key = (
                    tax_line_vals['tax_line_id'],
                    tax_line_vals['account_id'],
                    tax_line_vals['analytic_account_id'],
                )
                if key not in tax_lines_vals_merged:
                    tax_lines_vals_merged[key] = tax_line_vals
                else:
                    tax_lines_vals_merged[key]['debit'] += tax_line_vals['debit']
                    tax_lines_vals_merged[key]['credit'] += tax_line_vals['credit']
            currency = self.env['res.currency'].browse(company_currency)
            for vals in tax_lines_vals_merged.values():
                vals['debit'] = currency.round(vals['debit'])
                vals['credit'] = currency.round(vals['credit'])
                self.env['account.move.line'].create(vals)
        return line_total

    
    def action_move_line_create(self):
        '''
        Confirm the vouchers given in ids and create the journal entries for each of them
        '''
        for voucher in self:
            local_context = dict(self._context)
            local_context['company_id'] = voucher.journal_id.company_id.id
            if voucher.move_id:
                continue
            company_currency = voucher.journal_id.company_id.currency_id.id
            current_currency = voucher.currency_id.id or company_currency
            # we select the context to use accordingly if it's a multicurrency case or not
            # But for the operations made by _convert, we always need to give the date in the context
            ctx = local_context.copy()
            ctx['date'] = voucher.account_date
            ctx['check_move_validity'] = False
            # Create the account move record.
            move = self.env['account.move'].create(voucher.account_move_get())
            # Get the name of the account_move just created
            # Create the first line of the voucher
            move_line = self.env['account.move.line'].with_context(ctx).create(voucher.with_context(ctx).first_move_line_get(move.id, company_currency, current_currency))
            line_total = move_line.debit - move_line.credit
            if not voucher.voucher_type or voucher.voucher_type != 'purchase':
                line_total = line_total - voucher._convert(voucher.tax_amount)
            elif voucher.voucher_type == 'purchase':
                # tax_amt = voucher._convert(voucher.tax_amount) * voucher.currency_rate if voucher.currency_rate > 0.0 else voucher._convert(voucher.tax_amount)
                tax_amt = voucher._convert(voucher.tax_amount)
                line_total = line_total + tax_amt
                # line_total = line_total + voucher._convert(voucher.tax_amount)
            # Create one move line per voucher line where amount is not 0.0
            line_total = voucher.with_context(ctx).voucher_move_line_create(line_total, move.id, company_currency, current_currency)

            # Create a payment to allow the reconciliation when pay_now = 'pay_now'.
            if voucher.pay_now == 'pay_now':
                payment_id = (self.env['account.payment']
                    .with_context(force_counterpart_account=voucher.account_id.id)
                    .create(voucher.voucher_pay_now_payment_create()))
                payment_id.post()

                # Reconcile the receipt with the payment
                lines_to_reconcile = (payment_id.move_line_ids + move.line_ids).filtered(lambda l: l.account_id == voucher.account_id)
                lines_to_reconcile.reconcile()

            # Add tax correction to move line if any tax correction specified
            if voucher.tax_correction != 0.0:
                tax_move_line = self.env['account.move.line'].search([('move_id', '=', move.id), ('tax_line_id', '!=', False)], limit=1)
                if len(tax_move_line):
                    tax_move_line.write({'debit': tax_move_line.debit + voucher.tax_correction if tax_move_line.debit > 0 else 0,
                        'credit': tax_move_line.credit + voucher.tax_correction if tax_move_line.credit > 0 else 0})

            # We post the voucher.
            voucher.write({
                'move_id': move.id,
                'state': 'posted',
                'number': move.name
            })
            move.action_post()
            if voucher.move_id.name != voucher.number:
                # search_move = self.env['account.move'].search([('name', '=', voucher.number)], limit=1)
                search_del_move = self.env['account.move'].search([('name', '=', voucher.move_id.name)], limit=1)
                # if search_move:
                #     voucher.move_id = search_move.id
                if search_del_move:
                    search_del_move.write({'name': voucher.number})
                if voucher.journal_id.sequence_id:
                    voucher.journal_id.sequence_id.write({
                        'number_next_actual': voucher.journal_id.sequence_id.number_next_actual - 1
                    })
        return True

    
    def _track_subtype(self, init_values):
        if 'state' in init_values:
            return self.env.ref('cash_management.mt_voucher_state_change')
        return super(AccountVoucher, self)._track_subtype(init_values)

    
    @api.depends('currency_name', 'journal_currency_name')
    def _compute_show_amount_currency(self):
        show_amount_currency = False
        # IDR-IDR = HIDE
        # IDR-USD = SHOW
        # IDR-FALSE = HIDE
        # USD-FALSE = HIDE
        # USD-USD = HIDE
        # USD-IDR = HIDE
        if (self.currency_name != 'USD' and self.journal_currency_name != 'IDR') or \
                (self.currency_name == self.journal_currency_name):
            self.show_amount_currency = True
        else:
            self.show_amount_currency = False

class AccountVoucherLine(models.Model):
    _name = 'account.voucher.line'
    _description = 'Accounting Voucher Line'

    name = fields.Text(string='Description', required=True)
    sequence = fields.Integer(default=10,
        help="Gives the sequence of this line when displaying the voucher.")
    voucher_id = fields.Many2one('account.voucher', 'Voucher', required=1, ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Product',
        ondelete='set null', index=True)
    account_id = fields.Many2one('account.account', string='Account',
        required=True, domain=[('deprecated', '=', False)],
        help="The income or expense account related to the selected product.")
    price_unit = fields.Float(string='Unit Price', required=True, digits=dp.get_precision('Product Price'), oldname='amount')
    price_subtotal = fields.Monetary(string='Amount',
        store=True, readonly=True, compute='_compute_subtotal')
    quantity = fields.Float(digits=dp.get_precision('Product Unit of Measure'),
        required=True, default=1)
    account_analytic_id = fields.Many2one('account.analytic.account', 'Analytic Account')
    analytic_tag_ids = fields.Many2many('account.analytic.tag', string='Analytic Tags')
    company_id = fields.Many2one('res.company', related='voucher_id.company_id', string='Company', store=True, readonly=True)
    tax_ids = fields.Many2many('account.tax', string='Tax', help="Only for tax excluded from price")
    currency_id = fields.Many2one('res.currency', related='voucher_id.currency_id', readonly=False)
    currency_rate_id = fields.Many2one('res.currency', related='voucher_id.currency_rate_id', readonly=True,store=True)
    currency_name = fields.Char('Currency Name ', store=True, compute='_compute_currency_name')
    journal_currency_name = fields.Char('Journal Cur Name ',store=True, compute='_compute_currency_name')
    currency_rate = fields.Float('Rate', compute='_compute_currency_rate',related='voucher_id.currency_rate', store=True)
    price_rate = fields.Float('Amount Currency')

    @api.onchange("line_ids")
    def _onchange_line_ids(self):
        res = super()._onchange_line_ids()
        if self.account_analytic_id:
            for line in self.line_ids:
                line.account_analytic_id = self.account_analytic_id
        return res
    
    @api.depends('voucher_id')
    def _compute_currency_rate(self):
        self.currency_rate = self.voucher_id.currency_rate

    @api.onchange('price_rate')
    def _onchange_price_rate(self):
        if not self.price_rate:
            return

        self.price_unit = self.price_rate * self.currency_rate


    
    @api.depends('price_unit', 'tax_ids', 'quantity', 'product_id', 'voucher_id.currency_id')
    def _compute_subtotal(self):
        self.price_subtotal = self.quantity * self.price_unit
        if self.tax_ids:
            taxes = self.tax_ids.compute_all(self.price_unit, self.voucher_id.currency_id, self.quantity, product=self.product_id, partner=self.voucher_id.partner_id)
            self.price_subtotal = taxes['total_excluded']

    @api.onchange('product_id', 'voucher_id', 'price_unit', 'company_id')
    def _onchange_line_details(self):
        if not self.voucher_id or not self.product_id or not self.voucher_id.partner_id:
            return
        onchange_res = self.product_id_change(
            self.product_id.id,
            self.voucher_id.partner_id.id,
            self.price_unit,
            self.company_id.id,
            self.voucher_id.currency_id.id,
            self.voucher_id.voucher_type)
        for fname, fvalue in onchange_res['value'].items():
            setattr(self, fname, fvalue)

    def _get_account(self, product, fpos, type):
        accounts = product.product_tmpl_id.get_product_accounts(fpos)
        if type == 'sale':
            return accounts['income']
        return accounts['expense']

    
    def product_id_change(self, product_id, partner_id=False, price_unit=False, company_id=None, currency_id=None, type=None):
        # TDE note: mix of old and new onchange badly written in 9, multi but does not use record set
        context = self._context
        company_id = company_id if company_id is not None else context.get('company_id', False)
        company = self.env['res.company'].browse(company_id)
        currency = self.env['res.currency'].browse(currency_id)
        if not partner_id:
            raise UserError(_("You must first select a partner."))
        part = self.env['res.partner'].browse(partner_id)
        if part.lang:
            self = self.with_context(lang=part.lang)

        product = self.env['product.product'].browse(product_id)
        fpos = part.property_account_position_id
        account = self._get_account(product, fpos, type)
        values = {
            'name': product.partner_ref,
            'account_id': account.id,
        }

        if type == 'purchase':
            values['price_unit'] = price_unit or product.standard_price
            taxes = product.supplier_taxes_id or account.tax_ids
            if product.description_purchase:
                values['name'] += '\n' + product.description_purchase
        else:
            values['price_unit'] = price_unit or product.lst_price
            taxes = product.taxes_id or account.tax_ids
            if product.description_sale:
                values['name'] += '\n' + product.description_sale

        values['tax_ids'] = taxes.ids

        if company and currency:
            if company.currency_id != currency:
                if type == 'purchase':
                    values['price_unit'] = price_unit or product.standard_price
                values['price_unit'] = values['price_unit'] * currency.rate

        return {'value': values, 'domain': {}}

    
    @api.depends('voucher_id')
    def _compute_currency_name(self):
        self.currency_name = self.voucher_id.currency_name
        self.journal_currency_name = self.voucher_id.journal_currency_name


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    # Allows to force the destination account
    # for receivable/payable
    #
    # @override
    def _get_counterpart_move_line_vals(self, invoice=False):
        values = super(AccountPayment, self)._get_counterpart_move_line_vals(invoice)

        if self._context.get('force_counterpart_account'):
            values['account_id'] = self._context['force_counterpart_account']

        return values
