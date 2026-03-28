# -*- coding: utf-8 -*-

from odoo import models

class AccountReporsXLS(models.AbstractModel):
    _name = 'report.sales_profit_loss_report.report_sales_profit_report_xls'
    _description = 'Analytic Account Record Xls'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):
        # currency = False
        format1 = workbook.add_format({'font_size': 12, 'align': 'vcenter', 'bold': True})
        format1.set_font_color('white')
        format1.set_bg_color('black')
        format2 = workbook.add_format({'font_size': 10, 'align': 'vcenter', })
        format3 = workbook.add_format({'font_size': 10, 'align': 'vcenter', 'font_color': 'green'})
        format4 = workbook.add_format({'font_size': 10, 'align': 'vcenter', 'font_color': 'red'})
        sheet = workbook.add_worksheet(str('testing'))
        merge_format = workbook.add_format({
                                'font_size': 14,
                                'bold': 1,
                                'align': 'center',
                                'valign': 'vcenter'})
        bold = workbook.add_format({'bold': True,'font_size': 14,})
        sheet.merge_range('A1:J4', '', merge_format)
        sheet.write_rich_string(0,0, bold,'Sales Profit & Loss Report', bold,' | Date From : ',data['form']['from_date'],bold,' Date To : ',data['form']['to_date'],merge_format)
        object_head_data = self.env['report.sales_profit_loss_report.report_sales_profit_report'].generate_report_values(data['form'])
        for i in range(0,11):
            if i in [0,1]:
                width = 30
            else:
                width = 18
            sheet.set_column(i, i, width)
        sheet.write(6, 0, 'Product Name', format1)
        sheet.write(6, 1, 'Product Category', format1)
        sheet.write(6, 2, 'Quantity', format1)
        sheet.write(6, 3, 'Unit', format1)
        sheet.write(6, 4, 'Unit Price', format1)
        sheet.write(6, 5, 'Taxes', format1)
        sheet.write(6, 6, 'Amount w/o Tax', format1)
        sheet.write(6, 7, 'Cost Price', format1)
        sheet.write(6, 8, 'Gross Profit/Loss', format1)
        if object_head_data:
            amt_wo_tax = cost_price = gross_pnl = 0
            main_ct = 7
            for obj_data in object_head_data:
                if obj_data == 'product_dict':
                    count = 7
                    row_count = 0
                    for rec in object_head_data[obj_data]:
                        new_val = self.env['sale.order'].check_report_vals(object_head_data[obj_data][rec])
                        for new in new_val:
                            sheet.write(count, row_count, str(rec.name), format2)
                            sheet.write(count, row_count+1, str(new_val[new]['category'].name), format2)
                            sheet.write(count, row_count+2, str(new_val[new]['qty']), format2)
                            sheet.write(count, row_count+3, str(new_val[new]['uom'].name), format2)
                            sheet.write(count, row_count+4, str(new_val[new]['unit_price']) +' '+ self.env.company.currency_id.symbol, format2)
                            sheet.write(count, row_count+5, str(new_val[new]['taxes']) +' '+ self.env.company.currency_id.symbol, format2)
                            sheet.write(count, row_count+6, str(new_val[new]['amt_wo_tax']) +' '+ self.env.company.currency_id.symbol, format2)
                            sheet.write(count, row_count+7, str(round(new_val[new]['cost_price'], 2)) +' '+ self.env.company.currency_id.symbol, format2)
                            sheet.write(count, row_count+8, str(round(new_val[new]['gross_pnl'], 2)) +' '+ self.env.company.currency_id.symbol, format3 if new_val[new]['gross_pnl'] > 0 else format4)
                            count += 1
                            amt_wo_tax = amt_wo_tax + new_val[new]['amt_wo_tax']
                            cost_price = cost_price + new_val[new]['cost_price']
                            gross_pnl = gross_pnl + new_val[new]['gross_pnl']
                            main_ct += 1
            sheet.write(main_ct, 6, str(round(amt_wo_tax, 2)) +' '+ self.env.company.currency_id.symbol, format1)
            sheet.write(main_ct, 7, str(round(cost_price, 2)) +' '+ self.env.company.currency_id.symbol, format1)
            sheet.write(main_ct, 8, str(round(gross_pnl, 2)) +' '+ self.env.company.currency_id.symbol, format1)
