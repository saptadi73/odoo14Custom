# -*- coding: utf-8 -*-
# Part of Akun+. See LICENSE file for full copyright and licensing details.

from datetime import datetime, timedelta, date
from functools import partial
from itertools import groupby
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.misc import formatLang
from odoo.osv import expression
from odoo.tools import float_is_zero, float_compare
from odoo.addons import decimal_precision as dp

from werkzeug.urls import url_encode
import re
import xlwt
import base64
import io
import csv
import psycopg2
from psycopg2 import DatabaseError, errorcodes



class SimPinMitraBankLoanDetail(models.Model):
    _name = "simpin_syariah.loan_detail"
    _description = "Loan Detail Produk Bank Mitra Kerja Simpin Syariah"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "tanggal_akad, periode_angsuran,name"

    @api.model
    def _default_currency(self):
        return self.env.user.company_id.currency_id.id

    name = fields.Char(string='Loan Detail', copy=False, index=True,track_visibility='onchange', states={'draft': [('readonly', False)]})
    mitra_bank_id = fields.Many2one('simpin_syariah.mitra.bank',string='Mitra Bank', readonly=True, store=True)
    company_id = fields.Many2one('res.company', string='Company', required=True,
        copy=False, default=lambda self: self.env['res.company']._company_default_get())
    pembiayaan_lines = fields.One2many('simpin_syariah.pembiayaan', 'loan_id','Pembiayaan', domain=[('state', 'in', ['check','active','approve','close'])],
                                       readonly=False, copy=True, track_visibility='onchange')
    #invoice_lines = fields.One2many('account.invoice', 'loan_id', string='Angsuran Bank', copy=False, store=True, domain=[('type', '=', 'in_invoice')])
    total_pembiayaan = fields.Monetary(string='Total Pembiayaan',  currency_field='currency_id',compute='compute_total',store=True)
    margin = fields.Float(string='Margin (%)', track_visibility='onchange', states={'draft': [('readonly', False)]}, required=True)
    periode_angsuran = fields.Integer(string='Periode Angsuran', required=True, readonly=True,
                                      track_visibility='onchange', states={'draft': [('readonly', False)]}, default=12)
    total_angsuran = fields.Monetary(string='Total Angsuran',  compute='compute_total',store=True)
    tanggal_akad = fields.Date(string='Tanggal Awal', track_visibility='onchange', states={'draft': [('readonly', False)]}, store=True, default=date.today())
    jatuh_tempo = fields.Date(string='Tanggal Akhir', readonly=True, store=True)
    saldo = fields.Monetary(string='Saldo',  currency_field='currency_id', compute='compute_saldo',store=True)
    currency_id = fields.Many2one('res.currency', string="Currency", readonly=True, default=_default_currency)
    product_id = fields.Many2one('product.product',string='Produk', readonly=True, store=True) 
    state = fields.Selection([
        ('draft', 'Draft'),
        ('running', 'Running'),
        ('close', 'Closed'),
        ], string='Status', copy=False, index=True, default='draft', readonly=True)
#    credit_account = fields.Many2one('account.account', required=True, string='HPP Pokok', states={'draft': [('readonly', False)]}, store=True,track_visibility='onchange')
    account_analytic_id = fields.Many2one('account.analytic.account', string='Analytic Account')
    #invoice_id = fields.Many2one('account.invoice', string='Invoice Pembiayaan Bank', copy=False, store=True)
    journal_id = fields.Many2one('account.journal', string='Journal Pembiayaan Bank', store=True)
    tanggal_akad_pembiayaan = fields.Date(string='Tanggal Akad Pembiayaan', track_visibility='onchange', states={'draft': [('readonly', False)]}, store=True, default=date.today())

    @api.onchange('tanggal_akad','periode_angsuran')
    def onchange_tanggal_akad(self):
        if self.tanggal_akad and self.periode_angsuran:
            self.jatuh_tempo = self.tanggal_akad + relativedelta(months=self.periode_angsuran)
        
    
    @api.depends('pembiayaan_lines.state','margin','total_pembiayaan')
    #@api.depends('pembiayaan_lines.state','margin','invoice_lines','invoice_lines.state','total_pembiayaan')
    def compute_total(self):
        for line in self:
#        raise UserError(_('pembiayaan_lines %s')%(self.pembiayaan_lines,))
            total_pembiayaan = total_angsuran = 0.0

