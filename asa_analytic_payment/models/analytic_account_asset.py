# Copyright 2020 Jesus Ramoneda <jesus.ramoneda@qubiq.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.tools import float_compare, float_is_zero
from odoo.exceptions import UserError


class AnalyticAccountAsset(models.Model):
    _inherit = "account.asset.asset"

    account_analytic_id     = fields.Many2one(
        comodel_name='account.analytic.account')
    analytic_id             = fields.Many2one(
        comodel_name='account.analytic.account')
    mutasi_asset_id         = fields.Many2one('account.asset.asset',string="Mutasi Asset")
    asset_count             = fields.Integer(compute='_asset_count', string='Asset Count')

    def _asset_count(self):
        for rec in self:
            asset_ids = self.env['account.asset.asset'].search([('mutasi_asset_id', '=', rec.id)])
            rec.asset_count = len(asset_ids)

    def action_view_asset(self):
        action = self.env.ref('base_accounting_kit.action_account_asset_asset_form').read()[0]
        action['context'] = {}
        action['domain'] = [('mutasi_asset_id', '=', self.id)]
        return action

    @api.onchange('category_id')
    def onchange_category_id(self):
        res = super(AnalyticAccountAsset, self).onchange_category_id()
        self.account_analytic_id = self.category_id.account_analytic_id
        return res

    def create_mutasi_asset(self):
        for rec in self :
            if not rec.mutasi_asset_id :
                comulative = 0
                val = 0
                for line in rec.depreciation_line_ids :
                    if line.move_check == True :
                        comulative += line.amount
                        val += 1

                vals = {    
                            'name'              : rec.name +'-'+'Mutasi',
                            'category_id'       : rec.category_id.id,
                            'code'              : rec.code,
                            'company_id'        : rec.company_id.id,
                            'value'             : rec.value,
                            'salvage_value'     : rec.salvage_value + comulative,
                            'value_residual'    : rec.value_residual,
                            'mutasi_asset_id'   : rec.id,
                            'method'            : rec.method,
                            'method_time'       : rec.method_time,
                            'prorata'           : rec.prorata,
                            'method_number'     : rec.method_number - val,
                            'method_period'     : rec.method_period,

                        }

                asset = self.env['account.asset.asset'].create(vals)
                rec.write({'state': 'close'})

                # for line in rec.depreciation_line_ids:
                #     if line.move_check == False :
                #         line_vals = {
                #                         'asset_id'          : asset.id,
                #                         'name'              : line.name,
                #                         'sequence'          : line.sequence,
                #                         'depreciated_value' : line.depreciated_value,
                #                         'amount'            : line.amount,
                #                         'remaining_value'   : line.remaining_value,
                #                         'depreciation_date' : line.depreciation_date,
                #                     }
                #         self.env['account.asset.depreciation.line'].create(line_vals)

            else :
                raise UserError(_("You can't create mutasi asset for this asset because mutasi asset is created."))



