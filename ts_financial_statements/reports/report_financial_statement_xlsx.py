
from odoo import models, fields, api
from datetime import datetime
from calendar import monthrange
import calendar
from xlsxwriter.utility import xl_range
from ftplib import FTP

class TsFinancialReportXlsx(models.AbstractModel):
    _name = 'report.ts_financial_statements.profit_and_loss_report'
    _inherit = 'report.report_xlsx.abstract'
    
    def _prepare_domain_data(self, data, accounts, moves, record_id=False):
        domain = []
        if accounts:
            domain.append(('account_id','in',accounts.ids))
        if moves:
            domain.append(('move_id.state','in',moves))
        if data.get('date_from', False):
            domain.append(('date', '>=', data.get('date_from')))
        if data.get('date_to', False):
            domain.append(('date', '<=', data.get('date_to')))
        
        if data.get('comparison_by', False) == 'company':
            domain.append(('company_id','=',record_id.id))
        else:
            domain.append(('analytic_account_id', '=', record_id.id))
            domain.append(('company_id', '=', self.env.company.id))
        # print("company and  loop id ~~~~~~~~~~~~~~~ ",self.env.company,record_id,domain)
        # print("******************",data.get('date_from', False), data.get('date_to', False))
        return domain
        
        
    def prepare_report_contents(self, workbook, report_id, moves, data, analytic_ids=False):
        # parent_id = self.env['ts.financial.report'].search([('id', '=', report_id)])
        report_lines = self.env['ts.financial.report.line'].search([('parent_id', '=', report_id)])
        print("Report Lines++++++++++++++++++++",report_lines)
        form = data['form']
        # date_from = form['date_from']
        # date_to = form['date_to']
        company_ids = form['company_id']
        analytic_ids = form['analytic_ids']
        
        if data.get('comparison_by', False) == 'company':
            companies = self.env['res.company'].search([('id','in',company_ids)])
            data_result = companies
        else:
            analytic_accounts = self.env['account.analytic.account'].search([('id','in',analytic_ids)])
            data_result = analytic_accounts
        print("form data ---------------------",data_result)

        result = []
        
        for report in report_lines:
            report_dict = {'particular':'', 'total_balance':'','view_layout':'','data_layout':'','data_dict':''}
            layout = ''
            if report.style_overwrite == '1':
                money = workbook.add_format({'num_format': '_(* #,##0.00_);_(* (#,##0.00);_(* "-"??_);_(@_)', 'border': 0})
                heading1 = workbook.add_format({'bold': False, 'valign': 'vcenter', 'border': 0, 'font_size': 11})
                heading1.set_indent(1)
                layout = money
                report_dict['view_layout'] = heading1
            if report.style_overwrite == '2':
                money_bold = workbook.add_format({'num_format': '_(* #,##0.00_);_(* (#,##0.00);_(* "-"??_);_(@_)', 'bold': True, 'fg_color': '#2e75b6', 'border': 1})
                money_bold.set_font_color('white')
                layout = money_bold
                heading2 = workbook.add_format({'bold': True, 'valign': 'vcenter', 'border': 0, 'font_size': 11})
                report_dict['view_layout'] = heading2
            if report.style_overwrite == '3':
                money_head1 = workbook.add_format({'num_format': '_(* #,##0.00_);_(* (#,##0.00);_(* "-"??_);_(@_)', 'bold': True, 'border': 0})
                heading3 = workbook.add_format({'bold': True, 'valign': 'vcenter', 'border': 0, 'font_size': 11})
                layout = money_head1
                report_dict['view_layout'] = heading3
            if report.style_overwrite == '4':
                money_format3 = workbook.add_format({'num_format': '_(* #,##0.00_);_(* (#,##0.00);_(* "-"??_);_(@_)', 'bold': True, 'fg_color': '#2e75b6', 'border': 1})
                money_format3.set_font_color('white')
                money_format3.set_top(2)
                layout = money_format3
            if report.style_overwrite == '5':
                footer_money_bold = workbook.add_format({'num_format': '_(* #,##0.00_);_(* (#,##0.00);_(* "-"??_);_(@_)', 'bold': True, 'fg_color': '#2e75b6', 'border': 1})
                footer_money_bold.set_font_color('white')
                footer_money_bold.set_bottom(2)
                layout = footer_money_bold
            if report.style_overwrite == '6':
                if report.enable_percent_sign:
                    ratio_layout = workbook.add_format({'num_format': '0.00%', 'align': 'right', 'border': 0})
                else:
                    ratio_layout = workbook.add_format({'num_format': '0.000', 'align': 'right', 'border': 0})
                layout = ratio_layout
            
            report_dict['particular'] = report.name
            report_dict['data_layout'] = layout
            
            result2 = []
            for f in data_result:
                data_dict = {'name':'', 'total_balance':'','debit':'','credit':''}
                total_balance = total_debit = total_credit = 0
                nom_balance = nom_debit = nom_credit = 0
                den_balance = den_debit = den_credit = 0
                # bbf_balance = bbf_debit = bbf_credit = 0
                # ftp_balance = ftp_debit = ftp_credit = 0
                if report.type == 'accounts':
                    # it's the sum of the linked accounts
                    if report.style_overwrite == '6':
                        num_accounts = report.numerator_account_ids
                        den_accounts = report.denominator_account_ids
                        domain1 = self._prepare_domain_data(data,num_accounts,moves,f)
                        num_acc_moves = self.env['account.move.line'].search(domain1)
                        for mv in num_acc_moves:
                            nom_debit += mv.debit 
                            nom_credit += mv.credit
                            nom_balance = nom_debit - nom_credit
                        domain2 = self._prepare_domain_data(data,den_accounts,moves,f)
                        den_acc_moves = self.env['account.move.line'].search(domain2)
                        for mv in den_acc_moves:
                            den_debit += mv.debit 
                            den_credit += mv.credit
                            den_balance = den_debit - den_credit
                        if den_balance != 0:
                            data_dict['total_balance'] = nom_balance/den_balance
                            print ("================debit 111=====", den_credit,nom_credit)
                        else:
                            data_dict['total_balance'] = '#DIV/0!'
                    else:    
                        accounts = report.account_ids
                        domain = self._prepare_domain_data(data,accounts,moves,f)
                        move_recs = self.env['account.move.line'].search(domain)
                        for mv in move_recs:
                            total_debit += mv.debit 
                            total_credit += mv.credit
                            total_balance = total_debit - total_credit
                            print ("================debit 222=====", total_debit,total_credit)
                        if report.reverse_balance_sign:
                            data_dict['total_balance'] = total_balance*-1
                        else:
                            data_dict['total_balance'] = total_balance
                    data_dict['name'] = f.name
                    result2.append(data_dict)
                if report.type == 'account_type':
                    if report.style_overwrite == '6':
                        num_accounts = self.env['account.account'].search([('user_type_id','in',report.numerator_acc_type_ids.ids)])
                        den_accounts = self.env['account.account'].search([('user_type_id','in',report.denominator_acc_type_ids.ids)])
                        domain1 = self._prepare_domain_data(data,num_accounts,moves,f)
                        num_acc_moves = self.env['account.move.line'].search(domain1)
                        for mv in num_acc_moves:
                            nom_debit += mv.debit 
                            nom_credit += mv.credit
                            nom_balance = nom_debit - nom_credit
                        domain2 = self._prepare_domain_data(data,den_accounts,moves,f)
                        den_acc_moves = self.env['account.move.line'].search(domain2)
                        for mv in den_acc_moves:
                            den_debit += mv.debit 
                            den_credit += mv.credit
                            den_balance = den_debit - den_credit
                        if den_balance != 0:
                            data_dict['total_balance'] = nom_balance/den_balance
                            print ("================debit 3333=====", den_credit,nom_credit)
                        else:
                            data_dict['total_balance'] = '#DIV/0!'
                    else:
                        # if parent_id.is_balance_sheet:
                        #     babf_acc_list = []
                        #     ftp_acc_list = []
                        #     for type in report.account_type_ids:
                        #         if type.include_initial_balance:
                        #             babf_acc_list.append(type.id)
                        #         else:
                        #             ftp_acc_list.append(type.id)
                        #     bbf_accounts = self.env['account.account'].search([('user_type_id','in',babf_acc_list)])
                        #     ftp_accounts = self.env['account.account'].search([('user_type_id','in',ftp_acc_list)])
                        #     domain1 = self._prepare_domain_data(data,bbf_accounts,moves,f,False,date_to)
                        #     bbf_acc_moves = self.env['account.move.line'].search(domain1)
                        #     for mv in bbf_acc_moves:
                        #         bbf_debit += mv.debit 
                        #         bbf_credit += mv.credit
                        #         bbf_balance = bbf_debit - bbf_credit
                        #     domain2 = self._prepare_domain_data(data,ftp_accounts,moves,f,date_from,date_to)
                        #     ftp_acc_moves = self.env['account.move.line'].search(domain2)
                        #     for mv in ftp_acc_moves:
                        #         ftp_debit += mv.debit 
                        #         ftp_credit += mv.credit
                        #         ftp_balance = ftp_debit - ftp_credit
                        #     data_dict['total_balance'] = bbf_balance+ftp_balance
                        # else:
                        accounts = self.env['account.account'].search([('user_type_id','in',report.account_type_ids.ids)])
                        domain = self._prepare_domain_data(data,accounts,moves,f)
                        move_recs = self.env['account.move.line'].search(domain)
                        for mv in move_recs:
                            total_debit += mv.debit 
                            total_credit += mv.credit
                            total_balance = total_debit - total_credit
                            print ("================debit 44444=====", total_debit,total_credit)
                        if report.reverse_balance_sign:
                            data_dict['total_balance'] = total_balance*-1
                        else:
                            data_dict['total_balance'] = total_balance
                    data_dict['debit'] = total_debit
                    data_dict['credit'] = total_credit
                    data_dict['name'] = f.name
                    result2.append(data_dict)
                if report.type == 'account_group':
                    if report.style_overwrite == '6':
                        num_accounts = self.env['account.account'].search([('group_id','in',report.numerator_acc_group_ids.ids)])
                        den_accounts = self.env['account.account'].search([('group_id','in',report.denominator_acc_group_ids.ids)])
                        domain1 = self._prepare_domain_data(data,num_accounts,moves,f)
                        num_acc_moves = self.env['account.move.line'].search(domain1)
                        for mv in num_acc_moves:
                            nom_debit += mv.debit 
                            nom_credit += mv.credit
                            nom_balance = nom_debit - nom_credit
                        domain2 = self._prepare_domain_data(data,den_accounts,moves,f)
                        den_acc_moves = self.env['account.move.line'].search(domain2)
                        for mv in den_acc_moves:
                            den_debit += mv.debit 
                            den_credit += mv.credit
                            den_balance = den_debit - den_credit
                        if den_balance != 0:
                            data_dict['total_balance'] = nom_balance/den_balance
                            print ("================debit 55555=====", den_credit,nom_credit)
                        else:
                            data_dict['total_balance'] = '#DIV/0!'
                    else:
                        accounts = self.env['account.account'].search([('group_id','in',report.account_group_ids.ids)])
                        domain = self._prepare_domain_data(data,accounts,moves,f)
                        move_recs = self.env['account.move.line'].search(domain)
                        for mv in move_recs:
                            total_debit += mv.debit 
                            total_credit += mv.credit
                            total_balance = total_debit - total_credit
                            print ("================debit 666666=====", total_debit,total_credit)
                        if report.reverse_balance_sign:
                            data_dict['total_balance'] = total_balance*-1
                        else:
                            data_dict['total_balance'] = total_balance
                    data_dict['name'] = f.name
                    result2.append(data_dict)
                if report.type == 'report_value':
                    data_return = self.get_report_vals_from_lines(data,report,moves,f)
                    data_dict['total_balance'] = data_return
                    data_dict['name'] = f.name
                    result2.append(data_dict)
                report_dict['data_dict'] = result2
                if report.type == 'sum':
                    empty_heading = workbook.add_format({'bold': True, 'valign': 'vcenter', 'border': 0, 'font_size': 11})
                    report_dict['particular'] = report.name
                    report_dict['total_balance'] = ''
                    report_dict['view_layout'] = empty_heading

            result.append(report_dict)
        print("List vals are ++++++++++ ",result)
        return result
        
    
    def get_report_vals_from_lines(self,data,report,moves,f):
        report_lines = report.report_line_ids
        if report_lines:
            print("Report Lnes are ------------ >>> ",report_lines)
            sum_total_balance = 0
            for line in report_lines:
                total_balance = total_debit = total_credit = 0
                if line.type == 'accounts':
                    accounts = line.account_ids
                    domain = self._prepare_domain_data(data,accounts,moves,f)
                    move_recs = self.env['account.move.line'].search(domain)
                    for mv in move_recs:
                        total_debit += mv.debit 
                        total_credit += mv.credit
                        total_balance = total_debit - total_credit
                        print ("================debit 777777=====", total_debit,total_credit)
                if line.type == 'account_type':
                    accounts = self.env['account.account'].search([('user_type_id','in',line.account_type_ids.ids)])
                    domain = self._prepare_domain_data(data,accounts,moves,f)
                    move_recs = self.env['account.move.line'].search(domain)
                    for mv in move_recs:
                        total_debit += mv.debit 
                        total_credit += mv.credit
                        total_balance = total_debit - total_credit
                        print ("================debit 888888=====", total_debit,total_credit)
                if line.type == 'account_group':
                    accounts = self.env['account.account'].search([('group_id','in',line.account_group_ids.ids)])
                    domain = self._prepare_domain_data(data,accounts,moves,f)
                    move_recs = self.env['account.move.line'].search(domain)
                    for mv in move_recs:
                        total_debit += mv.debit 
                        total_credit += mv.credit
                        total_balance = total_debit - total_credit
                        print ("================debit 99999=====", total_debit,total_credit)
                if line.reverse_balance_sign:
                    sum_total_balance += total_balance*-1
                else:
                    sum_total_balance += total_balance
            return sum_total_balance
        
    
    def generate_xlsx_report(self, workbook, data, records):
        form = data['form']
        date_to = form['date_to']
        target_move = form['target_move']
        journal_ids = form['journal_ids']
        analytic_ids = form['analytic_ids']
        company_ids = form['company_id']
        type_report = form['report_type']
        if target_move == 'posted':
            moves = ['posted']
        else:
            moves = ['draft','posted']
            
        company_id = self.env['res.company'].search([('id', '=', self.env.company.id)])
        print ("===============type reporttttt============", type_report)
        
        company_format = workbook.add_format({'bold': 1, 'border': 0, 'valign': 'vcenter', 'fg_color': '#1f4e79', 'font_size': 16})
        title_format = workbook.add_format({'bold': 1, 'border': 0, 'valign': 'vcenter', 'fg_color': '#2e75b6', 'font_size': 11})
        date_row_format = workbook.add_format({'bold': 1, 'border': 1, 'align': 'center', 'valign': 'vcenter', 'fg_color': '#2e75b6', 'font_size': 11})
        table_top_merged = workbook.add_format({'bold': 1, 'border': 1, 'align': 'center', 'valign': 'vcenter', 'fg_color': '#1f4e79', 'font_size': 11})
        company_format.set_font_color('white')
        title_format.set_font_color('white')
        date_row_format.set_text_wrap()
        date_row_format.set_font_color('white')
        table_top_merged.set_font_color('white')
        money_total = workbook.add_format({'num_format': '_(* #,##0.00_);_(* (#,##0.00);_(* "-"??_);_(@_)', 'bold': True, 'fg_color': '#2e75b6', 'border': 0})
        money_total.set_font_color('white')
        
        if data.get('account_report_id', False):
            report_id = data.get('account_report_id', False)
        result = self.prepare_report_contents(workbook,report_id,moves,data,analytic_ids)
        
        report = self.env['ts.financial.report'].search([('id','=',report_id)])
        sheet = workbook.add_worksheet(report.name)
        
        layout1 = workbook.add_format({'border': 0})
        ratio_bold = workbook.add_format({'num_format': '0.00%', 'border': 0, 'fg_color': '#2e75b6'})
        
        sheet.set_row(0, 26)
        sheet.set_row(1, 20)
        sheet.set_row(2, 20)
        sheet.set_column('A:A', 40)
        sheet.set_column('B:Z', 15)
        
        row = 4
        col = 1
        row += 2
        if type_report == 'standard' :
            for data in result:
                print ("===================data==================", data)
                sheet.write(row, 0, data['particular'] ,data['view_layout'])
                col = 1
                for f in data['data_dict']:
                    sheet.write(5, col, f['name'], date_row_format)
                    sheet.write(row, col, f['total_balance'] ,data['data_layout'])
                    col += 1
                cell_range = xl_range(row, 1, row, col-1)
                row = row +1
                if not data['data_dict'] == []:
                    sheet.write_formula(row-1, col, f'=SUM({cell_range})',money_total)
            
            sheet.merge_range(0,0,0,col, company_id.name, company_format)
            sheet.merge_range(1,0,1,col, report.name, title_format)
            sheet.merge_range(2,0,2,col, str(report.desc_before_date) +' '+ str(date_to) , title_format)
            sheet.merge_range(4,1,4, col, 'AMOUNT IN PKR', table_top_merged)
            sheet.write(5, col, 'Total', date_row_format)
        else :
            row = 5
            col = 1
            row += 2
            for data in result:
                print ("===================data==================", data)
                sheet.write(row, 0, data['particular'] ,data['view_layout'])
                tot = 0
                debit = 0
                credit = 0
                total = 0
                for f in data['data_dict']:
                    company = self.env['res.company'].search([('name', '=', f['name'])], limit=1)
                    print ("==========comany========", company.is_konsolidasi)
                    if company.is_konsolidasi != True :
                        tot += f['total_balance']
                        sheet.write(row, 1, tot ,data['data_layout'])
                    else :
                        debit += f['debit']
                        credit += f['credit']
                        sheet.write(row, 2, debit ,data['data_layout'])
                        sheet.write(row, 3, credit ,data['data_layout'])

                    total = tot + debit - credit
                    sheet.write(row, 4, total ,data['data_layout'])
            
                row = row +1
            sheet.merge_range(1,0,1,4, 'NERACA ELIMINASI', title_format)
            sheet.merge_range(2,0,2,4, str(date_to) , title_format)
            sheet.merge_range(4, 0,5,0, 'AKTIVA', date_row_format)
            sheet.merge_range(4, 1,5,1,'Konsolidasi', date_row_format)
            sheet.merge_range(4, 2,4,3, 'ELIMINASI', date_row_format)
            sheet.write(5, 2, '+', date_row_format)
            sheet.write(5, 3, '-', date_row_format)
            sheet.merge_range(4,4,5,4, 'Total', date_row_format)


        
