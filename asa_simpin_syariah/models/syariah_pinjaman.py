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


class AccountMove(models.Model):
    _inherit = 'account.move'

    pinjaman_id = fields.Many2one('simpin_syariah.pinjaman', string='Simpanan')
    
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
                if move.pinjaman_id:
                    if move.move_type == 'in_invoice' :
                        print ("=============paid===============")
                        move.pinjaman_id.write({'state': 'active'})
                        move.pinjaman_id.create_invoice_angsuran()
                        print ("============close=======")
        return res


class SimPinPinjaman(models.Model):
    _name = "simpin_syariah.pinjaman"
    _description = "Pinjaman Anggota Simpin Syariah"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'resource.mixin']

    @api.depends('akad_id')
    def _cek_akad_kode(self):
        if self.akad_id:
            self.akad_kode = self.akad_id.kode


    @api.model
    def _default_currency(self):
        return self.env.user.company_id.currency_id.id

    name = fields.Char(string='Nomor Pinjaman',default='/')
    member_id = fields.Many2one('simpin_syariah.member',string='Nama Anggota', required=True,
                                 domain=[('state', '=', 'done')])
    akad_kode = fields.Char(string='Akad Code',compute='_cek_akad_kode',readonly=True, store=True)
    akad_id = fields.Many2one('master.akad_syariah',string='Jenis Akad', required=True,
                              readonly=True, states={'draft': [('readonly', False)]}, copy=False,track_visibility='onchange',
                              domain=[('is_actived', '=', True),
                                      '|',('category_id.parent_id.name', '=', 'Pinjaman'),
                                      ('category_id.name', '=', 'Pinjaman')])
    product_id = fields.Many2one('product.product',string='Produk', required=True,
                              readonly=True, states={'draft': [('readonly', False)]}, copy=False,track_visibility='onchange',
                                 domain=[('is_syariah', '=', True),
                                         '|',('product_tmpl_id.categ_id.parent_id.name', '=', 'Pinjaman'),
                                         ('product_tmpl_id.categ_id.name', '=', 'Pinjaman')])
    is_blokir = fields.Boolean('Blokir', default=False)
    currency_id = fields.Many2one('res.currency', string="Currency", readonly=True, default=_default_currency)
    balance = fields.Monetary(string='Balance',  store=True, currency_field='currency_id', compute='_compute_balance')
    tunggakan = fields.Monetary(string='Tunggakan', currency_field='currency_id', compute='_compute_balance',store=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submit', 'Submitted'),
        ('check', 'Check Document'),
        ('approve', 'Approved'),
        ('active', 'Active'),
        ('close', 'Closed'),
        ('block', 'Blocked'),
        ], string='Status', copy=False, index=True, default='draft', track_visibility='onchange', readonly=True)
    account_analytic_id = fields.Many2one('account.analytic.account', string='Analytic Account')
    peruntukan = fields.Many2one('master.general', string='Peruntukan', required=True,
                                     domain=[('type_umum', '=', 'peruntukan'),('akad_id', '=', False)], track_visibility='onchange')
    periode_angsuran = fields.Integer(string='Periode Angsuran', required=True, readonly=True,
                                      track_visibility='onchange', states={'draft': [('readonly', False)]}, default=12)
    angsuran = fields.Monetary(string='Angsuran',compute='_compute_angsuran',track_visibility='onchange',store=True)
    #invoice_lines = fields.One2many('account.invoice', 'pinjaman_id', string='Angsuran', copy=False, store=True, domain=[('type', '=', 'out_invoice')])
    tanggal_akad = fields.Date(string='Tanggal Akad', states={'approve': [('readonly', True)]}, index=True)
    nilai_pinjaman = fields.Monetary(string='Nilai Pinjaman',currency_field='currency_id',track_visibility='onchange',
                                     default=5000000,required=True)
    payment_id = fields.Many2one('account.payment', string='Pencairan')
    journal_id = fields.Many2one('account.journal', string='Journal', related='akad_id.journal_id')
    biaya_lines = fields.One2many('pinjaman.biaya', 'pinjaman_id',  string='Komponen Biaya')
    jumlah_biaya = fields.Monetary(string='Total Biaya', currency_field='currency_id', track_visibility='onchange')
    move_pencairan = fields.Many2one('account.move',readonly=True, store=True, string='Journal Pencairan')
    notes = fields.Text(string='Keterangan')
    src_bank_id = fields.Many2one('res.bank','Source Bank',help='Source Bank', track_visibility='onchange')
    src_bank_norek = fields.Char('Source Bank Account #',help='Source Bank Account', track_visibility='onchange')
    mitra_id = fields.Many2one('simpin_syariah.mitra', string='Mitra Kerja', related='member_id.mitra_id',store=True)

    ########## DOCUMENT PENDUKUNG ###########
    upload_ktp = fields.Binary(string="Upload KTP")
    file_ktp = fields.Char(string="File KTP")
    upload_ktp_pasangan = fields.Binary(string="Upload KTP Pasangan")
    file_ktp_pasangan = fields.Char(string="File KTP Pasangan")
    upload_kk = fields.Binary(string="Upload KK")
    file_kk = fields.Char(string="File KK")
    upload_npwp = fields.Binary(string="Upload NPWP")
    file_npwp = fields.Char(string="File NPWP")
    upload_slip1 = fields.Binary(string="Upload Slip Gaji #1")
    file_slip1 = fields.Char(string="File Slip Gaji #1")
    upload_slip2 = fields.Binary(string="Upload Slip Gaji #2")
    file_slip2 = fields.Char(string="File Slip Gaji #2")
    upload_slip3 = fields.Binary(string="Upload Slip Gaji #3")
    file_slip3 = fields.Char(string="File Slip Gaji #3")
    upload_dok_lain = fields.Binary(string="Upload Buku Tabungan")
    file_dok_lain = fields.Char(string="File Buku Tabungan")
    partner_id = fields.Many2one('res.partner', 'Customer')
    
    #@api.depends('invoice_lines')
    def _compute_balance(self):
        balance = self.nilai_pinjaman
        tunggakan = 0
        for line in self.invoice_lines:
            if line.state=='paid':
                balance-= line.amount_total
            else:
                tunggakan += line.amount_total