#            total_angsuran = self.total_angsuran
            for biaya in line.pembiayaan_lines:
                if biaya.state=='active' or biaya.state=='approve': # or biaya.state=='close': 
                    total_pembiayaan += biaya.total_pembiayaan


            if line.pembiayaan_lines and line.state=='running':
                line.update({'total_pembiayaan': total_pembiayaan,})

            if line.margin>0:
                total_angsuran = self.calc_pmt(line.margin,line.periode_angsuran,total_pembiayaan)

            saldo = total_angsuran * self.periode_angsuran
            for inv in line.invoice_lines:
                if inv.state=='paid':
                    saldo -= inv.amount_total
            line.update({'total_angsuran': total_angsuran,'saldo': saldo,})

    def calc_pmt(self,margin,periode_angsuran,nilai_pinjaman):
        annual_rate = margin/100
        interest_rate = annual_rate / 12
        present_value = nilai_pinjaman * interest_rate

        angsuran = present_value / (1-((1 + interest_rate)**-periode_angsuran))
        return angsuran

    
    #@api.depends('invoice_lines.state')
    def compute_saldo(self):
        for line in self:
            data_angsuran = line.get_data_angsuran()
            to_pay = 0.0
            for inv in line.invoice_lines:
                to_pay+=inv.residual_signed
            bulan_jalan = relativedelta(date.today(),line.tanggal_akad)
            bulan = bulan_jalan.years*12 + bulan_jalan.months
            saldo = self.saldo + to_pay
#            raise UserError(_('saldo %s')%(saldo,))

            
    
    def print_jadwal_angsuran(self):
        return self.env.ref('simpin_syariah.action_jadwal_angsuran_bank').report_action(self.id)

    def get_data_angsuran(self):
        periode = self.periode_angsuran
        angsuran = self.total_angsuran
        if self.tanggal_akad:
            bulan = self.tanggal_akad
        else:
            bulan = date.today()
        pokok_pinjaman = self.total_pembiayaan
        angsuran_margin = pokok_pinjaman * (self.margin/1200)
        angsuran_pokok = angsuran - angsuran_margin
        result = []
        for i in range(1,periode+1):
            isi_data ={}
            bulan += relativedelta(months=1)
            if i==1:
                pokok_pinjaman = self.total_pembiayaan
                angsuran_margin = pokok_pinjaman * (self.margin/1200)
                angsuran_pokok = angsuran - angsuran_margin
            else:
                pokok_pinjaman -= angsuran_pokok
                angsuran_margin = pokok_pinjaman * (self.margin/1200)
                angsuran_pokok = angsuran - angsuran_margin

            isi_data['no'] = i
            isi_data['periode'] = datetime.strftime(bulan,'%B %Y')
            isi_data['pokok_pinjaman'] = round(pokok_pinjaman,0)
            isi_data['angsuran_pokok'] = round(angsuran_pokok,0)
            isi_data['angsuran_margin'] = round(angsuran_margin,0)
            isi_data['angsuran_bulanan'] = round(angsuran,0)
        
            result.append(isi_data)
        return result  

    def action_get_pembiayaan(self):
        total_pembiayaan = 0
        for product in self.mitra_bank_id.product_lines:
            pembiayaan = self.env['simpin_syariah.pembiayaan'].search([('product_id','=', product.id),
                                                                       ('periode_angsuran','=',self.periode_angsuran),
                                                                       ('state','in',['check','approve']),
                                                                       ],order='akad_id, periode_angsuran')
