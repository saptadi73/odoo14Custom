# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from datetime import date,datetime
# classes under  menus of laboratry

class medical_lab(models.Model):

    _name = 'medical.lab'

    name = fields.Char('ID')
    test_id = fields.Many2one('medical.test_type', 'Test Type', required = True)
    date_analysis =  fields.Datetime('Date of the Analysis' , default = datetime.now())
    patient_id = fields.Many2one('medical.patient','Patient', required = True) 
    date_requested = fields.Datetime('Date requested',  default = datetime.now())
    medical_lab_physician_id = fields.Many2one('medical.physician','Pathologist')
    requestor_physician_id = fields.Many2one('medical.physician','Physician', required = True)
    critearea_ids = fields.One2many('medical_test.critearea','medical_lab_id', 'Critearea')
    results= fields.Text('Keterangan Klinis')
    diagnosis = fields.Text('Diagnosis')
    is_invoiced = fields.Boolean(copy=False,default = False)
    skull_ap_lateral = fields.Boolean('Skull AP/Lateral')
    mastoid = fields.Boolean('Mastoid')
    tmj = fields.Boolean('Temporo Mandibular Joint')
    sinus = fields.Boolean('Sinus (Waters/Lateral)')
    nasal = fields.Boolean('Nasal')
    panoramik = fields.Boolean('Panoramik/Chepalometri')
    rhese_position = fields.Boolean('Rhese Position')
    thorax = fields.Boolean("Thorax(AP/PA)")
    thorax_lateral = fields.Boolean("Thorax AP+Lateral")
    iga = fields.Boolean("Iga/Costae AP/Oblique")
    top_lordotik = fields.Boolean("Top Lordorik")
    sternum = fields.Boolean("Sternum AP+Oblique")
    bno = fields.Boolean('BNO-IVP')
    cysthography = fields.Boolean('Cysthography')
    urethography = fields.Boolean('Urethography')
    cystourethography = fields.Boolean('Cystourethography')
   
    
    @api.model
    def create(self,val):
        val['name'] = self.env['ir.sequence'].next_by_code('ltest_seq')
        result = super(medical_lab, self).create(val)
        if val.get('test_id'):
            critearea_obj= self.env['medical_test.critearea']
            criterea_ids = critearea_obj.search([('test_id', '=',val['test_id'] )])
            for id in   criterea_ids:
                critearea_obj.write({'medical_lab_id':result})         

        return result

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:    
