
import time
from datetime import datetime
from datetime import time as datetime_time
from dateutil import relativedelta

import random
import string
from odoo import api, fields, models, _
from odoo.exceptions import Warning as UserWarning


class HrEmployee(models.Model):
    """Implement company wide unique identification number."""

    _inherit = 'hr.employee'

    employee_npwp = fields.Char('NPWP')

class HrPotongan(models.Model):

    _name = 'hr.potongan'
    _description = 'Potongan Gaji'    

    name = fields.Char(string='NIK',readonly=True,states={'draft': [('readonly', False)]})
    contract_id = fields.Many2one('hr.contract',string='Contract',required=True,readonly=True,states={'draft': [('readonly', False)]})
#    employee_id = fields.Many2one('hr.employee',string='Employee',required=True,readonly=True,states={'draft': [('readonly', False)]})
    bmt_tabungan = fields.Float(string='BMT Tabungan', default=0.0,readonly=True,states={'draft': [('readonly', False)]})
    bmt_reguler = fields.Float(string='BMT Reguler', default=0.0,readonly=True,states={'draft': [('readonly', False)]})
    bmt_program = fields.Float(string='BMT Program', default=0.0,readonly=True,states={'draft': [('readonly', False)]})
    bmt_qordh = fields.Float(string='BMT Qordh', default=0.0,readonly=True,states={'draft': [('readonly', False)]})
    potongan_alis = fields.Float(string='Potongan Air-listrik', default=0.0,readonly=True,states={'draft': [('readonly', False)]})
    potongan_kop = fields.Float(string='Koperasi', default=0.0,readonly=True,states={'draft': [('readonly', False)]})
    potongan_ikm = fields.Float(string='Potongan IKM', default=0.0,readonly=True,states={'draft': [('readonly', False)]})
    potongan_lain = fields.Float(string='Potongan Lain-lain', default=0.0,readonly=True,states={'draft': [('readonly', False)]})
    potongan_pin_pri = fields.Float(string='Pinjaman Pribadi', default=0.0,readonly=True,states={'draft': [('readonly', False)]})
    pakan_uf = fields.Float(string='Pakan UF', default=0.0,readonly=True,states={'draft': [('readonly', False)]})
    bnt_kering = fields.Float(string='BNT. Kering', default=0.0,readonly=True,states={'draft': [('readonly', False)]})
    peralatan = fields.Float(string='Peralatan', default=0.0,readonly=True,states={'draft': [('readonly', False)]})
    swalayan = fields.Float(string='Swalayan', default=0.0,readonly=True,states={'draft': [('readonly', False)]})
    kan_material = fields.Float(string='KAN Material', default=0.0,readonly=True,states={'draft': [('readonly', False)]})
    arisan_jabmart = fields.Float(string='Arisan Jabmart', default=0.0,readonly=True,states={'draft': [('readonly', False)]})
    pinj_khusus_p = fields.Float(string='Pinjaman Khusus P2', default=0.0,readonly=True,states={'draft': [('readonly', False)]})
    pel_keswan = fields.Float(string='Pel Keswan', default=0.0,readonly=True,states={'draft': [('readonly', False)]})
    asuransi = fields.Float(string='Asuransi', default=0.0,readonly=True,states={'draft': [('readonly', False)]})
    rumput = fields.Float(string='Rumput', default=0.0,readonly=True,states={'draft': [('readonly', False)]})
    investor = fields.Float(string='Investor', default=0.0,readonly=True,states={'draft': [('readonly', False)]})
    ampas_bir = fields.Float(string='Ampas Bir', default=0.0,readonly=True,states={'draft': [('readonly', False)]})
    takziah = fields.Float(string='Takziah', default=0.0,readonly=True,states={'draft': [('readonly', False)]})
    kis = fields.Float(string='KIS', default=0.0,readonly=True,states={'draft': [('readonly', False)]})
    ember = fields.Float(string='Ember', default=0.0,readonly=True,states={'draft': [('readonly', False)]})
    pmk = fields.Float(string='PMK', default=0.0,readonly=True,states={'draft': [('readonly', False)]})
    bengkel = fields.Float(string='Bengkel', default=0.0,readonly=True,states={'draft': [('readonly', False)]})
    jual_sapi = fields.Float(string='Jual Sapi', default=0.0,readonly=True,states={'draft': [('readonly', False)]})
    from_date = fields.Date(string='From',required=True,readonly=True,states={'draft': [('readonly', False)]})
    to_date = fields.Date(string='To',required=True,readonly=True,states={'draft': [('readonly', False)]})
    state = fields.Selection([
        ('draft', 'Draft'),
        ('valid', 'Validated'),
        ('proses', 'Proses')
        ], string='Status', default='draft',copy=False, index=True, readonly=True, store=True)
    korpen = fields.Float(string='Koreksi Pendapatan', default=0.0,readonly=True,states={'draft': [('readonly', False)]})     
    
    def action_validate(self):
        return

class HrContractAdd(models.Model):
    """Implement company wide unique identification number."""

    _inherit = 'hr.contract'
    
    deduction_lines = fields.One2many('hr.potongan','contract_id',string='Other Allowance')