#        raise UserError(_('%s Balance %s - tunggakan %s')%(self.name,balance,tunggakan,))
        self.balance = balance
        self.tunggakan = tunggakan

    #@api.onchange('invoice_lines')
    def _onchange_invoice_lines(self):
        self._compute_balance


    @api.onchange('biaya_lines')
    def _onchange_biaya_lines(self):
        total = 0
        for line in self.biaya_lines:
            total += line.subtotal
        self.jumlah_biaya = total
        self._compute_angsuran()


    
    @api.depends('periode_angsuran','nilai_pinjaman','product_id','jumlah_biaya')
    def _compute_angsuran(self):
        margin = periode_max = nilai_max = nilai_min = periode_min = False
        
        if self.product_id and (self.state!='active' or self.state!='close'):
            for line in self.product_id.nisbah_lines:
                if not periode_max or line.periode_max>periode_max: 
                    periode_max = line.periode_max
                if not periode_min or line.periode_max<periode_min:
                    periode_min = line.periode_min

                if line.periode_max>=self.periode_angsuran:
                    nilai_max = line.nilai_max
                    nilai_min = line.nilai_min
                    break


            if nilai_min and self.nilai_pinjaman<nilai_min and self.state!='draft':
                self.nilai_pinjaman=nilai_min
                raise UserError(_('Nilai Pinjaman Minimal %s')%('{:,}'.format(nilai_min),))
            elif nilai_max and self.nilai_pinjaman>nilai_max:
                self.nilai_pinjaman=nilai_max
                raise UserError(_('Nilai Pinjaman melebihi Nilai Maksimal %s')%('{:,}'.format(nilai_max),))

            if self.periode_angsuran > periode_max:
                self.periode_angsuran = periode_max
                raise UserError(_('Periode melebihi maksimal %s bulan')%(periode_max,))
            elif self.periode_angsuran < periode_min and self.state!='draft':
                self.periode_angsuran = periode_min
                raise UserError(_('Periode minimal %s bulan')%(periode_min,))

            self.src_bank_id = self.product_id.sumber_dana.bank_id.id
            self.src_bank_norek = self.product_id.sumber_dana.bank_account_id.acc_number