#            raise UserError(_('res %s')%(pembiayaan,))
            for line in pembiayaan:
                total_pembiayaan += line.total_pembiayaan
                line.write({'mitra_bank_id':self.mitra_bank_id.id,'loan_id': self.id})
                line.onchange_mitra_bank_id()
                line._onchange_biaya_lines()
        self.write({'total_pembiayaan': total_pembiayaan})

    
    def action_run_ld(self):
        self.compute_total()
        if self.margin<=0.0 or self.periode_angsuran<=0 or not self.mitra_bank_id.journal_id:
            raise UserError(_('Periode Angsuran dan Margin TIDAK boleh 0'))
        
        prod = []
        for product in self.mitra_bank_id.product_lines:
            prod.append(product.id)
        csql = """
        select distinct akad_id,sum(total_pembiayaan) total
        from simpin_syariah_pembiayaan
        where loan_id=%s
        group by akad_id
        """
        self.env.cr.execute(csql, (self.id,))
        pembiayaan = self.env.cr.dictfetchall()
        invoice_lines = []
        biaya_admin = 0
        pct = nominal = False
        for biaya_bank in self.mitra_bank_id.biaya_lines:
            if biaya_bank.is_bill:
                if biaya_bank.nilai_pct>0:
                    pct = biaya_bank.nilai_pct /100
                    coa_pct = biaya_bank.coa_debit
                    name_pct = biaya_bank.name
                elif biaya_bank.nominal>0:
                    nominal = biaya_bank.nominal * len(self.pembiayaan_lines)
                    coa_nominal = biaya_bank.coa_debit
                    name_nominal = biaya_bank.name
                else:
                    raise UserError(_('Komponen Biaya Bank %s belum memiliki Nilai')%(self.mitra_bank_id.name,))
        coa_pokok = coa_margin = False
        if self.mitra_bank_id.hpp_pokok:
            coa_pokok = self.mitra_bank_id.hpp_pokok
        if self.mitra_bank_id.hpp_margin:
            coa_margin = self.mitra_bank_id.hpp_margin
            total_margin = (self.total_angsuran * self.periode_angsuran) - self.total_pembiayaan
        if not self.mitra_bank_id.hpp_pokok and not self.mitra_bank_id.hpp_margin:
            raise UserError(_('Konfigurasi HPP Pokok dan HPP Margin belum sesuai'))    

        for line in pembiayaan:
            akad_id = self.env['master.akad_syariah'].search([('id','=',line['akad_id'])])
            biaya_admin += line['total'] * pct
            invoice_lines += [(0, 0, self._prepare_inv_line(akad_id,line['total'],self.product_id,self.periode_angsuran,coa_pokok,coa_pokok.name + ' ' + akad_id.name))]

        if coa_margin:
            invoice_lines += [(0, 0, self._prepare_inv_line(akad_id,total_margin,self.product_id,self.periode_angsuran,coa_margin,coa_margin.name + ' ' + self.name))]
        if pct:
            invoice_lines += [(0, 0, self._prepare_inv_line(akad_id,-biaya_admin,self.product_id,self.periode_angsuran,coa_pct,name_pct))]
        if nominal:
            invoice_lines += [(0, 0, self._prepare_inv_line(akad_id,-nominal,self.product_id,self.periode_angsuran,coa_nominal,name_nominal))]

#        raise UserError(_('Create Invoice senilai %s \n invoice_lines %s \n jml %s')%(self.total_pembiayaan,invoice_lines,len(self.pembiayaan_lines)))
        self.state = 'running'
        for product in self.mitra_bank_id.product_lines:
            product.update({'state': self.state})
        for line in self.pembiayaan_lines:
            line.action_approve(self.tanggal_akad_pembiayaan)

        inv_vals = {
                    'date_invoice': self.tanggal_akad,
                    'name': 'Pengajuan Pembiayaan ' + self.mitra_bank_id.name + ' - ' + self.name,
                    'origin': self.name,
                    'type': 'out_invoice',
                    'reference': False,
                    'account_id': self.mitra_bank_id.journal_id.default_credit_account_id.id,
                    'partner_id': self.mitra_bank_id.partner_id.id,
                    'invoice_line_ids': invoice_lines,
                    'currency_id': self.currency_id.id,
                    'comment': 'Pengajuan ' + self.mitra_bank_id.name + ' - ' + self.name,
                    'payment_term_id': 1,
                    'mitra_bank_id': self.mitra_bank_id.id,
                    'loan_id': self.id,
                    'type_journal': 'Bill LD',
                    'operating_unit_id': self.env.user.default_operating_unit_id.id,
                    }
