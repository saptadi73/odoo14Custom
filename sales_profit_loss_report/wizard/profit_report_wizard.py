# -*- coding: utf-8 -*-
import datetime
from odoo import models, fields, api

class ProductProfitReport(models.TransientModel):
    _name = "sales_profit_report.report"
    _description = 'Product Profit Report'

    @api.model
    def _get_from_date(self):
        company = self.env.user.company_id
        current_date = datetime.date.today()
        from_date = company.compute_fiscalyear_dates(current_date)['date_from']
        return from_date

    from_date = fields.Date(string='Start Date', default=_get_from_date, required=True)
    to_date = fields.Date(string='End Date', default=fields.Date.context_today, required=True)
    company = fields.Many2one('res.company', string='Company', required=True,
                              default=lambda self: self.env.user.company_id.id)

    def print_pnl_pdf_report(self):
        data = {}
        data['form'] = {}
        data['form'].update(self.read([])[0])
        return self.env.ref('sales_profit_loss_report.report_sales_profit_loss_action').with_context(
            landscape=True).report_action(self, data=data)


    def print_pnl_xls_report(self):
        data = {}
        data['form'] = {}
        data['form'].update(self.read([])[0])
        return self.env.ref('sales_profit_loss_report.report_sales_profit_loss_action_xls').report_action(self, data=data, config=False)
