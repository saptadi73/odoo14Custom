import time
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _, SUPERUSER_ID
from odoo.exceptions import UserError, ValidationError


class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    _description = 'Employee'

    divisi_id       = fields.Many2one('hr.employee.divisi', string="Divisi")
#    leaving_date   = fields.Date("Leaving Date", required=True)
    
class Divisi(models.Model):
    _name = 'hr.employee.divisi'
    _description = 'HR Employee Divisi'

    name = fields.Char(string="Divisi")