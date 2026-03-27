from odoo import api, fields, models, _
from odoo.exceptions import UserError

class PayslipEmployees(models.TransientModel):
    _inherit = 'hr.payslip.employees'

    employee_ids = fields.Many2many('hr.employee', 'hr_employee_group_rel', 'payslip_id', 'employee_id', 'Employees')

    def compute_sheet(self):
        payslips = self.env['hr.payslip']
        [data] = self.read()
        active_id = self.env.context.get('active_id')
        if active_id:
            run_data = self.env['hr.payslip.run'].browse(active_id)
            from_date = run_data.date_start
            to_date = run_data.date_end
            periode_id = run_data.periode_id
            credit_note = run_data.credit_note
        else:
            raise UserError(_("No active payslip run found."))
        if not data['employee_ids']:
            raise UserError(_("You must select employee(s) to generate payslip(s)."))
        for employee in self.env['hr.employee'].browse(data['employee_ids']):
            slip_data = self.env['hr.payslip'].onchange_employee_id(from_date, to_date, employee.id, contract_id=False)
            res = {
                'employee_id': employee.id,
                'name': slip_data['value'].get('name'),
                'struct_id': slip_data['value'].get('struct_id'),
                'contract_id': slip_data['value'].get('contract_id'),
                'payslip_run_id': active_id,
                'input_line_ids': [(0, 0, x) for x in slip_data['value'].get('input_line_ids')],
                'worked_days_line_ids': [(0, 0, x) for x in slip_data['value'].get('worked_days_line_ids')],
                'date_from': from_date,
                'date_to': to_date,
                'credit_note': credit_note,
                'company_id': employee.company_id.id,
                'periode_id': periode_id.id,
            }
            payslip = self.env['hr.payslip'].create(res)
            # Assign periode_id to payslip
            payslip.write({'periode_id': periode_id.id})
            payslips += payslip
        payslips.compute_sheet()
        return {'type': 'ir.actions.act_window_close'}