#        raise UserError(_('vals %s')%(inv_vals,))
        invoice = self.env['account.invoice'].create(inv_vals)

        invoice.action_invoice_open_syariah()
        self.invoice_id = invoice.id
        self.saldo = self.total_angsuran * self.periode_angsuran
        move_line = self.env['account.move.line'].search([('move_id','=',invoice.move_id.id)])
        for line in move_line:
            line.analytic_account_id = self.account_analytic_id.id

        return {
                'type': 'ir.actions.client',
                'tag': 'reload',
                }

        
    def _prepare_inv_line(self, akad, amount, product_id, periode,coa=False,label=False):
        if coa:
            account_id = coa.id
            name = label
        else:
            account_id = akad.journal_id.default_credit_account_id.id
            name = 'Pengajuan ' + akad.name.upper() + ' ' + self.mitra_bank_id.name + ' - ' + self.name + ': ' + str(periode) + ' Bulan'
        return {
                'name': name,
#                'origin': 'Pengajuan ' + akad.name.upper() + ' ' + product_id.name + ': ' + str(periode) + ' Bulan',
                'account_id': account_id,
                'price_unit': amount,
                'quantity': 1.0,
                'discount': 0.0,
                'product_id': product_id.id,
                'account_analytic_id': self.account_analytic_id.id or False,
                'operating_unit_id': self.env.user.default_operating_unit_id.id,
                }

    
    def action_create_bill(self):
        invoice_lines = []
        loan_id = coa_hpp = name_hpp = False
        date_today = date.today() #datetime.strptime('2021-09-25','%Y-%m-%d') # 
        for line in self:
            if line.state=='running' and line.saldo==0:
                line.write({'state': 'close'})
            elif line.total_pembiayaan==0 and line.total_angsuran==0:
                line.write({'state': 'close'})
            elif line.state=='running' and line.saldo>0:
                tgl_inv = False
                jml_bulan = relativedelta(date_today,line.tanggal_akad)
                last_invoice = self.env['account.invoice'].search([('type_journal','=','Bill LD'),
                                                                    ('type','=','in_invoice'),
                                                                    ('loan_id','=',line.id),('date_invoice','<=',date_today),
                                                                    ('state','in',['open','paid'])],
                                                                    order='date_invoice desc',limit=1)
                if last_invoice and last_invoice.date_invoice<=line.jatuh_tempo:
                    cbln = relativedelta(date_today,last_invoice.date_invoice)
                    if cbln.months>=1:
                        tgl_inv = last_invoice.date_invoice + relativedelta(months=1)
                        jml_bulan = relativedelta(tgl_inv,line.tanggal_akad)
                        bln = (jml_bulan.years*12)+jml_bulan.months-1
#                    raise UserError(_('Create Vendor Bill %s - %s')%(tgl_inv,cbln,))
                elif not last_invoice and jml_bulan.months>0:
                    day_diff = date_today.day - line.tanggal_akad.day
                    tgl_inv = date_today-relativedelta(days=day_diff)
                    bln = (jml_bulan.years*12)+jml_bulan.months

                data_angsuran = line.get_data_angsuran()

#                raise UserError(_('tgl %s \n %s == %s \n inv %s -- %s')%(line.name,tgl_inv,line.jatuh_tempo.strftime("%Y-%m-%d"), last_invoice.date_invoice,jml_bulan))
                if tgl_inv and line.periode_angsuran>bln and tgl_inv.strftime("%Y-%m-%d")<=line.jatuh_tempo.strftime("%Y-%m-%d"):
                    loan_id = line.id
                    product_grouped = {}
                    pembiayaan = self.env['simpin_syariah.pembiayaan'].search([('loan_id','=',line.id)],order='product_id')
                    for biaya in pembiayaan:
                        val = {'product_id': biaya.product_id.id, 'amount': biaya.total_pembiayaan}
                        key = biaya.product_id.id
                        if key not in product_grouped:
                            product_grouped[key] = val
                        else:
                            product_grouped[key]['amount'] += val['amount']
