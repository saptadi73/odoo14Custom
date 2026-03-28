# -*- coding: utf-8 -*-
# Part of Akun+. See LICENSE file for full copyright and licensing details.

from datetime import datetime, timedelta, date
from functools import partial
from itertools import groupby

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.misc import formatLang
from odoo.osv import expression
from odoo.tools import float_is_zero, float_compare
from dateutil.relativedelta import relativedelta

from werkzeug.urls import url_encode

class AccountMove(models.Model):
    _inherit = 'account.move'

    investasi_id = fields.Many2one('simpin_syariah.investasi', string='Investasi')

    @api.depends(
        'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual',
        'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual_currency',
        'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual',
        'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual_currency',
        'line_ids.debit',
        'line_ids.credit',
        'line_ids.currency_id',
        'line_ids.amount_currency',
        'line_ids.amount_residual',
        'line_ids.amount_residual_currency',
        'line_ids.payment_id.state',
        'line_ids.full_reconcile_id')
    def _compute_amount(self):
        res = super(AccountMove, self)._compute_amount()
        for move in self :
            print ("=============amount============", move.payment_state)
            if move.payment_state == 'paid' :
                if move.investasi_id:
                    if move.move_type == 'out_invoice' :
                        print ("=============paid===============")
                        move.investasi_id.write({'state': 'active'})
                        print ("============close=======")
        return res

class SimPinInvestasi(models.Model):
    _name = "simpin_syariah.investasi.line"
    _description = "Pembayaran Investasi Anggota Simpin Syariah"

    name = fields.Char(string='Deskripsi',store=True)
    investasi_id = fields.Many2one('simpin_syariah.investasi',string='Investasi',store=True)
    invoice_id = fields.Many2one('account.move',string='No. Invoice')
    tanggal_proses = fields.Date(string='Tanggal Proses',store=True)
    # state = fields.Selection([
    #     ('open', 'Open'),
    #     ('paid', 'Paid'),
    #     ], string='Status', copy=False, index=True, related='invoice_id.state',store=True)
    state = fields.Selection([
        ('open', 'Open'),
        ('paid', 'Paid'),
        ], string='Status', copy=False, index=True)

    
