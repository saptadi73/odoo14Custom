from odoo import api, fields, models
from odoo import tools
from odoo.exceptions import UserError
from odoo.tools import float_compare
from odoo.tools.misc import formatLang
from dateutil.relativedelta import relativedelta

class AccountMove(models.Model):
    _inherit = 'account.move'

    categ_asset_id = fields.Many2one('account.asset.category', string='Category')
    asset_type = fields.Selection([('sale', 'Sale: Revenue Recognition'), ('purchase', 'Purchase: Asset'), ('expense', 'Deferred Expense')], index=True, readonly=False, states={'draft': [('readonly', False)]})
#     remaining_value = fields.Monetary(string='Depreciable Value', copy=False)
#     depreciated_value = fields.Monetary(string='Cumulative Depreciation', copy=False)


    # def _reverse_moves(self, default_values_list=None, cancel=False):
    #     for move in self:
    #         # Report the value of this move to the next draft move or create a new one
    #         if move.asset_id:
    #             # Set back the amount in the asset as the depreciation is now void
    #             move.asset_id.value_residual += move.amount_total
    #             # Recompute the status of the asset for all depreciations posted after the reversed entry
    #             for later_posted in move.asset_id.depreciation_move_ids.filtered(lambda m: m.date >= move.date and m.state == 'posted'):
    #                 later_posted.depreciated_value -= move.amount_total
    #                 later_posted.remaining_value += move.amount_total
    #             first_draft = min(move.asset_id.depreciation_move_ids.filtered(lambda m: m.state == 'draft'), key=lambda m: m.date, default=None)
    #             if first_draft:
    #                 # If there is a draft, simply move/add the depreciation amount here
    #                 # The depreciated and remaining values don't need to change
    #                 first_draft.amount_total += move.amount_total
    #             else:
    #                 # If there was no raft move left, create one
    #                 last_date = max(move.asset_id.depreciation_move_ids.mapped('date'))
    #                 method_period = move.asset_id.method_period

    #                 self.create(self._prepare_move_for_asset_depreciation({
    #                     'asset_id': move.asset_id,
    #                     'move_ref': _('Report of reversal for {name}').format(move.asset_id.name),
    #                     'amount': move.amount_total,
    #                     'date': last_date + (relativedelta(months=1) if method_period == "1" else relativedelta(years=1)),
    #                     'depreciated_value': move.amount_total + max(move.asset_id.depreciation_move_ids.mapped('depreciated_value')),
    #                     'remaining_value': 0,
    #                 }))

    #             msg = _('Depreciation entry %s reversed (%s)') % (move.name, formatLang(self.env, move.amount_total, currency_obj=move.company_id.currency_id))
    #             move.asset_id.message_post(body=msg)

#             # If an asset was created for this move, delete it when reversing the move
#             for line in move.line_ids:
#                 if line.asset_id.state == 'draft' or all(state == 'draft' for state in line.asset_id.depreciation_move_ids.mapped('state')):
#                     line.asset_id.state = 'draft'
#                     line.asset_id.unlink()

#         return super(AccountMove, self)._reverse_moves(default_values_list, cancel)

#     @api.model
#     def _prepare_move_for_asset_depreciation(self, vals):
#         missing_fields = set(['asset_id', 'move_ref', 'amount', 'remaining_value', 'depreciated_value']) - set(vals)
#         if missing_fields:
#             raise UserError(_('Some fields are missing {}').format(', '.join(missing_fields)))
#         asset = vals['asset_id']
#         account_analytic_id = asset.account_analytic_id
#         analytic_tag_ids = asset.analytic_tag_ids
#         depreciation_date = vals.get('date', fields.Date.context_today(self))
#         company_currency = asset.company_id.currency_id
#         current_currency = asset.currency_id
#         prec = company_currency.decimal_places
#         amount = current_currency._convert(vals['amount'], company_currency, asset.company_id, depreciation_date)
#         move_line_1 = {
#             'name': asset.name,
#             'account_id': asset.account_depreciation_id.id,
#             'debit': 0.0 if float_compare(amount, 0.0, precision_digits=prec) > 0 else -amount,
#             'credit': amount if float_compare(amount, 0.0, precision_digits=prec) > 0 else 0.0,
#             'analytic_account_id': account_analytic_id.id if asset.asset_type == 'sale' else False,
#             'analytic_tag_ids': [(6, 0, analytic_tag_ids.ids)] if asset.asset_type == 'sale' else False,
#             'currency_id': company_currency != current_currency and current_currency.id or False,
#             'amount_currency': company_currency != current_currency and - 1.0 * vals['amount_total'] or 0.0,
#         }
#         move_line_2 = {
#             'name': asset.name,
#             'account_id': asset.account_depreciation_expense_id.id,
#             'credit': 0.0 if float_compare(amount, 0.0, precision_digits=prec) > 0 else -amount,
#             'debit': amount if float_compare(amount, 0.0, precision_digits=prec) > 0 else 0.0,
#             'analytic_account_id': account_analytic_id.id if asset.asset_type in ('purchase', 'expense') else False,
#             'analytic_tag_ids': [(6, 0, analytic_tag_ids.ids)] if asset.asset_type in ('purchase', 'expense') else False,
#             'currency_id': company_currency != current_currency and current_currency.id or False,
#             'amount_currency': company_currency != current_currency and vals['amount_total'] or 0.0,
#         }
#         move_vals = {
#             'ref': vals['move_ref'],
#             'date': depreciation_date,
#             'journal_id': asset.journal_id.id,
#             'line_ids': [(0, 0, move_line_1), (0, 0, move_line_2)],
#             'auto_post': asset.state == 'open',
#             'asset_id': asset.id,
#             'remaining_value': vals['emaining_value'],
#             'depreciated_value': vals['depreciated_value'],
#             'amount_total': amount,
#             'name': '/',
#             'asset_value_change': vals.get('asset_value_change', False),
#             'type': 'entry',
#         }
#         return move_vals

#     @api.model
#     def create_asset_move(self, vals):
#         move_vals = self._prepare_move_for_asset_depreciation(vals)
#         return self.env['account.move'].create(move_vals)