#                   raise UserError(_('product_grouped %s')%(product_grouped,))

                    coa_pokok = self.mitra_bank_id.hpp_pokok
                    name_pokok = coa_pokok.name + ' ' + line.name.upper()
                    invoice_lines = [(0, 0, self.mitra_bank_id.prepare_inv_line(line,data_angsuran[bln]['angsuran_pokok'],tgl_inv,coa_pokok.id,name_pokok))]
                    coa_margin = self.mitra_bank_id.hpp_margin
                    name_margin = coa_margin.name + ' ' + line.name.upper()
                    invoice_lines += [(0, 0, self.mitra_bank_id.prepare_inv_line(line,data_angsuran[bln]['angsuran_margin'],tgl_inv,coa_margin.id,name_margin))]
                    inv_vals = {
                                'date_invoice': tgl_inv.strftime("%Y-%m-%d"),
                                'name': 'Angsuran Pembiayaan ' + line.name.upper() + ': ' + tgl_inv.strftime("%B %Y"),
                                'type': 'in_invoice',
                                'reference': self.mitra_bank_id.bank_id.name + ': ' + line.name,
                                'origin': self.mitra_bank_id.bank_id.name + ': ' + line.name,
                                'account_id': self.mitra_bank_id.journal_id.default_debit_account_id.id,
                                'partner_id': self.mitra_bank_id.partner_id.id,
                                'invoice_line_ids': invoice_lines,
                                'currency_id': self.mitra_bank_id.currency_id.id,
                                'comment': 'Angsuran Pembiayaan' + line.name.upper() + ': ' + tgl_inv.strftime("%B %Y"),
                                'payment_term_id': 1,
                                'mitra_bank_id': self.mitra_bank_id.id,
                                'loan_id': loan_id,
                                'type_journal': 'Bill LD',
                                'operating_unit_id': self.env.user.default_operating_unit_id.id,
                                }
#                    raise UserError(_('Create Vendor Bill %s ')%(inv_vals,))
                    invoice = self.env['account.invoice'].create(inv_vals)
                    invoice.action_invoice_open_syariah()
                    move_line = self.env['account.move.line'].search([('move_id','=',invoice.move_id.id)])
                    for mline in move_line:
                        mline.analytic_account_id = line.account_analytic_id.id



class SimPinMitraBank(models.Model):
    _name = "simpin_syariah.mitra.bank"
    _description = "Bank Mitra Kerja Simpin Syariah"
    _inherit = ['mail.thread', 'mail.activity.mixin']
