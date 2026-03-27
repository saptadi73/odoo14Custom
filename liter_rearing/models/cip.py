# from odoo import models, fields, api
#
# class Cip(models.Model):
#     _name = "cip"
#     _inherit = ['mail.thread', 'mail.activity.mixin']
#     _description = "CIP"
#     _rec_name = 'name'
#
#     name = fields.Char('CIP Name')
#     category_id = fields.Many2one('type.cip', 'CIP Category')
#     ref = fields.Char('Reference')
#     date = fields.Date('Date')
#     account_analytic_id = fields.Many2one('account.analytic.account')
#     eartag_id = fields.Char('Eartag ID')
#     sapi_id = fields.Many2one('sapi', 'Sapi')
#     company_id = fields.Many2one('res.company', 'Company')
#     gross_value = fields.Float('Gross Value')
#
# class TypeCip(models.Model):
#     _name = "type.cip"
#     _inherit = ['mail.thread', 'mail.activity.mixin']
#     _description = "Tipe CIP"
#
#     kode = fields.Char('Kode')
#     name = fields.Char('Category Name')
#     account_id = fields.Many2one('account.account', 'Account')
#     company_id = fields.Many2one('res.company', 'Company')
