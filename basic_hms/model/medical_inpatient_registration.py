# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from datetime import date,datetime
from odoo.exceptions import UserError

class medical_inpatient_registration(models.Model):
    _name = 'medical.inpatient.registration'

    name = fields.Char(string="Registration Code", copy=False, readonly=True, index=True)
    patient_id = fields.Many2one('medical.patient',string="Patient",required=True)
    hospitalization_date = fields.Datetime(string="Hospitalization date",required=True)
    discharge_date = fields.Datetime(string="Expected Discharge date",required=True)
    attending_physician_id = fields.Many2one('medical.physician',string="Attending Physician")
    operating_physician_id = fields.Many2one('medical.physician',string="Operating Physician")
    admission_type = fields.Selection([('routine','Routine'),('maternity','Maternity'),('elective','Elective'),('urgent','Urgent'),('emergency','Emergency  ')],required=True,string="Admission Type")
    medical_pathology_id = fields.Many2one('medical.pathology',string="Reason for Admission")
    info = fields.Text(string="Extra Info")
    bed_transfers_ids = fields.One2many('bed.transfer','inpatient_id',string='Transfer Bed',readonly=True)
    medical_diet_belief_id = fields.Many2one('medical.diet.belief',string='Belief')
    therapeutic_diets_ids = fields.One2many('medical.inpatient.diet','medical_inpatient_registration_id',string='Therapeutic_diets')
    diet_vegetarian = fields.Selection([('none','None'),('vegetarian','Vegetarian'),('lacto','Lacto Vegetarian'),('lactoovo','Lacto-Ovo-Vegetarian'),('pescetarian','Pescetarian'),('vegan','Vegan')],string="Vegetarian")
    nutrition_notes = fields.Text(string="Nutrition notes / Directions")
    state = fields.Selection([('free','Free'),('confirmed','Confirmed'),('hospitalized','Hospitalized'),('invoice','Create Invoiced'), ('cancel','Cancel'),('done','Done')],string="State",default="free")
    nursing_plan = fields.Text(string="Nursing Plan")
    discharge_plan = fields.Text(string="Discharge Plan")
    icu = fields.Boolean(string="ICU")
    medication_ids = fields.One2many('medical.inpatient.medication','medical_inpatient_registration_id',string='Medication')
    hospitalized_id = fields.Many2one('product.product', 'Hospitalized Service', required=True)
    validity_status = fields.Selection([
        ('invoice', 'Invoice'),
        ('tobe', 'To be Invoiced'),
    ], 'Status', sort=False, readonly=True, default='tobe')
    no_invoice = fields.Boolean(string='Invoice exempt', default=True)
    is_invoiced = fields.Boolean(copy=False, default=False)

    @api.model
    def default_get(self, fields):
        result = super(medical_inpatient_registration, self).default_get(fields)
        patient_id  = self.env['ir.sequence'].next_by_code('medical.inpatient.registration')
        if patient_id:
            result.update({
                        'name':patient_id,
                       })
        return result

    def registration_confirm(self):
        self.write({'state': 'confirmed'})

    def registration_admission(self):
        self.write({'state': 'hospitalized'})

    def registration_cancel(self):
        self.write({'state': 'cancel'})

    def patient_discharge(self):
        self.write({'state': 'done'})

    def create_invoice(self):
        inpatient_req_obj = self.env['medical.inpatient.registration']
        account_invoice_obj = self.env['account.invoice']
        account_invoice_line_obj = self.env['account.invoice.line']

        inpatient_req = inpatient_req_obj
        if inpatient_req.is_invoiced == True:
            raise UserError(_(' Invoice is Already Exist'))
        if inpatient_req.no_invoice == False:
            res = account_invoice_obj.create({'partner_id': inpatient_req.patient_id.patient_id.id,
                                              'date_invoice': date.today(),
                                              'account_id': inpatient_req.patient_id.patient_id.property_account_receivable_id.id,
                                              })

            res1 = account_invoice_line_obj.create({'product_id': inpatient_req.hospitalized_id.id,
                                                    'product_uom': inpatient_req.hospitalized_id.uom_id.id,
                                                    'name': inpatient_req.hospitalized_id.name,
                                                    'product_uom_qty': 1,
                                                    'price_unit': inpatient_req.hospitalized_id.lst_price,
                                                    'account_id': inpatient_req.patient_id.patient_id.property_account_receivable_id.id,
                                                    'invoice_id': res.id})

            if res:
                inpatient_req.write({'is_invoiced': True})
                imd = self.env['ir.model.data']
                action = imd.xmlid_to_object('account.action_invoice_tree1')
                list_view_id = imd.xmlid_to_res_id('account.view_order_form')
                result = {
                    'name': action.name,
                    'help': action.help,
                    'type': action.type,
                    'views': [[list_view_id, 'form']],
                    'target': action.target,
                    'context': action.context,
                    'res_model': action.res_model,
                    'res_id': res.id,
                }
                if res:
                    result['domain'] = "[('id','=',%s)]" % res.id
        else:
            raise UserError(_(' The Appointment is invoice exempt'))
        return result

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:s