#    _inherit = 'res.partner'

    @api.model
    def _default_currency(self):
        return self.env.user.company_id.currency_id.id


    name = fields.Char(string='Nama Bank', related="bank_id.name", copy=False, index=True)
    company_id = fields.Many2one('res.company', string='Company', required=True,
        copy=False, default=lambda self: self.env['res.company']._company_default_get())
    bank_id = fields.Many2one('res.bank','Bank',required=True,help='Nama Mitra Bank', track_visibility='onchange', index=True)
    plafond = fields.Monetary(string='Plafond', currency_field='currency_id', store=True, index=True, track_visibility='onchange')    
    currency_id = fields.Many2one('res.currency', string="Currency", readonly=True, default=_default_currency)
    tanggal_akad = fields.Date(string='Tanggal Akad',  index=True, track_visibility='onchange')
    tanggal_akhir = fields.Date(string='Jatuh Tempo',  index=True, track_visibility='onchange')
    product_lines = fields.One2many('product.product','mitra_bank_id',string='Products Lines', index=True, domain=[('state', '!=', 'close')])
    biaya_lines = fields.One2many('mitra_bank.biaya','mitra_bank_id',string='Komponen Biaya')
    ld_lines = fields.One2many('simpin_syariah.loan_detail','mitra_bank_id',string='Loan Detail')
    total_pencairan = fields.Monetary(string='Total Pencairan',  currency_field='currency_id', compute='compute_total',store=True)
    partner_id = fields.Many2one('res.partner', string='Partner', store=True)
    journal_id = fields.Many2one('account.journal', string='Journal')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submit', 'Submitted'),
        ('check', 'Check Document'),
        ('approve', 'Approved'),
        ('active', 'Active'),
        ('close', 'Closed'),
        ], string='Status', copy=False, index=True, default='draft', track_visibility='onchange', readonly=True)
    account_analytic_id = fields.Many2one('account.analytic.account', string='Analytic Account',track_visibility='onchange')

    hpp_pokok = fields.Many2one('account.account', string='HPP Pokok', states={'draft': [('readonly', False)]}, store=True,track_visibility='onchange')
    hpp_margin = fields.Many2one('account.account', string='HPP Margin', states={'draft': [('readonly', False)]}, store=True,track_visibility='onchange')
    escrow_account = fields.Many2one('account.account', string='Escrow Account', states={'draft': [('readonly', False)]}, store=True,track_visibility='onchange')
    mydt_account = fields.Many2one('account.account', string='Account MYDT', states={'draft': [('readonly', False)]}, store=True,track_visibility='onchange')
    hpp_account = fields.Many2one('account.account', string='HPP', states={'draft': [('readonly', False)]}, store=True,track_visibility='onchange')

    
    @api.depends('product_lines')
    def compute_total(self):
        for xline in self:
            total = 0.0
            if xline.product_lines:
                for line in xline.product_lines:
                    total_pengajuan = 0.0
                    total_pembiayaan = 0.0
                    total_cair = 0
                    pengajuan = self.env['simpin_syariah.pembiayaan'].search([('state','in',['approve','submit']),('product_id','=',line.id)])
                    for ajuan_line in pengajuan:
                        total_pengajuan += ajuan_line.total_pembiayaan
                    pencairan = self.env['simpin_syariah.pembiayaan'].search([('state','in',['active','close']),('product_id','=',line.id)])
                    for cair_line in pencairan:
                        total_cair += cair_line.total_pembiayaan
                    line.total_pembiayaan = total_cair
                    line.total_pengajuan = total_pengajuan
                    total += total_cair
                xline.total_pencairan = total

    @api.onchange('bank_id')
    def onchange_bank_id(self):
        if self.bank_id:
            partner_id = self.env['res.partner'].search([('name','=',self.name)])
            if not partner_id or len(partner_id)==0:
                partner_id = self.env['res.partner'].create({
                                'name': self.name,
                                'is_company': True,
                                'active': True,
                                'customer': True,
                                'supplier': True,
                                'employee': False,
                                })

            self.partner_id = partner_id.id

    
    def write(self, vals):
        res = super(SimPinMitraBank, self).write(vals)
        return res
    
    
    def action_bank_approve(self):
        for line in self.product_lines:
            if line.state=='submit':
                line.action_bank_approve()

    def get_data_angsuran(self,ld_data):
        periode = ld_data.periode_angsuran
        angsuran = ld_data.total_angsuran
        if ld_data.tanggal_akad:
            bulan = ld_data.tanggal_akad
        else:
            bulan = date.today()
        pokok_pinjaman = ld_data.total_pembiayaan
        angsuran_margin = pokok_pinjaman * (ld_data.margin/1200)
        angsuran_pokok = angsuran - angsuran_margin
        result = []
        for i in range(1,periode+1):
            isi_data ={}
            bulan += relativedelta(months=1)
            if i==1:
                pokok_pinjaman = ld_data.total_pembiayaan
                angsuran_margin = pokok_pinjaman * (ld_data.margin/1200)
                angsuran_pokok = angsuran - angsuran_margin
            else:
                pokok_pinjaman -= angsuran_pokok
                angsuran_margin = pokok_pinjaman * (ld_data.margin/1200)
                angsuran_pokok = angsuran - angsuran_margin

            isi_data['no'] = i
            isi_data['periode'] = datetime.strftime(bulan,'%B %Y')
            isi_data['pokok_pinjaman'] = round(pokok_pinjaman,0)
            isi_data['angsuran_pokok'] = round(angsuran_pokok,0)
            isi_data['angsuran_margin'] = round(angsuran_margin,0)
            isi_data['angsuran_bulanan'] = round(angsuran,0)
        
            result.append(isi_data)
        return result  

    
    def action_cron_create_vb(self):
        mitra_bank = self.env['simpin_syariah.mitra.bank'].search([('bank_id','!=',False)])
        if mitra_bank:
            for rec in mitra_bank:
                rec.action_create_bill()

    
    def action_update_bill(self):
        for rec in self:
            for line in rec.ld_lines:
                for inv in line.invoice_lines:
                    angsuran = amount = False
                    for inv_line in inv.invoice_line_ids:
                        angsuran = inv_line.name.find('Angsuran')
                        margin = inv_line.name.find('Margin')
                        if angsuran>=0:
                            inv_line.update({'account_id': rec.hpp_pokok.id})
                            inv.move_id.update({'state': 'draft'})
                            for aml in inv.move_id.line_ids:
                                angs_aml = aml.name.find('Angsuran')
                                if angs_aml>=0 and aml.debit>0:
                                    aml.update({'account_id': rec.hpp_pokok.id})
                            inv.move_id.update({'state': 'posted'})
                        elif margin>=0:
                            amount = inv_line.price_subtotal
                                    
                    payment = self.env['account.payment'].search([('invoice_ids','=',inv.id)])
                    payment_move = False
                    if payment:
                        payment_move = payment.move_line_ids[0].move_id
                        payment_aml =  payment.move_line_ids[0]
                        aml = self._prepare_move_line_syariah(rec.hpp_account,amount,0,payment_aml,rec)
                        aml = self._prepare_move_line_syariah(rec.mydt_account,0,amount,payment_aml,rec)

                        cek = []
                        for line in payment_move.line_ids:
                            cek.append({'COA': line.account_id.name,
                                        'debit': line.debit,
                                        'credit': line.credit,
                                        'debit_cash_basis': line.debit_cash_basis,
                                        'credit_cash_basis': line.credit_cash_basis,
                                        'balance_cash_basis': line.balance_cash_basis,
                                        'currency_id': line.currency_id.id,})

