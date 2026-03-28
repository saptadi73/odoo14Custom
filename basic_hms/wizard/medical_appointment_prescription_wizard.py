# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from datetime import date, datetime


# classes under  menus of laboratry

class medical_appointment_prescription_create(models.TransientModel):
    _name = 'medical.appointment.prescription.create'

    def create_prescription_appointment(self):
        res_ids = []
        lab_rqu_obj = self.env['medical.appointment']
        browse_records = lab_rqu_obj.browse(self._context.get('active_ids'))
        result = {}
        for browse_record in browse_records:
            medical_lab_obj = self.env['medical.prescription.order']
            res = medical_lab_obj.create({'name': self.env['ir.sequence'].next_by_code('medical.prescription.order'),
                                            'patient_id': browse_record.patient_id.id,
                                            'prescription_date': browse_record.appointment_date or False,
                                            'invoice_to_insurer': browse_record.invoice_to_insurer or False,
                                            'petugas_id': browse_record.petugas_id.id or False,
                                            'medicine_id': browse_record.medicine_id.id or False
                                          })
            res_ids.append(res.id)
            if res_ids:
                imd = self.env['ir.model.data']
                # write_ids = lab_rqu_obj.browse(self._context.get('active_id'))
                # write_ids.write({'state': 'tested'})
                action = imd.sudo().xmlid_to_object('basic_hms.action_medical_prescription_order')
                list_view_id = imd.sudo().xmlid_to_res_id('basic_hms.medical_prescription_order_tree_view')
                form_view_id = imd.sudo().xmlid_to_res_id('basic_hms.medical_prescription_order_form_view')
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
