# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
#from datetime import datetime, date
from datetime import datetime, timedelta
from odoo.exceptions import UserError

class medical_appointment(models.Model):
	_name = "medical.appointment"
	_inherit = 'mail.thread'

	name = fields.Char(string="Appointment ID", readonly=True ,copy=True)
	is_invoiced = fields.Boolean(copy=False,default = False)
	institution_partner_id = fields.Many2one('res.partner',domain=[('is_institution','=',True)],string="Health Center")
	inpatient_registration_id = fields.Many2one('medical.inpatient.registration',string="Inpatient Registration")
	patient_status = fields.Selection([
			('ambulatory', 'Ambulatory'),
			('outpatient', 'Outpatient'),
			('inpatient', 'Inpatient'),
		], 'Patient status', sort=False,default='outpatient')
	# patient_id = fields.Many2one('medical.patient','Patient',required=True)
	patient_id = fields.Many2one('sapi','Sapi',required=False)
	urgency_level = fields.Selection([
			('a', 'Normal'),
			('b', 'Urgent'),
			('c', 'Medical Emergency'),
		], 'Urgency Level', sort=False,default="b")
	status_layanan = fields.Selection([
		('draft', 'Draft'),
		('open', 'Open'),
		('close', 'Close'),
		('cancel', 'Cancel')
	], 'Status Layanan', default='draft')
	tgl_layanan = fields.Datetime('Tanggal Permohonan',required=True, default = fields.Datetime.now)
	appointment_end = fields.Datetime('Appointment End')
	petugas_id = fields.Many2one('medical.physician', 'Petugas')
	jabatan_id = fields.Many2one('master.jabatan', 'Jabatan', related='petugas_id.jabatan_id')
	peternak_id = fields.Many2one('peternak.sapi', 'Peternak/Pemilik')
	wilayah_id = fields.Many2one('master.wilayah', 'Wilayah')
	kode_peternak = fields.Char('Kode Peternak', related='peternak_id.kode_peternak')
	layanan_id = fields.Many2one('jenis.pelayanan', 'Jenis Layanan')
	# petugas_id = fields.Many2one('medical.physician','Physician',required=True)
	no_invoice = fields.Boolean(string='Invoice exempt',default=True)
	validity_status = fields.Selection([
			('invoice', 'Invoice'),
			('tobe', 'To be Invoiced'),
		], 'Status', sort=False,readonly=True,default='tobe')
	appointment_validity_date = fields.Datetime('Validity Date')
	consultations_id = fields.Many2one('product.product','Consultation Service')
	comments = fields.Text(string="Info")
	state = fields.Selection([('draft','Draft'),('confirmed','Confirm'),('cancel','Cancel'),('done','Done')],string="State",default='draft')
	invoice_to_insurer = fields.Boolean('Invoice to Insurance')
	medical_patient_psc_ids = fields.Many2many('medical.patient.psc',string='Pediatrics Symptoms Checklist')
	medical_prescription_order_ids = fields.One2many('medical.prescription.order','appointment_id',string='Prescription')
	insurer_id = fields.Many2one('medical.insurance','Insurer')
	duration = fields.Integer('Duration')
	appointment_line = fields.One2many('medical.appointment.line', 'appointment_id', 'Appointment Lines')
	medicine_id = fields.Many2one('product.template', 'Product Template')
	medicament_appointment_count = fields.Integer(compute='compute_medicament_appointment_count')
	jns_layanan_ids = fields.Many2many('jenis.pelayanan', string='Jenis Layanan')
	jenis_layanan = fields.Selection([('1','PKB'),('2','Pengobatan'),('3','Mutasi'),('4','Ganti ID Sapi'),
									  ('5','IB'),('6','Sapi Masuk'),('7','Melahirkan'),('8','Ganti Pemilik'),
									  ('10','Vaksinasi'),('11','Abortus'),('12','Specimen'),('13','Kering Kandang'),
									  ('14','Potong kuku'),('15','Potong Tanduk'),('16','NKT/Ukur BB TB'),('17','Palpasi Rektal'),
									  ('18','Sampel Kuartir'),('20','Identifikasi')],string="Jenis Layanan")
	pkb_id = fields.Many2one('form.pkb','PKB')
	pengobatan_id = fields.Many2one('form.pengobatan','Pengobatan')
	mutasi_id = fields.Many2one('form.mutasi','Mutasi')
	ganti_sapi_id = fields.Many2one('form.gis','Ganti ID Sapi')
	ib_id = fields.Many2one('form.ib','IB')
	sapi_masuk_id = fields.Many2one('form.masuk','Sapi Masuk')
	melahirkan_id = fields.Many2one('form.melahirkan','Melahirkan')
	ganti_pemilik_id = fields.Many2one('form.ganti.pmlk','Ganti Pemilik')
	vaksin_id = fields.Many2one('form.vaksinasi','Vaksinasi')
	abortus_id = fields.Many2one('form.abortus','Abortus')
	specimen_id = fields.Many2one('form.specimen','Specimen')
	kering_kandang_id = fields.Many2one('form.kk','Kering Kandang')
	potong_id = fields.Many2one('form.pot.kuku','Potong kuku')
	potong_tanduk_id = fields.Many2one('form.pt','Potong Tanduk')
	nkt_id = fields.Many2one('form.nkt','NKT/Ukur BB TB')
	palpasi_id = fields.Many2one('form.pr','Palpasi Rektal')
	sampel_id = fields.Many2one('form.sq','Sampel Kuartir')
	identifikasi_id = fields.Many2one('form.ident','Identifikasi')


	def get_medicament_appointment(self):
		action = self.env.ref('basic_hms.'
							  'action_medical_prescription_order').read()[0]
		action['domain'] = [('patient_id', 'in', self.ids)]
		return action

	def compute_medicament_appointment_count(self):
		for record in self:
			record.medicament_appointment_count = self.env['medical.prescription.order'].search_count(
				[('patient_id', 'in', self.ids)])

	# @api.onchange('product_id')
	# def onchange_product_id(self):
	# 	for rec in self:
	# 		lines = [(5, 0, 0)]
	# 		for line in self.product_id.product_variant_ids:
	# 			val = {
	# 				'product_id': line.id,
	# 				'qty': 5
	# 			}
	# 			lines.append((0, 0, val))
	# 			rec.appointment_line = lines

	def func_open(self):
		if self.status_layanan == 'draft':
			self.status_layanan = 'open'

	def func_close(self):
		if self.status_layanan == 'open':
			self.status_layanan = 'close'

	def func_cancel(self):
		if self.status_layanan == 'open':
			self.status_layanan = 'cancel'

	# @api.onchange('patient_id')
	# def onchange_name(self):
	# 	ins_obj = self.env['medical.insurance']
	# 	ins_record = ins_obj.search([('medical_insurance_partner_id', '=', self.patient_id.patient_id.id)])
	# 	if len(ins_record)>=1:
	# 		self.insurer_id = ins_record[0].id
	# 	else:
	# 		self.insurer_id = False

	@api.model
	def create(self, vals):
		vals['name'] = self.env['ir.sequence'].next_by_code('medical.appointment') or 'APT'
		msg_body = 'Appointment created'
		for msg in self:
			msg.message_post(body=msg_body)
		result = super(medical_appointment, self).create(vals)
		return result

	@api.onchange('inpatient_registration_id')
	def onchange_patient(self):
		if not self.inpatient_registration_id:
			self.patient_id = ""
		inpatient_obj = self.env['medical.inpatient.registration'].browse(self.inpatient_registration_id.id)
		self.patient_id = inpatient_obj.id

	def confirm(self):
		self.write({'state': 'confirmed'})

	def done(self):
		self.write({'state': 'done'})

	def cancel(self):
		self.write({'state': 'cancel'})

	def print_prescription(self):
		return self.env.ref('basic_hms.report_print_prescription').report_action(self)


	def view_patient_invoice(self):
		self.write({'state': 'cancel'})

	def create_invoice(self):
		lab_req_obj = self.env['medical.appointment']
		account_invoice_obj  = self.env['account.invoice']
		account_invoice_line_obj = self.env['account.invoice.line']

		lab_req = lab_req_obj
		if lab_req.is_invoiced == True:
			raise UserError(_(' Invoice is Already Exist'))
		if lab_req.no_invoice == False:
			res = account_invoice_obj.create({'partner_id': lab_req.patient_id.patient_id.id,
												   'date_invoice': date.today(),
											 'account_id':lab_req.patient_id.patient_id.property_account_receivable_id.id,
											 })

			res1 = account_invoice_line_obj.create({'product_id':lab_req.consultations_id.id ,
											 'product_uom': lab_req.consultations_id.uom_id.id,
											 'name': lab_req.consultations_id.name,
											 'product_uom_qty':1,
											 'price_unit':lab_req.consultations_id.lst_price,
											 'account_id': lab_req.patient_id.patient_id.property_account_receivable_id.id,
											 'invoice_id': res.id})

			if res:
				lab_req.write({'is_invoiced': True})
				imd = self.env['ir.model.data']
				action = imd.xmlid_to_object('account.action_invoice_tree1')
				list_view_id = imd.xmlid_to_res_id('account.view_order_form')
				result = {
								'name': action.name,
								'help': action.help,
								'type': action.type,
								'views': [ [list_view_id,'form' ]],
								'target': action.target,
								'context': action.context,
								'res_model': action.res_model,
								'res_id':res.id,
							}
				if res:
					result['domain'] = "[('id','=',%s)]" % res.id
		else:
			 raise UserError(_(' The Appointment is invoice exempt'))
		return result

	def create_prescription(self):
		res_ids = []
		for browse_record in self:
			result = {}
			medical_prescription_obj = self.env['medical.prescription.order']
			res = medical_prescription_obj.create({
				'name': self.env['ir.sequence'].next_by_code('medical.prescription.order'),
				'patient_id': browse_record.patient_id.id,
				'prescription_date': browse_record.appointment_date or False,
				'invoice_to_insurer': browse_record.invoice_to_insurer or False,
				'doctor_id': browse_record.doctor_id.id or False,
			})
			res_ids.append(res.id)
			if res_ids:
				imd = self.env['ir.model.data']
				action = imd.xmlid_to_object('basic_hms.action_medical_prescription_order')
				list_view_id = imd.xmlid_to_res_id('basic_hms.medical_prescription_order_tree_view')
				form_view_id = imd.xmlid_to_res_id('basic_hms.medical_prescription_order_form_view')
				result = {
					'name': action.name,
					'help': action.help,
					'type': action.type,
					'views': [[list_view_id, 'tree'], [form_view_id, 'form']],
					'target': action.target,
					'context': action.context,
					'res_model': action.res_model,
					'res_id': res.id,

				}

			if res_ids:
				result['domain'] = "[('id','=',%s)]" % res_ids

		return result
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:



class medical_appointment_line(models.Model):
	_name = "medical.appointment.line"
	_description = "Appointment Lines"

	product_id = fields.Many2one('product.product', string='Medicine')
	qty = fields.Integer(string="Quantity")
	appointment_id = fields.Many2one('medical.appointment', 'Appointment ID')
