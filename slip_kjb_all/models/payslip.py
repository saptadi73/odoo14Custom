from datetime import date, datetime, time
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _, SUPERUSER_ID
from odoo.exceptions import UserError, ValidationError


class HRAttendance(models.Model):
	_inherit = "hr.attendance"


	lpagi = fields.Float('Liter Pagi', default=0.0, help="Liter Pagi.")
	lpagi_int = fields.Float('Total Pagi', default=0.0)
	lsore = fields.Float('Liter Sore', default=0.0, help="Liter Sore.")
	lsore_int = fields.Float('Total Sore', default=0.0)
	har_sat = fields.Float('Harga Satuan', default=0.0, help="Harga Satuan.")

class Payslip(models.Model):
	_inherit = "hr.payslip"
	

	hari_calendar = fields.Integer('Workday', states={'done': [('readonly', True)]})
	leave = fields.Integer('Total Leave', states={'done': [('readonly', True)]})
	alpha = fields.Integer('Alpha', states={'done': [('readonly', True)]})
	masuk = fields.Integer('Kehadiran', states={'done': [('readonly', True)]})
	pagi = fields.Float('Liter Pagi', default=0.0, states={'done': [('readonly', True)]})
	sore = fields.Float('Liter Sore', default=0.0, states={'done': [('readonly', True)]})
	t_liter = fields.Float('Total Liter', default=0.0, states={'done': [('readonly', True)]})
	h_satuan = fields.Float('Harga Satuan', default=0.0, states={'done': [('readonly', True)]})
	tohar = fields.Float('Total Harga', default=0.0, states={'done': [('readonly', True)]})
	holiday = fields.Integer('Public Holiday', states={'done': [('readonly', True)]})
	divisi_id = fields.Many2one('hr.employee.divisi', string='Divisi', required=False)
	department_id = fields.Many2one('hr.department', string='Department', required=False)

	

	def get_presence(self):

		"""cari jumlah kehadiran employee self.employee_id"""

		sql = """
			select count(*)
			from hr_attendance 
			where employee_id=%s
			and check_in between %s and %s
		"""

		cr = self.env.cr 
		cr.execute(sql, (self.employee_id.id, self.date_from, self.date_to ))
		res = cr.fetchone()

		return res[0]

	def get_lpagi_lsore(self):
		absen = self.env['hr.attendance'].search([('employee_id', '=', self.employee_id.id), ('check_in', '>=', self.date_from),
												 ('check_in', '<=', self.date_to)])
		lpagi_int = 0.00
		lsore_int = 0.00
		har_sat_int = 0.00
		for ab in absen :
			lpagi_int += ab.lpagi
			lsore_int += ab.lsore
			har_sat_int = ab.har_sat

		return {
			'liter_pagi': lpagi_int,
			'liter_sore': lsore_int,
            'total_liter' : lpagi_int + lsore_int,
			'satuan_harga' : har_sat_int,
			'total_harga': har_sat_int * (lpagi_int + lsore_int)

		}
	
	def get_leave(self):
		leave_obj = self.env['hr.leave'].search([('employee_id', '=', self.employee_id.id), ('date_from', '>=', self.date_from),
												 ('date_to', '<=', self.date_to), ('state', '=', 'validate')])

		tot_leave = 0.0
		for x in leave_obj:
			tot_leave += x.number_of_days
			
		return tot_leave


	def get_work_day(self):
		for contract in self.contract_id.filtered(lambda contract: contract.resource_calendar_id):
			day_from = datetime.combine(fields.Date.from_string(self.date_from), time.min)
			day_to = datetime.combine(fields.Date.from_string(self.date_to), time.max)
			workday = contract.employee_id.get_work_days_data(day_from, day_to, calendar=contract.resource_calendar_id)
		return workday
	
		
	@api.onchange('employee_id', 'date_from', 'date_to')
	def onchange_employee(self):
		res = super(Payslip, self).onchange_employee()
		if self.contract_id:
			self.divisi_id = self.employee_id.divisi_id.id
#			self.department_id = self.employee_id.department_id.id
			presence = self.get_presence()
			leave = self.get_leave()
			workday = self.get_work_day()
			info_absen = self.get_lpagi_lsore()
			self.masuk = presence
			self.pagi = info_absen.get('liter_pagi') or 0.0
			self.sore = info_absen.get('liter_sore') or 0.0
			self.t_liter = info_absen.get('total_liter') or 0.0
			self.h_satuan = info_absen.get('satuan_harga') or 0.0
			self.tohar = info_absen.get('total_harga') or 0.0
			self.leave = leave
			self.hari_calendar = workday['days']
			self.alpha = workday['days'] - presence

		return res
	
class HrPayslipLine(models.Model):
	_inherit = 'hr.payslip.line'
	
	divisi_id = fields.Many2one('hr.employee.divisi', string='Divisi', required=True)
#	department_id = fields.Many2one('hr.department', string='Department', required=True)
	date = fields.Date(string='Date', required=True)
	
	@api.model
	def create(self, values):
		if 'employee_id' not in values or 'contract_id' not in values or 'divisi_id' not in values or 'department_id' not in values:
			payslip = self.env['hr.payslip'].browse(values.get('slip_id'))
			values['employee_id'] = values.get('employee_id') or payslip.employee_id.id
			values['divisi_id'] = values.get('divisi_id') or payslip.divisi_id.id
#			values['department_id'] = values.get('department_id') or payslip.department_id.id
			values['date'] = values.get('date') or payslip.date_from
			values['contract_id'] = values.get('contract_id') or payslip.contract_id and payslip.contract_id.id
			if not values['contract_id']:
				raise UserError(_('You must set a contract to create a payslip line.'))
#			if not values['divisi_id']:
#				raise UserError(_('You must set a divisi to create a payslip line.'))
#			if not values['department_id']:
#				raise UserError(_('You must set a department to create a payslip line.'))
		return super(HrPayslipLine, self).create(values)
	
class HrPayrollStructure(models.Model):
	_inherit = 'hr.payroll.structure'
	
	created_payslip = fields.Many2one('res.users', string='Created Payslip By', required=True)
	
class HrSalaryRule(models.Model):
	_inherit = 'hr.salary.rule'
	
	categ_on_payslip = fields.Selection([('pendapatan','Pendapatan'),('potongan','Potongan')],string='Category on Print Out')
	
class HrEmployee(models.Model):
	_inherit = 'hr.employee'
	_description = 'Employee'

	payslip_count = fields.Integer(compute='_compute_payslip_count', string='Payslips', groups="hr_payroll_community.group_hr_payroll_user")

#	@api.multi
	def _compute_payslip_count(self):
		for employee in self:
			slip = self.env['hr.payslip'].search([('employee_id','=',employee.id), ('state','=','finish')])
			employee.payslip_count = len(slip)
			
	
		