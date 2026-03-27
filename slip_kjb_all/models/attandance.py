# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2017  Odoo SA  (http://www.vitraining.com)
#    All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import time
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
from odoo import api, fields, models, _, SUPERUSER_ID


class HRAttendance(models.Model):
    _inherit = "hr.attendance"
    
    checkin_float = fields.Float('CheckIn Jam', compute='_compute_jam_in')
    checkout_float = fields.Float('CheckOut Jam', compute='_compute_jam_out')
    hari = fields.Char('Hari', compute='_compute_hari')
    lambat = fields.Float('Telambat', compute ='_compute_lambat')
    lambat_int = fields.Integer('Telambat', compute ='_compute_lambat')
    pla = fields.Float('PLA', compute ='_compute_pla')
    pla_int = fields.Integer('PLA', compute ='_compute_pla')
    
#    @api.one
    @api.depends('check_in')
    def _compute_hari(self) :
        checkin = datetime.strptime(str(self.check_in), "%Y-%m-%d %H:%M:%S") + timedelta(hours=7)
        hari_checkin = checkin.strftime('%A')
        if hari_checkin == 'Monday':
            self.hari = '0'
        elif hari_checkin == 'Tuesday':
            self.hari = '1'
        elif hari_checkin == 'Wednesday':
            self.hari = '2'
        elif hari_checkin == 'Thursday':
            self.hari = '3'
        elif hari_checkin == 'Friday':
            self.hari = '4'
        elif hari_checkin == 'Saturday':
            self.hari = '5'
        elif hari_checkin == 'Sunday':
            self.hari = '6'    
        else :
            self.hari = 'uncategories'
            
            
    
    
    
#    @api.one
    @api.depends('check_in')
    def _compute_jam_in(self) :
       for record in self:
           if record.check_in:
               checkin = datetime.strptime(str(record.check_in), "%Y-%m-%d %H:%M:%S") + timedelta(hours=7)
               checkin_jam = checkin.strftime('%H.%M.%S')
               record.checkin_float = float(checkin_jam) 
             
#    @api.one
    @api.depends('check_out')
    def _compute_jam_out(self) :
       for record in self:
           if record.check_out:
               checkout  = datetime.strptime(str(record.check_out), "%Y-%m-%d %H:%M:%S") + timedelta(hours=7)
               checkout_jam = checkout.strftime('%H.%M.%S')
               record.checkout_float = float(checkout_jam)  
       
    
    
    
        
#    @api.one
    @api.depends('check_in','checkin_float')
    def _compute_lambat(self) :
        if self.check_in :
            calendar_check = self.env['resource.calendar.attendance'].search([('calendar_id','=',self.employee_id.resource_calendar_id.id),
                                                                          ('dayofweek','=',self.hari),('date_from','=', False )])
            
            calendar_tgl = self.env['resource.calendar.attendance'].search([('calendar_id','=',self.employee_id.resource_calendar_id.id),
                                                                          ('dayofweek','=',self.hari),
                                                                          ('date_from','!=', False )])
            
            
            masuk = []
            if len(calendar_tgl) :
                for tgl in calendar_tgl:
                    if self.check_in >= tgl.date_from and self.check_in <= tgl.date_to :            
                        masuk.append(tgl.hour_from) 
                        jam_min = min(masuk)
                        if self.checkin_float > jam_min :
                                self.lambat = self.checkin_float - jam_min
                                self.lambat_int = 1
                        else :
                                self.lambat = 0
                                self.lambat_int = 0
                    else :
                        masuk_jam = []
                        for o in calendar_check :
                            masuk_jam.append(o.hour_from)
                            min_jam1 = min(masuk_jam)
                            if self.checkin_float > min_jam1 :
                                self.lambat = self.checkin_float - min_jam1
                                self.lambat_int = 1
                            else :
                                self.lambat = 0
                                self.lambat_int = 0
                        
            else :
                jam_masuk = []
                for jam in calendar_check :
                    jam_masuk.append(jam.hour_from)
                    min_jam = min(jam_masuk)
                    if self.checkin_float > min_jam :
                        self.lambat = self.checkin_float - min_jam
                        self.lambat_int = 1
                    else :
                        self.lambat = 0
                        self.lambat_int = 0
                    

                
#    @api.one
    @api.depends('check_out')
    def _compute_pla(self) :
        if self.checkout_float :
            calendar_check = self.env['resource.calendar.attendance'].search([('calendar_id','=',self.employee_id.resource_calendar_id.id),
                                                                          ('dayofweek','=',self.hari), ('date_from','=', False )])
            
            calendar_tgl = self.env['resource.calendar.attendance'].search([('calendar_id','=',self.employee_id.resource_calendar_id.id),
                                                                          ('dayofweek','=',self.hari),
                                                                          ('date_from','!=', False )])
            
            
            keluar = []
            if len(calendar_tgl) :
                for tgl in calendar_tgl:
                    if self.check_out >= tgl.date_from and self.check_out <= tgl.date_to :               
                        keluar.append(tgl.hour_to) 
                        jam_max = max(keluar)
                        if self.checkout_float < jam_max :
                                self.pla = jam_max - self.checkout_float
                                self.pla_int = 1
                        else :
                                self.pla = 0
                                self.pla_int = 0
                    else :
                        keluar_jam = []
                        for o in calendar_check :
                            keluar_jam.append(o.hour_to)
                            max_jam1 = max(keluar_jam)
                            if self.checkout_float < max_jam1 :
                                self.pla = max_jam1 - self.checkout_float
                                self.pla_int = 1
                            else :
                                self.pla = 0
                                self.pla_int = 0
            else :
                jam_keluar = []
                for jam in calendar_check :
                    jam_keluar.append(jam.hour_to)
                    max_jam = max(jam_keluar)
                    if self.checkout_float < max_jam :
                        self.pla = max_jam - self.checkout_float
                        self.pla_int = 1
                    else :
                        self.pla = 0
                        self.pla_int = 0

    def real_working_hours_on_day(self, employee_id, datetime_day):
        day = datetime_day.strftime("%Y-%m-%d 00:00:00")
        day2 = datetime_day.strftime("%Y-%m-%d 24:00:00")

        #employee attendance
        att_id = self.search([('employee_id', '=', employee_id), ('check_in', '>', day), ('check_out', '<', day2)], limit=1, order='check_in asc' )
        
        time1=0
        time2=0
        if att_id :
            time1 = datetime.strptime(att_id.check_in,"%Y-%m-%d %H:%M:%S")
            if att_id.check_out :
                time2 = datetime.strptime(att_id.check_out,"%Y-%m-%d %H:%M:%S")
        
        if time2 and time1:
            delta = (time2 - time1).seconds / 3600.00
        else:
            delta = 0
       
        return delta