class SimPinInvestasi(models.Model):
    _name = "simpin_syariah.investasi"
    _description = "Investasi Anggota Simpin Syariah"
    _inherit = ['mail.thread', 'mail.activity.mixin']


    
    @api.depends('transaction_lines.balance')
    def _compute_amount(self):
        self.balance = sum(line.debit - line.credit for line in self.transaction_lines)

    @api.model
    def _default_currency(self):
        return self.env.user.company_id.currency_id.id

    name = fields.Char(string='Nomor Sertifikat')
    member_id = fields.Many2one('simpin_syariah.member',string='Nama Anggota', required=True,
                                 domain=[('state', '=', 'done')])
    akad_id = fields.Many2one('master.akad_syariah',string='Jenis Akad', required=True,
                              domain=[('is_actived', '=', True),
                                      '|',('category_id.parent_id.name', '=', 'Investasi'),
                                      ('category_id.name', '=', 'Investasi')])
    product_id = fields.Many2one('product.product',string='Produk', required=True,
                                 domain=[('is_syariah', '=', True),
                                         '|',('product_tmpl_id.categ_id.parent_id.name', '=', 'Investasi'),
                                         ('product_tmpl_id.categ_id.name', '=', 'Investasi')])
    currency_id = fields.Many2one('res.currency', string="Currency", default=_default_currency)
    account_analytic_id = fields.Many2one('account.analytic.account', required=True, string='Analytic Account')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submit', 'Submitted'),
        ('check', 'Check Document'),
        ('approve', 'Approved'),
        ('active', 'Active'),
        ('close', 'Closed'),
        ('block', 'Blocked'),
        ], string='Status', copy=False, index=True, default='draft', track_visibility='onchange', readonly=True)
    paket_investasi = fields.Selection([
        ('25000000', '25.000.000,-'),
        ('50000000', '50.000.000,-'),
        ('100000000', '100.000.000,-'),
        ('250000000', '250.000.000,-'),
        ], string='Paket Investasi', copy=False, index=True, default='25000000', track_visibility='onchange')
    qty_investasi = fields.Integer(string="Quantity", default=1)
    total_investasi = fields.Monetary(string='Total Investasi',currency_field='currency_id',compute='_compute_total_invest',track_visibility='onchange', store=True)
    jangka_waktu = fields.Selection([
        ('1', '1 Bulan'),
        ('3', '3 Bulan'),
        ('6', '6 Bulan'),
        ('12','12 Bulan'),
        ('24','24 Bulan'),
        ('36','36 Bulan'),
        ], string='Jangka Waktu', copy=False, index=True, default='1', track_visibility='onchange',required=True)
    tanggal_akad = fields.Date(string='Tanggal Akad', default=date.today())
    jatuh_tempo = fields.Date(string='Jatuh Tempo',compute='_compute_jatuh_tempo',store=True)
    pengembalian  = fields.Selection([
        ('aro', 'Automatic Roll Over (ARO)'),
        ('jatuh_tempo', 'Jatuh Tempo'),
        ], string='Pengembalian', copy=False, index=True, default='aro', track_visibility='onchange')
    nisbah_investor = fields.Float(string='Nisbah Investor',default=25, required=True)
    pajak_nisbah = fields.Many2one('account.tax', string='Pajak', required=True, domain=[('type_tax_use','!=','none'),('active', '=', True)])
    ahli_waris_id = fields.Many2one('simpin_syariah.member.waris',string='Ahli Waris', track_visibility='onchange')
    equivalent_rate = fields.Float(string='Equivalent Rate',digits=(4,6),default=8.6, required=True, track_visibility='onchange')
    bank_id = fields.Many2one('res.bank','Bank',help='Nama Bank Penerima', track_visibility='onchange')
    bank_norek = fields.Char('Account #',help='No Rekening Penerima', track_visibility='onchange')
    bank_namarek = fields.Char('Beneficiary',help='Nama Pada Rekening', track_visibility='onchange')
    journal_id = fields.Many2one('account.journal', string='Journal', related='akad_id.journal_id')
    setoran_investasi = fields.Many2one('account.payment', string='Setoran')
    investasi_line = fields.One2many('simpin_syariah.investasi.line','investasi_id',string='Pembayaran', copy=False, store=True)
    pembayaran_nisbah = fields.Selection([
        ('1', 'Setiap Bulan'),
        ('2', 'Jatuh Tempo'),
        ], string='Pembayaran Nisbah', copy=False, index=True, default='1', track_visibility='onchange')
    mitra_id = fields.Many2one('simpin_syariah.mitra', string='Mitra Kerja', related='member_id.mitra_id',store=True)

    
    @api.depends('paket_investasi','qty_investasi')
    def _compute_total_invest(self):
        self.total_investasi = self.paket_investasi * self.qty_investasi
        self.mitra_id = self.member_id.mitra_id.id

    
    @api.depends('jangka_waktu','tanggal_akad')
    def _compute_jatuh_tempo(self):
#        if self.tanggal_akad < date.today():
#            self.tanggal_akad=date.today()
        jangka_waktu = int(self.jangka_waktu)
        self.jatuh_tempo = self.tanggal_akad + relativedelta(months=jangka_waktu)
        

    
#    
    @api.onchange('member_id')
    def _onchange_member_id(self):
        t_domain = False
        if self.member_id:
            ahli_waris = self.env['simpin_syariah.member.waris'].search([
                                                      ('member_id', '=', self.member_id.id),
                                                          ])
            t_domain = {'domain': {'ahli_waris_id': [('id', 'in', ahli_waris.ids)]}}
        self.mitra_id = self.member_id.mitra_id.id
        return t_domain

#    
    @api.onchange('akad_id')
    def _onchange_akad_id(self):
        t_domain = False