#                    raise UserError(_('payment %s')%(cek,))

    def _prepare_move_line_syariah(self,coa,xdebit,xcredit,aml,rec):
        csql = """ 
                INSERT INTO account_move_line (name,quantity,debit,credit,balance,
                debit_cash_basis,credit_cash_basis,balance_cash_basis,
                account_id,move_id,ref,payment_id,journal_id,date_maturity,date,analytic_account_id,
                company_id,partner_id,user_type_id,  
                create_uid,create_date, write_uid,
                write_date, amount_residual,
                amount_currency, amount_residual_currency,blocked,company_currency_id) 
                VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,0,0,0,false)
                """
        self.env.cr.execute(csql, (coa.name,1,xdebit,xcredit,
                                xdebit-xcredit,xdebit,xcredit,xdebit-xcredit,
                                coa.id,aml.move_id.id,aml.ref,aml.payment_id.id,aml.journal_id.id,
                                aml.move_id.date,aml.move_id.date,rec.account_analytic_id.id,aml.company_id.id,
                                aml.partner_id.id,coa.user_type_id.id,aml.move_id.create_uid.id,aml.move_id.create_date,
                                aml.move_id.write_uid.id,aml.move_id.write_date,self.currency_id.id))
        return True

    
    def action_create_bill(self):
        invoice_lines = []
        loan_id = coa_hpp = name_hpp = False
        date_today = datetime.strptime('2021-09-25','%Y-%m-%d') #date.today() # 
        for line in self.ld_lines:
            if line.state=='running' and line.saldo==0:
                line.write({'state': 'close'})
            elif line.total_pembiayaan==0 and line.total_angsuran==0:
                line.write({'state': 'close'})
            elif line.state=='running' and line.saldo>0:
                tgl_inv = False
                jml_bulan = relativedelta(date_today,line.tanggal_akad)
                last_invoice = self.env['account.invoice'].search([('type_journal','=','Bill LD'),
                                                                    ('type','=','in_invoice'),
                                                                    ('loan_id','=',line.id),('date_invoice','<=',date_today),
                                                                    ('state','in',['open','paid'])],
                                                                    order='date_invoice desc',limit=1)
                if last_invoice and last_invoice.date_invoice<=line.jatuh_tempo and jml_bulan.months>0:
                    tgl_inv = last_invoice.date_invoice + relativedelta(months=1)
                    jml_bulan = relativedelta(tgl_inv,line.tanggal_akad)
                    bln = (jml_bulan.years*12)+jml_bulan.months-1
#                    raise UserError(_('Create Vendor Bill %s')%(tgl_inv,))
                elif not last_invoice and jml_bulan.months>0:
                    day_diff = date_today.day - line.tanggal_akad.day
                    tgl_inv = date_today-relativedelta(days=day_diff)
                    bln = (jml_bulan.years*12)+jml_bulan.months

                data_angsuran = self.get_data_angsuran(line)

#                raise UserError(_('tgl %s \n %s == %s \n inv %s')%(line.name,tgl_inv,line.jatuh_tempo.strftime("%Y-%m-%d"), last_invoice.date_invoice))
                if tgl_inv and line.periode_angsuran>bln and tgl_inv.strftime("%Y-%m-%d")<=line.jatuh_tempo.strftime("%Y-%m-%d"):
                    loan_id = line.id
                    product_grouped = {}
                    pembiayaan = self.env['simpin_syariah.pembiayaan'].search([('loan_id','=',line.id)],order='product_id')
                    for biaya in pembiayaan:
                        val = {'product_id': biaya.product_id.id, 'amount': biaya.total_pembiayaan}
                        key = biaya.product_id.id
                        if key not in product_grouped:
                            product_grouped[key] = val
                        else:
                            product_grouped[key]['amount'] += val['amount']
