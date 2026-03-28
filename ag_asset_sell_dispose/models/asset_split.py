
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_is_zero
from math import copysign
from odoo.tools import float_compare
from odoo.tools.misc import formatLang




class AccountAssetAsset(models.Model):
    _inherit = 'account.asset.asset'

    sales_value = fields.Float(string='Sale Value')
    children_ids = fields.One2many('account.asset.asset', 'parent_id', help="The children are the gains in value of this asset")
    parent_id = fields.Many2one('account.asset.asset', help="An asset has a parent when it is the result of gaining value")
    #depreciation_move_ids = fields.One2many('account.move', 'asset_id', string='Depreciation Lines', readonly=True, states={'draft': [('readonly', False)], 'open': [('readonly', False)], 'paused': [('readonly', False)]})
    disposal_date = fields.Date(readonly=True, states={'draft': [('readonly', False)]},)
    asset_type = fields.Selection([('sale', 'Sale: Revenue Recognition'), ('purchase', 'Purchase: Asset'), ('expense', 'Deferred Expense')], index=True, readonly=False, states={'draft': [('readonly', False)]})
    account_analytic_id = fields.Many2one('account.analytic.account')

    def action_set_to_close(self):
        """ Returns an action opening the asset pause wizard."""
        self.ensure_one()
        # new_wizard = self.env['account.asset.sell'].create({
        #     'asset_id': self.id,
        #     'action':'sell',
        # })
        return {
            'name': _('Sell Asset'),
            'view_mode': 'form',
            'res_model': 'account.asset.sell',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context':{
                'default_assets_id': self.id,
            }
            # 'res_id': new_wizard.id,
        }

    # def action_set_to_close(self):
    #     """ Returns an action opening the asset pause wizard."""
    #     self.ensure_one()
    #     new_wizard = self.env['account.asset.sell'].create({
    #         'assets_id': self.id,
    #     })
    #     return {
    #         'name': _('Sell Asset'),
    #         'view_mode': 'form',
    #         'res_model': 'account.asset.sell',
    #         'type': 'ir.actions.act_window',
    #         'target': 'new',
    #         'res_id': new_wizard.id,
    #     }

    def set_to_close(self, invoice_line_id, date=None):
        #res = super(AccountAssetAsset, self).set_to_close()
        print('---set_to_close---')

        for rec in self:
            rec.ensure_one()
            disposal_date = date or fields.Date.today()

            if invoice_line_id and rec.children_ids:
                raise UserError("You cannot automate the journal entry for an asset that has had a gross increase. Please use 'Dispose' and modify the entries.")
            move_ids = rec._get_disposal_moves([invoice_line_id], disposal_date)
            rec.write({'state': 'close', 'disposal_date': disposal_date})
            if move_ids:
                # raise UserError("test2")
                return rec._return_disposal_view(move_ids)
        #return res







    # def set_to_running(self):
    #     if self.depreciation_line_ids and not max(self.depreciation_line_ids, key=lambda m: m.move_id.date).asset_remaining_value == 0:
    #         self.env['asset.modify'].create({'asset_id': self.id, 'name': _('Reset to running')}).modify()
    #     self.write({'state': 'open', 'disposal_date': False})

    def _return_disposal_view(self, move_ids):
        name = _('Disposal Move')
        view_mode = 'form'
        if len(move_ids) > 1:
            name = _('Disposal Moves')
            view_mode = 'tree,form'
        return {
            'name': name,
            'view_mode': view_mode,
            'res_model': 'account.move',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'res_id': move_ids[0],
            'domain': [('id', 'in', move_ids)]
        }


    def _get_disposal_moves(self, invoice_line_ids, disposal_date):
        def get_line(asset, amount, account):
            return (0, 0, {
                'name': asset.name,
                'account_id': account.id,
                'debit': 0.0 if float_compare(amount, 0.0, precision_digits=prec) > 0 else -amount,
                'credit': amount if float_compare(amount, 0.0, precision_digits=prec) > 0 else 0.0,
                # 'analytic_account_id': account_analytic_id.id if asset.asset_type == 'sale' else False,
                # 'analytic_tag_ids': [(6, 0, analytic_tag_ids.ids)] if asset.asset_type == 'sale' else False,
                'currency_id': company_currency != current_currency and current_currency.id or False,
                'amount_currency': company_currency != current_currency and - 1.0 * asset.value_residual or 0.0,
            })

        move_ids = []
        assert len(self) == len(invoice_line_ids)
        for asset, invoice_line_id in zip(self, invoice_line_ids):
            if disposal_date < max(asset.depreciation_line_ids.filtered(
                    lambda x: not x.move_id.reversal_move_id and x.move_id.state == 'posted').mapped('move_id.date') or [fields.Date.today()]): #.mapped('date')
                if invoice_line_id:
                    raise UserError(
                        'There are depreciation posted after the invoice date (%s).\nPlease revert them or change the date of the invoice.' % disposal_date)
                else:
                    raise UserError('There are depreciation posted in the future, please revert them.')
            # Also dispose of the children
            # This is not implemented for selling with an invoice.
            if not invoice_line_id and asset.children_ids:
                move_ids += asset.children_ids._get_disposal_moves(
                    [self.env['account.move.line']] * len(asset.children_ids), disposal_date)
            # account_analytic_id = asset.account_analytic_id
            # analytic_tag_ids = asset.analytic_tag_ids
            company_currency = asset.company_id.currency_id
            current_currency = asset.currency_id
            prec = company_currency.decimal_places
            unposted_depreciation_line_ids = asset.depreciation_line_ids.filtered(lambda x: not x.move_check)
            if unposted_depreciation_line_ids:
                old_values = {
                    'method_end': asset.method_end,
                    'method_number': asset.method_number,
                }

                # Remove all unposted depr. lines
                commands = [(2, line_id.id, False) for line_id in unposted_depreciation_line_ids]

                # Create a new depr. line with the residual amount and post it
                asset_sequence = len(asset.depreciation_line_ids) - len(unposted_depreciation_line_ids) + 1

                initial_amount = asset.value
                initial_account = asset.category_id.account_asset_id
                depreciated_amount = asset.value_residual - initial_amount
                # copysign(
                #     sum(asset.depreciation_line_ids.filtered(lambda r: r.move_id.state == 'posted').mapped('amount')),
                #     -initial_amount)
                depreciation_account = asset.category_id.account_depreciation_id
                invoice_amount = copysign(invoice_line_id.price_subtotal, -initial_amount)
                invoice_account = invoice_line_id.account_id
                difference = -initial_amount - depreciated_amount - invoice_amount
                difference_account = asset.company_id.gain_account_id if difference > 0 else asset.company_id.loss_account_id
                line_datas = [(initial_amount,initial_account), (depreciated_amount, depreciation_account),#initial_account
                              (invoice_amount, invoice_account), (difference, difference_account)]
                print("******************************************************************\n")
                print(initial_amount)
                print("\n")
                print(initial_account)
                print("\n")
                print(depreciated_amount)
                print("\n")
                print(depreciation_account)
                print("\n")
                print(invoice_amount)
                print("\n")
                print(invoice_account)
                print("\n")
                print(difference)
                print("\n")
                print(difference_account)
                print("\n\n\n")
                if not invoice_line_id:
                    del line_datas[2]
                # raise UserError(asset_sequence)
                seq_name = asset.name + ': ' + (_('Disposal') if not invoice_line_id else _('Sale'))
                vals = {
                    'asset_id': asset.id,
                    'amount': asset.value_residual ,
                    'name': seq_name,
                    'sequence': asset_sequence,
                    'remaining_value': 0.0,
                    'depreciated_value':  0.0,
                    'depreciation_date': disposal_date,
                   # 'journal_id': asset.category_id.journal_id.id,
                #    'move_lines': ,
                    # 'move_id': [get_line(asset, amount, account) for amount, account in line_datas if account],
                }
                move_lines = [get_line(asset, amount, account) for amount, account in line_datas if account]
                commands.append((0, 0, vals))
                asset.write({'depreciation_line_ids': commands,'method_number': asset_sequence})
                # raise UserError("test2")
                tracked_fields = self.env['account.asset.asset'].fields_get(['method_number','method_end'])
                changes, tracking_value_ids = asset._message_track(tracked_fields, old_values)
                if changes:
                    asset.message_post(body=_('Asset sold or disposed. Accounting entry awaiting for validation.'),
                                       tracking_value_ids=tracking_value_ids)
                #move_ids += self.env['account.move'].search([('asset_id', '=', asset.id), ('state', '=', 'draft')]).ids
                print("********************************************************************************************\n")
                print(move_lines)
                print("\n********************************************************************************************")
                move_ids += asset.depreciation_line_ids[-1].create_move(post_move=False)

        return move_ids