#        if self.akad_id:
#            product = self.env['product.product'].search([('is_syariah', '=', True),('active', '=', True),
#                                                      ('jenis_syariah', '=', self.akad_id.id),
#                                                          ])
#        else:
#            product = self.env['product.product'].search([('is_syariah', '=', True),('active', '=', True),
#                                                      '|',('product_tmpl_id.categ_id.parent_id.name', '=', 'Investasi'),
#                                                      ('product_tmpl_id.categ_id.name', '=', 'Investasi')
#                                                          ])
#        raise UserError(_('CP product %s\n len(product) %s')%(product,len(product),))
#        if len(product)>0:
#            t_domain = {'domain': {'product_id': [('id', 'in', product.ids)]}}
#        else:
#            self.product_id = False
        return t_domain

    @api.onchange('product_id')
    def _onchange_product_id(self):
        t_domain = False
        if self.product_id:
            akad = self.env['master.akad_syariah'].search([('id', '=', self.product_id.product_tmpl_id.jenis_syariah.id)])
        else:
            akad = self.env['master.akad_syariah'].search([('category_id.name','=','Investasi'),('is_actived','=',True)])
            
        t_domain = {'domain': {'akad_id': [('id', 'in', akad.ids)]}}
        self.akad_id = False
        return t_domain


    @api.model
    def create(self, vals):
        ak_id = self.env['master.akad_syariah'].search([('id','=',vals.get('akad_id'))])
        akad_id = ak_id.name + " sequence"
        rekno = self.env['ir.sequence'].next_by_code(akad_id)
        if not rekno:
            cr_seq = self.env['ir.sequence'].create({
                            'name': ak_id.name,
                            'code': akad_id,
                            'implementation': 'standard',
                            'active': True,
                            'prefix': ak_id.kode + '/%(year)s/%(month)s/',
                            'padding': 5,
                            'company_id': self.env.user.company_id.id,
                            'use_date_range': False,
                            })
            if cr_seq:
                rekno = self.env['ir.sequence'].next_by_code(akad_id)
            else:
                raise UserError('Sequence Error')
        vals['name'] = rekno
        akad = super(SimPinInvestasi, self).create(vals)

        return akad


    
    def action_break(self):
        inv_line =[]
        jml_bulan = 0.0
        coa_debit = self.journal_id.default_debit_account_id
        coa_credit = self.journal_id.default_credit_account_id
        nisbah_bulanan = round(self.total_investasi * self.equivalent_rate / 1200,0)
        dt_nisbah = self.env['master.akad_journal'].search([('akad_id','=',self.akad_id.id),('type_journal','=','bayar_untung')],limit=1)
        dt_pokok = self.env['master.akad_journal'].search([('akad_id','=',self.akad_id.id),('type_journal','=','balik_modal')])
            
        if self.state=='active':
            if self.pembayaran_nisbah==2: # and date.today()==self.jatuh_tempo:
                jml = relativedelta(date.today(),self.tanggal_akad)
                jml_bulan = jml.years*12 + jml.months
                nisbah = nisbah_bulanan * jml_bulan
                inv_line += [(0,0,self._prepare_inv_line_nisbah('Pembayaran Nisbah ',dt_nisbah.coa_kredit.id,nisbah,1,self.pajak_nisbah))]
                inv_line += [(0,0,self._prepare_inv_line_nisbah('Pengembalian Dana Investasi ',dt_pokok.coa_debet.id,self.paket_investasi,self.qty_investasi))]
                inv_name = "Pencairan Investasi dan Nisbah: " + self.name + " an " + self.member_id.name
            elif self.pembayaran_nisbah==1:
                nisbah = nisbah_bulanan
#                inv_line += [(0,0,self._prepare_inv_line_nisbah('Pembayaran Nisbah ',dt_nisbah.coa_kredit.id,nisbah,1,self.pajak_nisbah))]
                inv_line += [(0,0,self._prepare_inv_line_nisbah('Pengembalian Dana Investasi ',dt_pokok.coa_debet.id,self.paket_investasi,self.qty_investasi))]
                inv_name = "Pencairan Investasi dan Nisbah: " + self.name + " an " + self.member_id.name