class AccountAssetLine(models.Model):
    _inherit = "account.asset.depreciation.line"


    def _set_analytic_account(self):
        def get_move_line(asset_line):
            return 1 if asset_line.asset_id.category_id.type == "sale" else 0
        for rec in self.filtered(
            lambda x: x.move_id and x.asset_id and
                x.asset_id.account_analytic_id):
            i = get_move_line(rec)
            rec.move_id.line_ids[i].analytic_account_id =\
                rec.asset_id.account_analytic_id

    # def write(self, values):
    #     res = super(AccountAssetLine, self).write(values)
    #     if values.get('move_id'):
    #         self._set_analytic_account()
    #     return res

    def create_move(self, post_move=True):
        created_moves = self.env['account.move']
        prec = self.env['decimal.precision'].precision_get('Account')
        if self.mapped('move_id'):
            raise UserError(_(
                'This depreciation is already linked to a journal entry! Please post or delete it.'))
        for line in self:
            category_id = line.asset_id.category_id
            depreciation_date = self.env.context.get(
                'depreciation_date') or line.depreciation_date or fields.Date.context_today(
                self)
            company_currency = line.asset_id.company_id.currency_id
            current_currency = line.asset_id.currency_id
            amount = current_currency.with_context(
                date=depreciation_date).compute(line.amount, company_currency)
            asset_name = line.asset_id.name + ' (%s/%s)' % (
            line.sequence, len(line.asset_id.depreciation_line_ids))
            partner = self.env['res.partner']._find_accounting_partner(
                line.asset_id.partner_id)
            move_line_1 = {
                'name': asset_name,
                'account_id': category_id.account_depreciation_id.id,
                'debit': 0.0 if float_compare(amount, 0.0,
                                              precision_digits=prec) > 0 else -amount,
                'credit': amount if float_compare(amount, 0.0,
                                                  precision_digits=prec) > 0 else 0.0,
                'journal_id': category_id.journal_id.id,
                'partner_id': partner.id,
                'analytic_account_id': line.asset_id.account_analytic_id.id,
                'currency_id': company_currency != current_currency and current_currency.id or False,
                'amount_currency': company_currency != current_currency and - 1.0 * line.amount or 0.0,
            }
            move_line_2 = {
                'name': asset_name,
                'account_id': category_id.account_depreciation_expense_id.id,
                'credit': 0.0 if float_compare(amount, 0.0,
                                               precision_digits=prec) > 0 else -amount,
                'debit': amount if float_compare(amount, 0.0,
                                                 precision_digits=prec) > 0 else 0.0,
                'journal_id': category_id.journal_id.id,
                'partner_id': partner.id,
                'analytic_account_id': line.asset_id.account_analytic_id.id,
                'currency_id': company_currency != current_currency and current_currency.id or False,
                'amount_currency': company_currency != current_currency and line.amount or 0.0,
            }
            move_vals = {
                'ref': line.asset_id.code,
                'date': depreciation_date or False,
                'journal_id': category_id.journal_id.id,
                'line_ids': [(0, 0, move_line_1), (0, 0, move_line_2)],
            }
            move = self.env['account.move'].create(move_vals)
            line.write({'move_id': move.id, 'move_check': True})
            created_moves |= move

        if post_move and created_moves:
            created_moves.filtered(lambda m: any(
                m.asset_depreciation_ids.mapped(
                    'asset_id.category_id.open_asset'))).post()
        return [x.id for x in created_moves]

    def create_grouped_move(self, post_move=True):
        if not self.exists():
            return []

        created_moves = self.env['account.move']
        category_id = self[
            0].asset_id.category_id  # we can suppose that all lines have the same category
        depreciation_date = self.env.context.get(
            'depreciation_date') or fields.Date.context_today(self)
        amount = 0.0
        for line in self:
            # Sum amount of all depreciation lines
            company_currency = line.asset_id.company_id.currency_id
            current_currency = line.asset_id.currency_id
            amount += current_currency.compute(line.amount, company_currency)

        name = category_id.name + _(' (grouped)')
        move_line_1 = {
            'name': name,
            'account_id': category_id.account_depreciation_id.id,
            'debit': 0.0,
            'credit': amount,
            'journal_id': category_id.journal_id.id,
            'analytic_account_id': line.asset_id.account_analytic_id.id,
        }
        move_line_2 = {
            'name': name,
            'account_id': category_id.account_depreciation_expense_id.id,
            'credit': 0.0,
            'debit': amount,
            'journal_id': category_id.journal_id.id,
            'analytic_account_id': line.asset_id.account_analytic_id.id,
        }
        move_vals = {
            'ref': category_id.name,
            'date': depreciation_date or False,
            'journal_id': category_id.journal_id.id,
            'line_ids': [(0, 0, move_line_1), (0, 0, move_line_2)],
        }
        move = self.env['account.move'].create(move_vals)
        self.write({'move_id': move.id, 'move_check': True})
        created_moves |= move

        if post_move and created_moves:
            self.post_lines_and_close_asset()
            created_moves.post()
        return [x.id for x in created_moves]