#            raise UserError(_('CP nilai min %s \n nilai max %s \n periode min %s \n periode max %s')%(nilai_min, nilai_max, periode_min,periode_max,))

        currency = self.currency_id or None
        total = self.nilai_pinjaman

        if total>0:
            angsuran = (total + self.jumlah_biaya) / self.periode_angsuran           
            self.angsuran = round(angsuran,0)


    def get_data_simulasi(self):
        self.env.cr.execute("select id,name,periode_min,periode_max,nisbah,nilai_min,nilai_max from master_nisbah where product_tmpl_id=%s",(self.product_id.product_tmpl_id.id,))
        res = self.env.cr.dictfetchall()
        _res = []

        pj_line=len(res)
        baris = 1
        harga_beli = 0
        kelipatan = urutan = 1
        for line in res:
            nilai_max = int(round(line['nilai_max'] / 1000000,0))
            periode_max = int(round(line['periode_max'] / 12,0))
            for i in range(0,nilai_max):
                harga_beli2 = line['nilai_min'] + ( i * 1000000)

                if harga_beli2>harga_beli:
                    isi_data ={}
                    isi_data['0'] = 1
                    isi_data['1'] = 0
                    isi_data['2'] = 0
                    isi_data['3'] = 0
                    isi_data['4'] = 0
                    isi_data['5'] = 0
                    isi_data['6'] = 0
                    isi_data['7'] = 0
                    isi_data['8'] = 0
                    isi_data['9'] = 0
                    isi_data['10'] = 0
                    isi_data['11'] = 0
                    isi_data['12'] = 0

                    isi_data['0'] = str(baris)
                    no_kol = 1
                    harga_beli = harga_beli2
                    isi_data[str(no_kol)] = harga_beli
                    no_kol+=1
                
                    for xx in range(0,periode_max):
                        periode = line['periode_min'] + (xx*12)
#                       isi_data[str(no_kol)] = periode
#                       no_kol+=1
                        angsuran = round(self.calc_pmt(line['nisbah'],periode,harga_beli),0)
                        harga_jual = angsuran*periode
                        isi_data[str(no_kol)] = harga_jual
                        no_kol+=1
                        isi_data[str(no_kol)] = angsuran
                        no_kol+=1
                        if periode>line['periode_max']:
                            break

                    if urutan==kelipatan:
                        baris +=1
                        _res.append(isi_data)

                        urutan=1
                    else:
                        urutan+=1
                    
                if harga_beli>=100000000:
                    kelipatan = 50
                elif harga_beli>=50000000:
                    kelipatan = 5

                    
                if harga_beli>=line['nilai_max']:
                    break


#        raise UserError(_('CP %s')%(_res,))
        return _res

    
    def create_invoice_syariah_daily(self):
        pinjaman = self.env['simpin_syariah.pinjaman'].search([('state','=','active')])
        if pinjaman:
            for line in pinjaman:
                line._compute_balance()
                cur_periode = relativedelta(date.today(),line.tanggal_akad)
                cek_periode = cur_periode.years*12 + cur_periode.months
#                raise UserError(_('curperiode %s = %s')%(cek_periode,line.periode_angsuran))
                if cek_periode<line.periode_angsuran:
                    line.create_invoice_syariah()
                elif line.balance==0 and line.tunggakan==0:
                    line.write({'state': 'close'})

    
    def create_invoice_syariah(self):
        sale_order = self.env['sale.order'].search([('pinjaman_id','=',self.id)])
        inv_obj = self.env['account.invoice']
        is_tagih=True

        coa_debet = coa_credit = False
        invoice_lines = []
        akad_line = self.env['master.akad_journal'].search([('akad_id','=',self.akad_id.id),
                                                            ('type_journal','=','tagihan')])

        if akad_line and self.state=='active':
            coa_debit = self.journal_id.default_debit_account_id
            coa_credit = self.journal_id.default_credit_account_id
            for line in akad_line:
                if line.coa_debet:
#                    if lunas>0:
#                        coa_name = 'Pelunasan : ' + self.name + " - " + self.member_id.name
#                        invoice_lines += [(0, 0, self._prepare_inv_line(self,coa_name, line.coa_debet.id,pelunasan))]
#                    else:
                    coa_name = 'Angsuran : ' + self.name + " - " + self.member_id.name
                    invoice_lines += [(0, 0, self._prepare_inv_line(self,coa_name, line.coa_debet.id,self.angsuran))]

#            raise UserError(_('invoice_lines %s \n angsuran %s')%(invoice_lines, self.angsuran,))

            total_tagihan = 0
            last_invoice = self.env['account.invoice'].search([('pinjaman_id','=',self.id),
                                                               ('state','in',['open','paid']),
                                                               ('type','=','out_invoice'),],order="id desc")
            if last_invoice:
                for ll_inv in last_invoice:
                    total_tagihan += ll_inv.amount_total
            
                if self.tunggakan + self.balance <=self.nilai_pinjaman and relativedelta(date.today(),last_invoice[0].date_invoice).months>0:
                    tanggal_inv = last_invoice[0].date_invoice + relativedelta(months=1)
                else:
                    is_tagih = False