#        raise UserError(_('jatuh_tempo %s - %s \n %s')%(self.pengembalian, jml_bulan, inv_line,))
        invoice = self.env['account.invoice'].create({
                        'date_invoice': date.today(),
                        'name': inv_name,
                        'origin': self.name,
                        'type': 'in_invoice',
                        'reference': self.name,
                        'account_id': dt_pokok.coa_kredit.id,
                        'partner_id': self.member_id.partner_id.id,
                        'invoice_line_ids': inv_line,
                        'currency_id': self.currency_id.id,
                        'comment': inv_name,
                        'payment_term_id': 1,
                        'investasi_id': self.id,
                        'type_journal': 'nisbah',
                        'operating_unit_id': self.env.user.default_operating_unit_id.id,
                    })
        
        invoice.action_invoice_open_syariah()   ##invoice.post harus ke syariah

        self.env['simpin_syariah.investasi.line'].create({
                                                    'name': inv_name,
                                                    'investasi_id': self.id,
                                                    'invoice_id': invoice.id,
                                                    'tanggal_proses': invoice.date,
                                                    })

        total = invoice.amount_total

        invoice.update({
                        'residual': total,
                        'residual_signed': total,
                        'residual_company_signed': total,
                        })

        self.write({'state': 'close'})

        return invoice

    
    def action_submit(self):
        self.write({'state': 'submit'})

    
    def action_check(self):
        self.write({'state': 'check'})

    def create_invoice(self):
        for trans in self:
            invoice_vals_list =[]
            if trans.product_id :
                if not trans.product_id.property_account_income_id:
                    raise UserError(_('You must add Income Account Product %s.')%(trans.product_id.name))
            
                invoice_vals = {
                                    'product_id': trans.product_id.id,
                                    'name': trans.product_id.name,
                                    'account_id': trans.product_id.property_account_income_id.id,
                                    'quantity': 1,
                                    'price_unit': trans.total_investasi
                                    }                  


                invoice_vals_list.append(invoice_vals)

            sim_name = 'Investasi : ' + trans.name + " - " + trans.member_id.name
            invoice_vals = {
                            'partner_id': trans.member_id.partner_id.id,
                            'state': 'draft',
                            'payment_reference':sim_name,
                            'move_type': 'out_invoice',
                            'investasi_id' : trans.id,
                            'journal_id' : trans.journal_id.id,
                            'invoice_line_ids': invoice_vals_list
                            }
            invoice = self.env['account.move'].sudo().create(invoice_vals)
            movelines = self.env['account.move.line'].search([('move_id','=',invoice.id),('account_id.code','=','11210010')])
            if movelines:
                movelines.write({'account_id' : trans.akad_id.property_account_receivable_id.id}) 
            invoice.action_post()

    
    def action_approve(self):
        self.create_invoice()
        self.write({'state': 'approve'})

    def _prepare_inv_line(self,coa):
        '''
        This function prepares move line of account.move related to an cash_advance
        '''
        return {
                'name': "Setoran Investasi : " + self.name,
                'origin': self.name,
                'account_id': coa,
                'price_unit': self.paket_investasi,
                'quantity': self.qty_investasi,
                'discount': 0.0,
                'partner_id': self.member_id.partner_id.id,
                'product_id': self.product_id.id,
                'account_analytic_id': self.account_analytic_id.id or False,
                'operating_unit_id': self.env.user.default_operating_unit_id.id,
                }

    def _prepare_inv_line_nisbah(self,name,coa,price,qty,tax=False):
        '''
        This function prepares move line of account.move related to an cash_advance
        '''
        limit_pajak = self.env['master.general'].search([('type_umum','=','nisbah')],limit=1)
        if tax and limit_pajak and price*qty>limit_pajak.nominal:
            line_tax = [(6,0,{self.pajak_nisbah.id})]
        else:
            line_tax = False
                
        return {
                'name': name,
                'account_id': coa,
                'price_unit': price,
                'quantity': qty,
                'discount': 0.0,
                'product_id': self.product_id.id,
                }

    
    def action_active(self):
        raise UserError(_('submodul Active'))
        self.write({'state': 'active'})

    
    def action_close(self):
        raise UserError(_('submodul Close'))
        self.write({'state': 'close'})

    
    def action_block(self):
        raise UserError(_('submodul Block'))
        self.write({'state': 'block'})


    def action_aro_jatem(self):
        investasi = self.env['simpin_syariah.investasi'].search([('state','=','active')])
#        for invest in investasi:
        last_invoice = self.env['account.invoice'].search([('investasi_id','=',self.id),
                                                           ('state','in',['open','paid']),
                                                           ('type','=','in_invoice')],order="id desc",limit=1)
                                                                   
#        if not last_invoice and invest.jatuh_tempo.day<=date.today().day:
#            new_invoice = invest.create_inv_nisbah()
#                raise UserError(_('new invoice %s')%(new_invoice.date_invoice))

        if (last_invoice and last_invoice.date_invoice.month<date.today().month) or not last_invoice:
            if self.state=='active' and date.today().day>=self.jatuh_tempo.day:
                self.create_inv_nisbah()
            else:
                raise UserError(_('Belum jatuh tempo %s')%(self.jatuh_tempo))
        else:
            raise UserError(_('Belum jatuh tempo atau sudah dibuatkan Nisbah - %s')%(self.jatuh_tempo))


    def create_inv_nisbah_daily(self):
        investasi = self.env['simpin_syariah.investasi'].search([('state','=','active')])
        if investasi:
            for line in investasi:
                last_invoice = self.env['account.invoice'].search([('investasi_id','=',line.id),
                                                                   ('state','in',['open','paid']),
                                                                   ('type','=','in_invoice')],order="id desc",limit=1)
                                                                   
                datediff = relativedelta(date.today(),last_invoice.date_invoice)
                if (last_invoice and datediff.months>0) or not last_invoice:
                    akad_diff = relativedelta(date.today(),line.tanggal_akad)
                    if line.state=='active' and date.today().day==1 and line.tanggal_akad.day>(date.today() - relativedelta(days=1)).day:
#                        raise UserError(_('investasi %s - %s -%s')%(line.id,(date.today() - relativedelta(days=1)).day,line.tanggal_akad,))
                        line.create_inv_nisbah(date.today() - relativedelta(days=1))
                    elif line.state=='active' and date.today().day==line.tanggal_akad.day:
#                        raise UserError(_('investasi %s - %s -%s')%(line.id,(date_today - relativedelta(days=1)).day,line.tanggal_akad,))
                        line.create_inv_nisbah()
            
    
    def create_inv_nisbah(self,tanggal=False):
        tgl_akad = self.tanggal_akad
        inv_cair = len(self.investasi_line)
        akad_date = tgl_akad + relativedelta(months=inv_cair) 
        date_today = akad_date.strftime("%Y-%m-01") 
        if tanggal:
            date_today = tanggal
        inv_line =[]
        coa_debit = self.product_id.property_account_expense_id.id
        coa_credit = self.akad_id.property_account_payable_id.id
        nisbah_bulanan = round(self.total_investasi * self.equivalent_rate / 1200,0)
        dt_nisbah = self.env['master.akad_journal'].search([('akad_id','=',self.akad_id.id),('type_journal','=','bayar_untung')],limit=1)
        dt_pokok = self.env['master.akad_journal'].search([('akad_id','=',self.akad_id.id),('type_journal','=','balik_modal')], limit=1)
            
        if self.pengembalian=='jatuh_tempo' and self.state=='active':
            if self.pembayaran_nisbah==2 and date_today==self.jatuh_tempo:
                nisbah = nisbah_bulanan * int(self.jangka_waktu)
                inv_line += [(0,0,self._prepare_inv_line_nisbah('Pembayaran Nisbah ',dt_nisbah.coa_kredit.id,nisbah,1,self.pajak_nisbah))]
                inv_line += [(0,0,self._prepare_inv_line_nisbah('Pengembalian Dana Investasi ',dt_pokok.coa_debet.id,self.paket_investasi,self.qty_investasi))]
                inv_name = "Pencairan Investasi dan Nisbah: " + self.name + " an " + self.member_id.name
            elif self.pembayaran_nisbah==1  and date_today==self.jatuh_tempo:
                nisbah = nisbah_bulanan
                inv_line += [(0,0,self._prepare_inv_line_nisbah('Pembayaran Nisbah ',dt_nisbah.coa_kredit.id,nisbah,1,self.pajak_nisbah))]
                inv_line += [(0,0,self._prepare_inv_line_nisbah('Pengembalian Dana Investasi ',dt_pokok.coa_debet.id,self.paket_investasi,self.qty_investasi))]
                inv_name = "Pencairan Investasi dan Nisbah: " + self.name + " an " + self.member_id.name
