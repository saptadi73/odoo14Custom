from odoo import api, fields, models

class master_kematian(models.Model):
	_name = "kematian"

	patient_id = fields.Many2one('medical.patient', string="Nama")
	sex = fields.Selection([('m', 'Male'), ('f', 'Female')], string="Sex")
	age = fields.Char(string="Age", related="patient_id.age")
	no_rm = fields.Char('No. RM')
	start_date = fields.Datetime('Sejak Tanggal')
	on_date = fields.Datetime('Pada Tanggal')
	active = fields.Boolean(default="True")
	photo = fields.Binary(string="Picture")

	@api.onchange('patient_id')
	def onchange_patient_id(self):
		if self.patient_id:
			if self.patient_id.sex:
				self.sex = self.patient_id.sex
		else:
			self.sex = ''