#                raise UserError(_('Total %s \n today-last = %s \n is_tagih %s ')%(self.tunggakan + self.balance <=self.nilai_pinjaman,relativedelta(date.today(),last_invoice[0].date_invoice).months>0,is_tagih,))
            else:
                tanggal_inv = self.tanggal_akad + relativedelta(months=1)

#            raise UserError(_('invoice_lines %s \n is_tagih %s \n tanggal %s')%(invoice_lines,is_tagih,tanggal_inv))

            if is_tagih:
                tanggal = relativedelta(date.today(),tanggal_inv)
                invoice = self.env['account.invoice'].create({
                    'date_invoice': tanggal_inv,
                    'name': self.name + " : " + self.member_id.name,
                    'origin': self.name,
                    'type': 'out_invoice',
                    'reference': self.name,
                    'account_id': coa_credit.id,
                    'partner_id': self.member_id.partner_id.id,
                    'invoice_line_ids': invoice_lines,
                    'currency_id': self.currency_id.id,
                    'comment': 'Angsuran ' + self.name + " : " + self.member_id.name,
                    'payment_term_id': 1,
                    'pinjaman_id': self.id,
                    'type_journal': 'tagihan',
                           'residual': self.angsuran,
                           'residual_signed': self.angsuran,
#                           'state': 'open',
                    })

                invoice.action_invoice_open_syariah()   ##invoice.post harus ke syariah

                invoice.message_post_with_view('mail.message_origin_link',
                                values={'self': invoice, 'origin': self},
                                subtype_id=self.env.ref('mail.mt_note').id)

                if sale_order.order_line:
                    for so_line in sale_order.order_line:
                        so_line.update({'invoice_lines': [(4,inv.id) for inv in invoice.invoice_line_ids]})
            else:
                self._compute_balance()

        return


    @api.model
    def create(self, vals):
        res = super(SimPinPinjaman, self).create(vals)
#        raise UserError(_('CP res %s')%(res,))
        return res

    
    def write(self, vals):
        res = super(SimPinPinjaman, self).write(vals)
