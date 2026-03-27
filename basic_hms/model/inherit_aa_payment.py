from odoo import models, fields, api, _

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account', store=True)



