
from odoo import api, fields, models
import string


class AccountFinancialReport(models.Model):
    _name = "ts.financial.report"
    _description = "Financial Statements Report"
    _rec_name = 'name'

    name = fields.Char('Report Name', required=True, translate=True)
    desc_before_date = fields.Char('Description Before Date')
    date_after_desc = fields.Boolean('Date Filter Addition in Heading')
    company_comparison = fields.Boolean('Enable Comparison of Company')
    sequence = fields.Integer('Sequence')
    level = fields.Integer(compute='_get_level', string='Level', store=True)
    report_line_ids = fields.One2many('ts.financial.report.line', 'parent_id', string='Report')
    analytic_comparison = fields.Boolean('Analytic Comparison')
    is_balance_sheet = fields.Boolean('Is Balance Sheet')
    
    
class TsFinancialReportLine(models.Model):
    _name = "ts.financial.report.line"
    _description = "Financial Statements Report"
    _rec_name = 'name'
    _order = "sequence "
    
    @api.onchange('type','style_overwrite')
    def onchange_type_style(self):
        for rec in self:
            if rec.type == 'accounts' and rec.style_overwrite == '6':
                rec.acc_visibile = True
            else:
                rec.acc_visibile = False
            if rec.type == 'account_type' and rec.style_overwrite == '6':
                rec.acc_type_visibile = True
            else:
                rec.acc_type_visibile = False
            if rec.type == 'account_group' and rec.style_overwrite == '6':
                rec.acc_group_visibile = True
            else:
                rec.acc_group_visibile = False
    
    name = fields.Char('Report Name', required=True, translate=True)
    parent_id = fields.Many2one('ts.financial.report', string="Report")
    sequence = fields.Float('Sequence')
    style_overwrite = fields.Selection(
        [('1', ' Simple Group  Layout (Format 1)'),
         ('2', ' Total Layout Format  with Boxes (Layout 2)'),
         ('3', ' Add Layout with Heading'),
         ('4', ' Layout Format with Upper Heading 3'),
         ('5', ' Add Layout With Lower Border (Format 4)'),
         ('6', 'Ratios with Percentage Heading')],
        'Financial Report Style',
        help="You can set up here the format you want this"
             " record to be displayed. If you leave the"
             " automatic formatting, it will be computed"
             " based on the financial reports hierarchy "
             "(auto-computed field 'level').")
    
    type = fields.Selection(
        [('sum', 'View'),
         ('accounts', 'Accounts'),
         ('account_type', 'Account Type'),
         ('account_group', 'Account Group'),
         ('report_value', 'Report Value')
         ], 'Type', default='sum')
    
    account_ids = fields.Many2many('account.account',string='Accounts')
    account_type_ids = fields.Many2many('account.account.type', string='Account Types')
    account_group_ids = fields.Many2many('account.group', string='Account Groups')
    report_line_ids = fields.Many2many('ts.financial.report.line','financial_report_line',
        'fr_report_id', 'fr_line_id', string='Report Values')
    upper_figures = fields.Float('Upper Figures')
    lower_figures = fields.Float('Lower Figures')
    
    numerator_account_ids = fields.Many2many('account.account','account_account_num_acc',
        'na_report_id', 'num_account_acc_id',string='Numerator Accounts')
    denominator_account_ids = fields.Many2many('account.account','account_account_den_acc',
        'den_report_id', 'den_account_acc_id',string='Denominator Accounts')
    acc_visibile = fields.Boolean('Acc Visible')
    
    numerator_acc_type_ids = fields.Many2many('account.account.type','account_account_num_type',
        'nt_report_id', 'num_account_type_id',
        'Numerator Acc Types')
    denominator_acc_type_ids = fields.Many2many('account.account.type','account_account_den_type',
        'dt_report_id', 'den_account_type_id',string='Denominator Acc Types')
    acc_type_visibile = fields.Boolean('Acc Type Visible')
    
    numerator_acc_group_ids = fields.Many2many('account.group','account_account_num_grp',
        'ng_report_id', 'num_account_grp_id',string='Numerator Acc Groups')
    denominator_acc_group_ids = fields.Many2many('account.group','account_account_den_grp',
        'dg_report_id', 'den_account_grp_id',string='Denominator Acc Groups')
    acc_group_visibile = fields.Boolean('Acc Group Visible')
    
    enable_percent_sign = fields.Boolean('Enable Percent Sign')
    reverse_balance_sign = fields.Boolean('Reverse balance sign')


    
    
    

