# from odoo import api, fields, models
#
#
# class analytic_user(models.Model):
#
#     _inherit = "res.users"
#
#     analytic_ids = fields.Many2many(
#         comodel_name="account.analytic.account",
#         string="Analytic Account",
#         relation="analytic_account_res_users_rel",
#     )