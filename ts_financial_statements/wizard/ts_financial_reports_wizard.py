
from odoo import api, models, fields, _
from unittest.mock import MagicMock
from odoo.exceptions import UserError


class FinancialReport(models.TransientModel):
    _name = "ts.financial.report.wizard"
    _description = "Financial Statement Report"

    date_from = fields.Date(string='Start Date')
    date_to = fields.Date(string='End Date')
    target_move = fields.Selection([('posted', 'All Posted Entries'),
                                    ('all', 'All Entries'),
                                    ], string='Target Moves', required=True, default='posted')
    comparison_by = fields.Selection([('company', 'By Company'),
                                    ('analytic_account', 'By Analytic Account'),
                                    ], string='Comparison By', required=True, default='company')
    
    account_report_id = fields.Many2one('ts.financial.report', string='Account Report',
        required=True)#, default=_get_default_report_id)
    
    analytic_ids = fields.Many2many('account.analytic.account', string='Analytic Accounts')
    
    journal_ids = fields.Many2many('account.journal', string='Journals',
                                   default=lambda self: self.env['account.journal'].search(
                                       [('company_id', '=', self.company_id.id)]))
    company_id = fields.Many2many('res.company', string='Company', required=True, default=lambda self: self.env.company)
    company_comparison = fields.Boolean('Company Comparison')
    analytic_comparison = fields.Boolean('Analytic Comparison')
    date_invisible = fields.Boolean('Date Invisibility')
    report_type = fields.Selection([('standard', 'Standard'),
                                    ('konsolidasi', 'Konsolidasi Eliminasi'),
                                    ], string='Report Type', required=True, default='standard')
    
    @api.onchange('account_report_id','comparison_by')
    def company_comparision_onchange(self):
        if self.account_report_id:
            if self.comparison_by == 'company':
                self.analytic_comparison = False
                if self.account_report_id.company_comparison:
                    self.company_comparison = True
                else:
                    self.company_comparison = False
                    raise UserError(_("Company Comparison for this report is Not Enabled."))
            elif self.comparison_by == 'analytic_account':
                self.company_comparison = False
                if self.account_report_id.analytic_comparison:
                    self.analytic_comparison = True
                else:
                    self.analytic_comparison = False
                    raise UserError(_("Comparison by Analytic Accounting for this report is Not Enabled."))
            else:
                self.company_comparison = False
                self.analytic_comparison = False
            if self.account_report_id.is_balance_sheet:
                self.date_invisible = True
            else:
                self.date_invisible = False
        else:
            self.company_comparison = False
            self.analytic_comparison = False
            self.date_invisible = False
    
    
    def generate_financial_report(self):
        data = {
            'account_report_id': self.account_report_id.id,
            'date_from': self.date_from,
            'date_to': self.date_to,
            'target_move': self.target_move,
            'analytic_ids': self.analytic_ids,
            'journal_ids': self.journal_ids,
            'company_id': self.company_id,
            'comparison_by': self.comparison_by,
            'report_type' : self.report_type
        }
        data['form'] = self.read(['account_report_id', 'date_from', 'date_to', 'target_move', 'analytic_ids','journal_ids','company_id','report_type'])[0]

        self.env.ref('ts_financial_statements.action_fs_report_xlsx').name = self.account_report_id.name
        return self.env.ref('ts_financial_statements.action_fs_report_xlsx').report_action(self, data=data)