#        raise UserError(_('CP res %s')%(res,))
        return res

    
    def action_blokir(self):
        raise UserError('Sub Modul Blokir Pinjaman')

    
    def action_pelunasan(self):
        self.create_invoice_syariah()
        self.update({'state': 'close'})


    
    def action_approve(self):
        ak_id = self.env['master.akad_syariah'].search([('id','=',self.akad_id.id)])
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

        if rekno:
            invoice = self.proses_pencairan(rekno)
            #self.create_invoice_angsuran(rekno)
            self.write({ 'state': 'approve',
                        'balance': self.nilai_pinjaman + self.jumlah_biaya,
                        'name': rekno,})

    def proses_pencairan(self,rekno):
        invoice_lines = inv_lines = []
        coa_debet = coa_credit = False
        if not self.journal_id.default_account_id: # or not self.journal_id.default_credit_account_id:
            raise UserError(_('Konfigurasi Journal belum Sesuai'))
        else:
            total = self.nilai_pinjaman
                
            coa_debit = self.product_id.property_account_expense_id.id
            coa_name = 'Pencairan : ' + rekno + " - " + self.member_id.name
            coa_credit = self.akad_id.property_account_payable_id.id
                
            invoice_vals_list =[]
            
            invoice_vals = {
                                'product_id': self.product_id.id,
                                'name': self.product_id.name,
                                'account_id': coa_debit,
                                'quantity': 1,
                                'price_unit': self.nilai_pinjaman
                                }
            # invoice_vals = {
            #                     'product_id': trans.product_id.id,
            #                     'name': trans.product_id.name,
            #                     'account_id': trans.akad_id.property_account_receivable_id.id,
            #                     'quantity': 1,
            #                     'price_unit': trans.product_id.minimal_setor
            #                 }                    


            invoice_vals_list.append(invoice_vals)


            invoice_vals = {
                            'partner_id': self.member_id.partner_id.id,
                            'state': 'draft',
                            'name': coa_name,
                            'ref': rekno,
                            'invoice_date': date.today(),
                            'move_type': 'in_invoice',
                            'pinjaman_id' : self.id,
                            'invoice_line_ids': invoice_vals_list
                            }
            invoice = self.env['account.move'].sudo().create(invoice_vals)
            movelines = self.env['account.move.line'].search([('move_id','=',invoice.id),('account_id.code','=','21100010')])
            if movelines:
                movelines.write({'account_id' : coa_credit}) 
            invoice.action_post()
            self.write({
                            'tanggal_akad': date.today(),
                            'move_pencairan': invoice.id,})

    @api.onchange('peruntukan')
    def _onchange_peruntukan(self):
        if self.peruntukan.akad_id:
            akad = self.env['master.akad_syariah'].search([('is_actived', '=', True),('id', '=', self.peruntukan.akad_id.id)])
        else:
            akad = self.env['master.akad_syariah'].search([('is_actived', '=', True),
                                                          '|',('category_id.parent_id.name', '=', 'Pinjaman'),
                                                          ('category_id.name', '=', 'Pinjaman')
                                                           ])
            

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id.product_tmpl_id.categ_id.parent_id.name == 'Pinjaman':
            akad = self.env['master.akad_syariah'].search([('is_actived', '=', True),('id', '=', self.product_id.jenis_syariah.id)])
            self.akad_id = self.product_id.jenis_syariah.id
        else:
            akad = self.env['master.akad_syariah'].search([('is_actived', '=', True),
                                                          '|',('category_id.parent_id.name', '=', 'Pinjaman'),
                                                          ('category_id.name', '=', 'Pinjaman')
                                                           ])
        self._compute_angsuran()
    
    
    def action_submit(self):
        self.write({'state': 'submit'})

    
    def action_check(self):
        self.write({'state': 'check'})

    
    def action_active(self):
        raise UserError('Sub Modul Pencairan Pinjaman')
        self.write({'state': 'active'})


    def create_invoice_angsuran(self):
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
                                    'price_unit': trans.angsuran
                                    }

                invoice_vals_list.append(invoice_vals)

            coa_name = 'Angsuran : ' + self.name + " - " + self.member_id.name
            invoice_vals = {
                            'partner_id': self.member_id.partner_id.id,
                            'state': 'draft',
                            'name': coa_name,
                            'ref': self.name,
                            'invoice_date': self.tanggal_akad,
                            'move_type': 'out_invoice',
                            'pinjaman_id' : self.id,
                            'invoice_line_ids': invoice_vals_list
                            }

            invoice = self.env['account.move'].sudo().create(invoice_vals)
            movelines = self.env['account.move.line'].search([('move_id','=',invoice.id),('account_id.code','=','11210010')])
            if movelines:
                movelines.write({'account_id' : trans.akad_id.property_account_receivable_id.id}) 
            invoice.action_post()

    
    def action_create_so(self):
        order_line = [(0,0,({
                        'product_id': self.product_id.id,
                        'name': self.product_id.name + " : " + self.name + " - " + self.member_id.name,
                        'product_uom_qty': 1,
                        'price_unit': self.nilai_pinjaman,
                        'tax_id': False,
                        'invoice_status': 'no',
                            }))]
        sale_order = self.env['sale.order'].create({
                                'name': self.env['ir.sequence'].next_by_code('sale.order'),
                                'partner_id': self.member_id.partner_id.id,
                                'validity_date': date.today(),
                                'payment_term_id': 1,
                                'order_line': order_line,
                                'origin': self.name,
                                'client_order_ref': 'Pinjaman '+ self.name,
                                'analytic_account_id': self.account_analytic_id.id,
                                'state': 'sale',
                                'pinjaman_id': self.id,
                                'user_id': self.env.uid,
                                'confirmation_date': date.today(),
#                                'invoice_status': 'no',
                                            })
        sale_order.action_confirm()



class PinjamanBiaya(models.Model):
    _name = "pinjaman.biaya"
    _description = "Komponen Biaya Pinjaman Anggota Simpin Syariah"


    @api.model
    def _default_currency(self):
        return self.env.user.company_id.currency_id.id

    name = fields.Char(string='Biaya')
    pinjaman_id = fields.Many2one('simpin_syariah.pinjaman',string='Pinjaman',track_visibility='onchange')
    quantity = fields.Integer(string='Qty',track_visibility='onchange', default=1)
    harga = fields.Monetary(string='Harga Satuan', currency_field='currency_id', track_visibility='onchange')
    subtotal = fields.Monetary(string='Sub Total', compute='_compute_harga', currency_field='currency_id', track_visibility='onchange')
    currency_id = fields.Many2one('res.currency', string="Currency", readonly=True, default=_default_currency)

    
    @api.depends('quantity','harga')
    def _compute_harga(self):
        self.subtotal = float(self.quantity) * float(self.harga)

   
    @api.onchange('quantity')
    def _onchange_quantity(self):
        self.subtotal = float(self.quantity) * float(self.harga)

    @api.onchange('harga')
    def _onchange_quantity(self):
        self.subtotal = float(self.quantity) * float(self.harga)
