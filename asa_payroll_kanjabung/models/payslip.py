from datetime import date, datetime, time
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _, SUPERUSER_ID
from odoo.exceptions import UserError, ValidationError
import itertools
from operator import itemgetter
import operator

class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    _description = 'Employee'

    peternak_id = fields.Many2one('peternak.sapi', 'Peternak')

class PayslipRun(models.Model):
    _inherit = "hr.payslip.run"

    periode_id = fields.Many2one('periode.setoran', string='Periode Setoran', required=True)
    date_start = fields.Date(string='Date From', required=True, readonly=True, help="start date",
                             states={'draft': [('readonly', False)]},
                             default=lambda self: fields.Date.to_string(date.today().replace(day=1)))
    date_end = fields.Date(string='Date To', required=True, readonly=True, help="End date",
                           states={'draft': [('readonly', False)]},
                           default=lambda self: fields.Date.to_string(
                               (datetime.now() + relativedelta(months=+1, day=1, days=-1)).date()))

    @api.onchange('periode_id')
    def onchange_periode_id(self):
        if self.periode_id:
            self.date_start = self.periode_id.periode_setoran_awal
            self.date_end = self.periode_id.periode_setoran_akhir

class Payslip(models.Model):
    _inherit = "hr.payslip"
    
    setor_pagi          = fields.Float('Setor Pagi', states={'done': [('readonly', True)]})
    setor_sore          = fields.Float('Setor Sore', states={'done': [('readonly', True)]})
    insen_prod          = fields.Float('Insentif Produksi', states={'done': [('readonly', True)]})
    insen_pmk           = fields.Float('Insentif PMK', states={'done': [('readonly', True)]})
    insen_daya_saing    = fields.Float('Insentif Daya Saing', states={'done': [('readonly', True)]})
    # fat                 = fields.Float('FAT',states={'done': [('readonly', True)]})
    fat_id              = fields.Many2one('tabel.fat', 'FAT', states={'done': [('readonly', True)]})
    grade_id            = fields.Many2one('tabel.grade', 'Grade', states={'done': [('readonly', True)]})
    harga_kual          = fields.Float('Harga Kualitas', states={'done': [('readonly', True)]})
    harga_satuan        = fields.Float('Harga Satuan', states={'done': [('readonly', True)]})
    total_harga_estimasi = fields.Float('Total Harga Susu', states={'done': [('readonly', True)]})
    tot_setoran         = fields.Float('Total Setoran Susu', states={'done': [('readonly', True)]})
    tot_tagihan         = fields.Float('Total Tagihan', compute='get_allocation_amount')
    inv_pay_ids         = fields.One2many('invoice.payslip', 'payslip_id')
    allocation_amount   = fields.Float('Total Amount', compute='get_allocation_amount')
    payment_method_id   = fields.Many2one('account.journal', string='Payment Method', required=False, domain=[('type', 'in', ('bank', 'cash'))])
    payment_count       = fields.Integer(compute='compute_payment_count')
    periode_id          = fields.Many2one('periode.setoran', string='Periode Setoran', required=False)
    liter_id            = fields.Many2one('liter.sapi', string='Liter Sapi', required=False)

    @api.onchange('periode_id')
    def onchange_periode_id(self):
        if self.periode_id :
            self.date_from = self.periode_id.periode_setoran_awal
            self.date_to   = self.periode_id.periode_setoran_akhir
    
    def get_amount_input(self):
        for rec in self :
            for line in rec.input_line_ids :
                invoice = self.env['invoice.payslip'].search([('payslip_id', '=', rec.id), ('code', '=', line.code)])
                if invoice :
                    allocation = 0
                    for inv in invoice :
                        allocation += inv.allocation
                else :
                    allocation = 0

                line.amount = allocation



    def get_payment(self):
        action = self.env.ref('account.'
                              'action_account_payments').read()[0]
        action['domain'] = [('payslip_id', 'in', self.ids)]
        return action

    def compute_payment_count(self):
        for record in self:
            record.payment_count = self.env['account.payment'].search_count(
                [('payslip_id', 'in', self.ids)])

    def process_payment(self):
        pay_method_id= self.env['account.payment.method'].search([('name','=','Manual')],limit=1)
        if not pay_method_id:
            pay_method_id= self.env['account.payment.method'].search([],limit=1)

        for rec in self.inv_pay_ids.mapped('company_id') :
            journal = self.env['invoice.payslip'].search([('company_id','=',rec.id),('payslip_id','=',self.id)],limit=1)
            
            if not journal.payment_method_id :
                raise UserError(_("Payment Method harus diisi terlebih dahulu....!! "))


            pay_val={
                'payment_type':'inbound',
                'partner_type':'customer',
                'payment_for':True,
                'partner_id':self.employee_id.peternak_id.partner_id.id,
                'journal_id': journal.payment_method_id.id or False,
                'payment_method_id': pay_method_id.id or False,
                'state':'draft',
                'amount':0,
                'payslip_id':self.id,
                'company_id' : rec.id
                }



            payment_id = self.env['account.payment'].create(pay_val)
            line_list=[]
            paid_amt=0
            for line in self.inv_pay_ids:
                if line.company_id.id == rec.id :
                    line_list.append((0,0,{
                        'invoice_id':line.invoice_id.id,
                        'date':line.date,
                        'due_date':line.due_date,
                        'original_amount':line.original_amount,
                        'balance_amount':line.balance_amount,
                        'allocation':line.allocation,
                        'account_payment_id':payment_id.id or False,
                        'tipe_invoice' : line.tipe_invoice
                    }))

                    paid_amt += line.allocation

            payment_id.write({
                'line_ids':line_list,
                'amount'  : paid_amt
            })

        # # payment_id.dev_generate_moves()
        return True



    @api.depends('inv_pay_ids','inv_pay_ids.allocation')
    def get_allocation_amount(self):
        for payment in self:
            amount = 0
            tagihan = 0
            payment.allocation_amount = 0
            for line in payment.inv_pay_ids:
                amount += line.allocation
                tagihan += line.balance_amount

            payment.allocation_amount = amount
            payment.tot_tagihan = tagihan

    def load_payment_lines(self):
        self.inv_pay_ids.unlink()
        account_inv_obj = self.env['account.move']
        invoice_ids=[]
        query = """ select id from account_move where partner_id = %s and state = %s and move_type in %s and payment_state != %s"""
        params = (self.employee_id.peternak_id.partner_id.id,'posted',('out_invoice','out_refund'), 'paid')
        self.env.cr.execute(query, params)
        result = self.env.cr.dictfetchall()
        invoice_ids = [inv.get('id') for inv in result]
        invoice_ids = account_inv_obj.browse(invoice_ids)
        for vals in invoice_ids:
            account_id = False
            account_id = vals.partner_id and vals.partner_id.property_account_receivable_id.id or False
                
            original_amount = vals.amount_total
            balance_amount = vals.amount_residual
            allocation = vals.amount_residual
            tipe_invoice = vals.tipe_invoice

            query = """ INSERT INTO invoice_payslip (invoice_id, account_id, date, due_date, original_amount, balance_amount, payslip_id, tipe_inv_id, code, company_id) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
            params = (vals.id,account_id, vals.invoice_date, vals.invoice_date_due, original_amount, balance_amount, self.id, vals.tipe_inv_id.id, vals.tipe_inv_id.code, vals.company_id.id)
            self.env.cr.execute(query, params)


    def get_setoran(self):
        if not self.employee_id.peternak_id.id :
            raise UserError(_("Employee yang dipilih belum ada peternaknya....!! "))
        else :
            setoran = self.env['liter.sapi'].search([('peternak_id', '=', self.employee_id.peternak_id.id), ('tgl_awal', '=', self.date_from),
                                                 ('tgl_akhir', '=', self.date_to)], limit=1)

            if setoran :
                pagi            = 0.0
                sore            = 0.0
                insen_prod      = setoran.insen_prod
                insen_pmk       = setoran.insen_pmk
                insen_daya_saing = setoran.insen_daya_saing
                # fat             = setoran.fat
                fat_id          = setoran.fat_id.id
                grade_id           = setoran.grade_id.id
                harga_kual      = setoran.harga_kual
                harga_satuan    = setoran.harga_satuan
                total_harga_estimasi = setoran.total_harga_estimasi
                tot_setoran     = setoran.setoran
                liter_id        = setoran.id

                for s in setoran.setoran_line_ids :
                    if s.tipe_setor_pagi == '1' :
                        pagi += s.setoran_pagi_l
                    if s.tipe_setor_sore == '2' :
                        sore += s.setoran_sore_l
            
            else :
                raise UserError(_("Belum ada setoran susu di periode %s sampai %s") %(self.date_from, self.date_to))


            # tagihan = self.env['account.move'].search([('partner_id', '=', self.employee_id.peternak_id.partner_id.id),('move_type', '=', 'out_invoice'), ('state', '=', 'posted'),
            #                                             ('payment_state', '=', 'not_paid')])

            # tot_tagihan = 0.0
            # if tagihan :
            #     for t in tagihan :
            #         tot_tagihan += t.amount_residual


        return {
            'setor_pagi'    : pagi,
            'setor_sore'    : sore,
            'insen_prod'    : insen_prod,
            'insen_pmk'     : insen_pmk,
            'insen_daya_saing': insen_daya_saing,
            # 'fat'           : fat,
            'fat_id'           : fat_id,
            'grade_id'         : grade_id,
            'harga_kual'    : harga_kual,
            'harga_satuan'  : harga_satuan,
            'total_harga_estimasi'  : total_harga_estimasi,
            'tot_setoran'   : tot_setoran,
            'liter_id'      : liter_id
            # 'tot_tagihan'   : tot_tagihan
        }
    
    
    
        
    @api.onchange('employee_id', 'date_from', 'date_to')
    def onchange_employee(self):
        res = super(Payslip, self).onchange_employee()
        if self.contract_id:
            setoran = self.get_setoran()
            self.setor_pagi = setoran.get('setor_pagi') or 0.0
            self.setor_sore = setoran.get('setor_sore') or 0.0
            self.insen_prod = setoran.get('insen_prod') or 0.0
            self.insen_pmk = setoran.get('insen_pmk') or 0.0
            self.insen_daya_saing = setoran.get('insen_daya_saing') or 0.0
            self.fat_id = setoran.get('fat_id') or False
            self.grade_id = setoran.get('grade_id') or False
            self.harga_kual = setoran.get('harga_kual') or 0.0
            self.harga_satuan = setoran.get('harga_satuan') or 0.0
            self.total_harga_estimasi = setoran.get('total_harga_estimasi') or 0.0
            self.tot_setoran = setoran.get('tot_setoran') or 0.0
            self.tot_tagihan = setoran.get('tot_tagihan') or 0.0
            self.liter_id = setoran.get('liter_id') or False


    def compute_setoran(self):
        setoran = self.get_setoran()
        self.setor_pagi = setoran.get('setor_pagi') or 0.0
        self.setor_sore = setoran.get('setor_sore') or 0.0
        self.insen_prod = setoran.get('insen_prod') or 0.0
        self.insen_pmk = setoran.get('insen_pmk') or 0.0
        self.insen_daya_saing = setoran.get('insen_daya_saing') or 0.0
        self.fat_id = setoran.get('fat_id') or False
        self.grade_id = setoran.get('grade_id') or False
        self.harga_kual = setoran.get('harga_kual') or 0.0
        self.harga_satuan = setoran.get('harga_satuan') or 0.0
        self.total_harga_estimasi = setoran.get('total_harga_estimasi') or 0.0
        self.tot_setoran = setoran.get('tot_setoran') or 0.0
        self.tot_tagihan = setoran.get('tot_tagihan') or 0.0
        self.liter_id = setoran.get('liter_id') or False



class InvoiceLinePyslip(models.Model):
    _name = 'invoice.payslip'
    _description = 'Invoice Payment Line'

    invoice_id = fields.Many2one('account.move',string='Invoice')
    account_id = fields.Many2one('account.account', string="Account")
    payment_method_id   = fields.Many2one('account.journal', string='Payment Method', required=False, domain=[('type', 'in', ('bank', 'cash'))])
    date = fields.Date(string="Date")
    due_date = fields.Date(string="Due Date")
    original_amount = fields.Float(string="Invoice Amount")
    balance_amount = fields.Float(string="Balance Amount")
    allocation = fields.Float(string="Allocation")
    diff_amt = fields.Float('Remaining Amount',compute='get_diff_amount')
    payslip_id = fields.Many2one('hr.payslip',string='Payslip')
    tipe_inv_id = fields.Many2one('master.tipe.invoice',string='Tipe Invoice')
    code = fields.Char(string='Code')
    tipe_invoice = fields.Selection([('kredit_pkp', 'Kredit PKP'),('kredit_sapi', 'Kredit Sapi'),('peralatan', 'Peralatan')], string='Tipe Invoice')
    company_id= fields.Many2one('res.company',string='Company')

    @api.onchange('tipe_inv_id')
    def onchange_tipe_invoice(self):
        if self.tipe_inv_id :
            self.code = self.tipe_inv_id.code

    @api.depends('balance_amount','allocation')
    def get_diff_amount(self):
        for line in self: 
            line.diff_amt = line.balance_amount - line.allocation




class MasterTipeInvoice(models.Model):
    _name = 'master.tipe.invoice'
    _description = 'Master Tipe Invoice'

    code = fields.Char(string='Code')
    name = fields.Char(string='Name')    

            

        
        