class AccountAssetDepreciationLine(models.Model):
    _inherit = 'account.asset.depreciation.line'

    def _prepare_move(self, line,move_lines=None):

        category_id = line.asset_id.category_id
        # account_analytic_id = line.asset_id.account_analytic_id
        # analytic_tag_ids = line.asset_id.analytic_tag_ids
        depreciation_date = self.env.context.get(
            'depreciation_date') or line.depreciation_date or fields.Date.context_today(self)
        company_currency = line.asset_id.company_id.currency_id
        current_currency = line.asset_id.currency_id
        prec = company_currency.decimal_places
        amount = current_currency._convert(
            line.amount, company_currency, line.asset_id.company_id, depreciation_date)
        asset_name = line.asset_id.name + ' (%s/%s)' % (line.sequence, len(line.asset_id.depreciation_line_ids))#+ '/' +line.asset_id.asset_code
        #asset_code_id = line.asset_id.asset_code + ' (%s/%s)' % (line.sequence, len(line.asset_id.depreciation_line_ids))
        move_line_1 = {
            'name': asset_name,
            # 'asset_category_id': category_id.id,
            'account_id': category_id.account_depreciation_id.id,
            'debit': 0.0 if float_compare(amount, 0.0, precision_digits=prec) > 0 else -amount,
            'credit': amount if float_compare(amount, 0.0, precision_digits=prec) > 0 else 0.0,
            'partner_id': line.asset_id.partner_id.id,
            # 'analytic_account_id': account_analytic_id.id if category_id.type == 'sale' else False,
            # 'analytic_tag_ids': [(6, 0, analytic_tag_ids.ids)] if category_id.type == 'sale' else False,
            'currency_id': company_currency != current_currency and current_currency.id or False,
            'amount_currency': company_currency != current_currency and - 1.0 * line.amount or 0.0,
        }
        move_line_2 = {
            'name': asset_name,
            #  'asset_category_id': category_id.id,
            'account_id': category_id.account_depreciation_expense_id.id,
            'credit': 0.0 if float_compare(amount, 0.0, precision_digits=prec) > 0 else -amount,
            'debit': amount if float_compare(amount, 0.0, precision_digits=prec) > 0 else 0.0,
            'partner_id': line.asset_id.partner_id.id,
            # 'analytic_account_id': account_analytic_id.id if category_id.type == 'purchase' else False,
            # 'analytic_tag_ids': [(6, 0, analytic_tag_ids.ids)] if category_id.type == 'purchase' else False,
            'currency_id': company_currency != current_currency and current_currency.id or False,
            'amount_currency': company_currency != current_currency and line.amount or 0.0,
        }
        # move_vals = {
        #     'ref': line.asset_id.name + '/' + line.asset_id.asset_code,
        #     'date': depreciation_date or False,
        #     'journal_id': category_id.journal_id.id,
        #     'categ_asset_id': category_id.id,
        #     'line_ids': [(0, 0, move_line_1), (0, 0, move_line_2)],
        # }
        if move_lines:
            move_vals = {
                'ref': line.asset_id.code,
                'date': depreciation_date or False,
                'journal_id': category_id.journal_id.id,
                'categ_asset_id': category_id.id,
                'line_ids': move_lines,
            }
        else:
            move_vals = {
                'ref': line.asset_id.code,
                'date': depreciation_date or False,
                'journal_id': category_id.journal_id.id,
                'categ_asset_id': category_id.id,
                'line_ids': [(0, 0, move_line_1), (0, 0, move_line_2)],
            }
        return move_vals





    def _prepare_move_grouped(self):
        asset_id = self[0].asset_id
        category_id = asset_id.category_id  # we can suppose that all lines have the same category
        # account_analytic_id = asset_id.account_analytic_id
        # analytic_tag_ids = asset_id.analytic_tag_ids
        depreciation_date = self.env.context.get('depreciation_date') or fields.Date.context_today(self)
        amount = 0.0
        for line in self:
            # Sum amount of all depreciation lines
            company_currency = line.asset_id.company_id.currency_id
            current_currency = line.asset_id.currency_id
            company = line.asset_id.company_id
            amount += current_currency._convert(line.amount, company_currency, company, fields.Date.today())

        name = category_id.name + _(' (grouped)')
        move_line_1 = {
            'name': name,
            'account_id': category_id.account_depreciation_id.id,
            'debit': 0.0,
            'credit': amount,
            'journal_id': category_id.journal_id.id,
            # 'analytic_account_id': account_analytic_id.id if category_id.type == 'sale' else False,
            # 'analytic_tag_ids': [(6, 0, analytic_tag_ids.ids)] if category_id.type == 'sale' else False,
        }
        move_line_2 = {
            'name': name,
            'account_id': category_id.account_depreciation_expense_id.id,
            'credit': 0.0,
            'debit': amount,
            'journal_id': category_id.journal_id.id,
            # 'analytic_account_id': account_analytic_id.id if category_id.type == 'purchase' else False,
            # 'analytic_tag_ids': [(6, 0, analytic_tag_ids.ids)] if category_id.type == 'purchase' else False,
        }
        move_vals = {
            'ref': category_id.name,
            'date': depreciation_date or False,
            'journal_id': category_id.journal_id.id,
            'categ_asset_id': category_id.id,
            'line_ids': [(0, 0, move_line_1), (0, 0, move_line_2)],
        }

        return move_vals