#                   raise UserError(_('product_grouped %s')%(product_grouped,))

                    coa_pokok = self.hpp_pokok
                    name_pokok = coa_pokok.name + ' ' + line.name.upper()
                    invoice_lines = [(0, 0, self.prepare_inv_line(line,data_angsuran[bln]['angsuran_pokok'],tgl_inv,coa_pokok.id,name_pokok))]
                    coa_margin = self.hpp_margin
                    name_margin = coa_margin.name + ' ' + line.name.upper()
                    invoice_lines += [(0, 0, self.prepare_inv_line(line,data_angsuran[bln]['angsuran_margin'],tgl_inv,coa_margin.id,name_margin))]
                    inv_vals = {
                                'date_invoice': tgl_inv.strftime("%Y-%m-%d"),
                                'name': 'Angsuran Pembiayaan ' + line.name.upper() + ': ' + tgl_inv.strftime("%B %Y"),
                                'type': 'in_invoice',
                                'reference': self.bank_id.name + ': ' + line.name,
                                'origin': self.bank_id.name + ': ' + line.name,
                                'account_id': self.journal_id.default_debit_account_id.id,
                                'partner_id': self.partner_id.id,
                                'invoice_line_ids': invoice_lines,
                                'currency_id': self.currency_id.id,
                                'comment': 'Angsuran Pembiayaan' + line.name.upper() + ': ' + tgl_inv.strftime("%B %Y"),
                                'payment_term_id': 1,
                                'mitra_bank_id': self.id,
                                'loan_id': loan_id,
                                'type_journal': 'Bill LD',
                                'operating_unit_id': self.env.user.default_operating_unit_id.id,
                                }
                    raise UserError(_('Create Vendor Bill %s ')%(inv_vals,))
                    invoice = self.env['account.invoice'].create(inv_vals)
                    invoice.action_invoice_open_syariah()
                    move_line = self.env['account.move.line'].search([('move_id','=',invoice.move_id.id)])
                    for mline in move_line:
                        mline.analytic_account_id = line.account_analytic_id.id


    def prepare_inv_line(self, line, amount=False,tanggal=False,coa=False,name=False):
        '''
        This function prepares move line of account.move related to an cash_advance
        '''
        if not name:
            name = 'Angsuran ' + line.name.upper()

        if not amount:
            amount = line.total_angsuran

        if not coa:
            coa = line.credit_account.id
            
        return {
                'name': name + ' ' + tanggal.strftime("%B %Y") ,
                'origin': name + ' ' + tanggal.strftime("%B %Y"),
                'account_id': coa,
                'price_unit': amount,
                'quantity': 1.0,
                'discount': 0.0,
                'product_id': line.product_id.id,
                'account_analytic_id': line.account_analytic_id.id or False,
                'operating_unit_id': self.env.user.default_operating_unit_id.id,
                }
    
class MitraBankBiaya(models.Model):
    _name = "mitra_bank.biaya"
    _description = "Komponen Biaya Bank Simpin Syariah"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "tipe"

    name = fields.Char(string='Deskripsi', default=lambda self: _('Administrasi'))
    mitra_bank_id = fields.Many2one('simpin_syariah.mitra.bank',string='Mitra Bank')
    product_tmpl_id = fields.Many2one('product.template',string='Product Template')
    product_id = fields.Many2one('product.product',string='Product')
    nilai_pct = fields.Float(default=0.0, string='Pct (%)')
    nominal = fields.Float(default=0.0, string='Nominal')
    coa_debit = fields.Many2one('account.account', required=False,string='Debet Account')
    coa_credit = fields.Many2one('account.account',required=False,string='Kredit Account')
    is_edit = fields.Boolean(string='Editable', default=False)
    is_bill = fields.Boolean(string='Billable', default=False)
    tipe = fields.Selection([
        ('adum', 'Administrasi'),
        ('notaris', 'Biaya Notaris'),
        ('asuransi', 'Biaya Asuransi'),
        ('transfer', 'Biaya Transfer Bank'),
        ('transfer_anggota', 'Biaya Transfer Anggota'),
        ('uangmuka', 'Uang Muka'),
        ('potongan', 'Potongan / Diskon'),
        ('lain', 'Lainnya'),
        ], string='Type', copy=False, index=True, default='adum',required=True)



        