#            elif self.pembayaran_nisbah==1 and relativedelta(date.today(),self.jatuh_tempo).months>0:
#                nisbah = nisbah_bulanan
#                inv_line += [(0,0,self._prepare_inv_line_nisbah('Pembayaran Nisbah ',dt_nisbah.coa_kredit.id,nisbah,1,self.pajak_nisbah))]
#                inv_name = "Pencairan Nisbah: " + self.name + " an " + self.member_id.name
            else:
                raise UserError('Belum Jatuh Tempo')
        elif self.pengembalian=='aro' and self.state=='active':
            if self.pembayaran_nisbah=='1':
                nisbah = nisbah_bulanan
                print ("==========aro===========", nisbah)
                #create VB nisbah dan extend jatuh_tempo sesuai jangka_waktu
                #jurnal nisbah
            else:
                nisbah = nisbah_bulanan * int(self.jangka_waktu)

            inv_line += [(0,0,self._prepare_inv_line_nisbah('Pembayaran Nisbah ',dt_nisbah.coa_kredit.id,nisbah,1,self.pajak_nisbah))]
            inv_name = "Nisbah Investasi ARO: " + self.name + " an " + self.member_id.name

        else:
            print ("===========else===========")
            raise UserError(_('Data Investasi tidak lengkap %s')%(self.id))
            


        invoice_vals = {
                            'partner_id': self.member_id.partner_id.id,
                            'state': 'draft',
                            'ref': self.name,
                            'invoice_date': date_today,
                            'move_type': 'in_invoice',
                            'investasi_id' : self.id,
                            'invoice_line_ids': inv_line
                        }

        invoice = self.env['account.move'].create(invoice_vals)

        self.env['simpin_syariah.investasi.line'].create({
                                                    'name': inv_name,
                                                    'investasi_id': self.id,
                                                    'invoice_id': invoice.id,
                                                    'tanggal_proses': invoice.date,
                                                    })

    def cron_create_inv_nisbah(self,tanggal=False):
        investasi = self.env['simpin_syariah.investasi'].search([('state','=', 'active')])
        for inves in investasi :
            tgl_akad = inves.tanggal_akad
            inv_cair = len(inves.investasi_line)
            akad_date = tgl_akad + relativedelta(months=inv_cair) 
            date_today = akad_date.strftime("%Y-%m-01") 
            if tanggal:
                date_today = tanggal
            inv_line =[]
            coa_debit = inves.product_id.property_account_expense_id.id
            coa_credit = inves.akad_id.property_account_payable_id.id
            nisbah_bulanan = round(inves.total_investasi * inves.equivalent_rate / 1200,0)
            dt_nisbah = self.env['master.akad_journal'].search([('akad_id','=',inves.akad_id.id),('type_journal','=','bayar_untung')],limit=1)
            dt_pokok = self.env['master.akad_journal'].search([('akad_id','=',inves.akad_id.id),('type_journal','=','balik_modal')], limit=1)
                
            if inves.pengembalian=='jatuh_tempo' and inves.state=='active':
                if inves.pembayaran_nisbah==2 and date_today==inves.jatuh_tempo:
                    nisbah = nisbah_bulanan * int(inves.jangka_waktu)
                    inv_line += [(0,0,inves._prepare_inv_line_nisbah('Pembayaran Nisbah ',dt_nisbah.coa_kredit.id,nisbah,1,inves.pajak_nisbah))]
                    inv_line += [(0,0,inves._prepare_inv_line_nisbah('Pengembalian Dana Investasi ',dt_pokok.coa_debet.id,inves.paket_investasi,inves.qty_investasi))]
                    inv_name = "Pencairan Investasi dan Nisbah: " + inves.name + " an " + inves.member_id.name
                elif inves.pembayaran_nisbah==1  and date_today==inves.jatuh_tempo:
                    nisbah = nisbah_bulanan
                    inv_line += [(0,0,inves._prepare_inv_line_nisbah('Pembayaran Nisbah ',dt_nisbah.coa_kredit.id,nisbah,1,inves.pajak_nisbah))]
                    inv_line += [(0,0,inves._prepare_inv_line_nisbah('Pengembalian Dana Investasi ',dt_pokok.coa_debet.id,inves.paket_investasi,inves.qty_investasi))]
                    inv_name = "Pencairan Investasi dan Nisbah: " + inves.name + " an " + inves.member_id.name
                else:
                    raise UserError('Belum Jatuh Tempo')
            elif inves.pengembalian=='aro' and inves.state=='active':
                if inves.pembayaran_nisbah=='1':
                    nisbah = nisbah_bulanan
                    print ("==========aro===========", nisbah)
                    #create VB nisbah dan extend jatuh_tempo sesuai jangka_waktu
                    #jurnal nisbah
                else:
                    nisbah = nisbah_bulanan * int(inves.jangka_waktu)

                inv_line += [(0,0,inves._prepare_inv_line_nisbah('Pembayaran Nisbah ',dt_nisbah.coa_kredit.id,nisbah,1,inves.pajak_nisbah))]
                inv_name = "Nisbah Investasi ARO: " + inves.name + " an " + inves.member_id.name

            else:
                print ("===========else===========")
                raise UserError(_('Data Investasi tidak lengkap %s')%(inves.id))
                


            invoice_vals = {
                                'partner_id': inves.member_id.partner_id.id,
                                'state': 'draft',
                                'ref': inves.name,
                                'invoice_date': date_today,
                                'move_type': 'in_invoice',
                                'investasi_id' : inves.id,
                                'invoice_line_ids': inv_line
                            }

            invoice = self.env['account.move'].create(invoice_vals)

            self.env['simpin_syariah.investasi.line'].create({
                                                        'name': inv_name,
                                                        'investasi_id': inves.id,
                                                        'invoice_id': invoice.id,
                                                        'tanggal_proses': invoice.date,
                                                        })


