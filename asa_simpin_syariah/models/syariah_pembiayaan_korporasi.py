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

class SimPinPembiayaan(models.Model):
    _name = "simpin_syariah.pembiayaan.korporasi"
    _description = "Pembiayaan Korporasi Simpin Syariah"
    _inherit = ['mail.thread']


    @api.model
    def _default_currency(self):
        return self.env.user.company_id.currency_id.id

    name = fields.Char(string='Nomor Pembiayaan')
    mitra_id = fields.Many2one('simpin_syariah.mitra', string='Mitra Kerja',store=True, required=True)
    akad_id = fields.Many2one('master.akad_syariah',string='Jenis Akad',
                                     domain=['|',('category_id.parent_id.name', 'ilike', 'Investasi'),
                                         ('category_id.name', 'ilike', 'Investasi')])
    product_id = fields.Many2one('product.product',string='Produk', required=True, 
                              readonly=True, states={'draft': [('readonly', False)]}, copy=False,track_visibility='onchange',
                                 domain=[('is_syariah', '=', True),
                                         '|',('product_tmpl_id.categ_id.parent_id.name', 'ilike', 'Investasi'),
                                         ('product_tmpl_id.categ_id.name', 'ilike', 'Investasi')])
    currency_id = fields.Many2one('res.currency', string="Currency", readonly=True, default=_default_currency)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submit', 'Submitted'),
        ('check', 'Check Document'),
        ('approve', 'Approved'),
        ('active', 'Active'),
        ('close', 'Closed'),
        ('block', 'Blocked'),
        ], string='Status', copy=False, index=True, default='draft', track_visibility='onchange', readonly=True)
    account_analytic_id = fields.Many2one('account.analytic.account', required=True, string='Analytic Account')
    peruntukan = fields.Many2one('master.general', string='Peruntukan', required=True, 
                                     domain=[('type_umum', '=', 'peruntukan'),('is_korporasi','=',True)], track_visibility='onchange')
    periode_angsuran = fields.Integer(string='Periode Angsuran', required=True, readonly=True, store=True,
                                      track_visibility='onchange', states={'draft': [('readonly', False)]}, default=12)
    #invoice_lines = fields.One2many('account.invoice', 'pembiayaan_id', string='Angsuran', copy=False, store=True, domain=[('type', '=', 'out_invoice'),('type_journal', 'in', ['tagihan','pelunasan'])])
    tanggal_akad = fields.Date(string='Tanggal Akad', states={'approve': [('readonly', True)]}, index=True)
    #total_investasi = fields.Monetary(string='Nilai Investasi',track_visibility='onchange',compute="_compute_total_investasi",required=True)
    total_investasi = fields.Monetary(string='Nilai Investasi',track_visibility='onchange')
    payment_id = fields.Many2one('account.payment', string='Pencairan')
    journal_id = fields.Many2one('account.journal', string='Journal', related='akad_id.journal_id')
    notes = fields.Text(string='Keterangan')
    partner_id = fields.Many2one('res.partner', string='Mitra Kerja', related='mitra_id.partner_id')
    partner_bank_id = fields.Many2one('res.partner.bank', string='Rek Mitra Kerja', states={'draft': [('readonly', False)]},
                                        track_visibility='onchange', help="You can find a vendor by its Name, TIN, Email or Internal Reference.")
    jangka_waktu = fields.Selection([
        ('12','12 Bulan'),
        ('24','24 Bulan'),
        ('36','36 Bulan'),
        ], string='Jangka Waktu', copy=False, index=True, default='12', track_visibility='onchange',required=True)
    jatuh_tempo = fields.Date(string='Jatuh Tempo',compute='_compute_jatuh_tempo',store=True)
    pengembalian  = fields.Selection([
        ('aro', 'Automatic Roll Over (ARO)'),
        ('jatuh_tempo', 'Jatuh Tempo'),
        ], string='Pengembalian', copy=False, index=True, default='aro', track_visibility='onchange')
    nisbah_investor = fields.Float(string='Nisbah Investor',default=25, required=True)
    pajak_nisbah = fields.Many2one('account.tax', string='Pajak', required=True, domain=[('type_tax_use','!=','none'),('active', '=', True)])
    journal_id = fields.Many2one('account.journal', string='Journal', related='akad_id.journal_id')
    pembayaran_nisbah = fields.Selection([
        ('1', 'Setiap Bulan'),
        ('2', 'Jatuh Tempo'),
        ], string='Pembayaran Nisbah', copy=False, index=True, default='1', track_visibility='onchange')
    
    ########## DOCUMENT PENDUKUNG ###########
    upload_mou = fields.Binary(string="Upload MOU")
    file_mou = fields.Char(string="File MOU")
    upload_dok_lain = fields.Binary(string="Upload Dok Pendukung")
    file_dok_lain = fields.Char(string="File Dok Pendukung")
    upload_npwp = fields.Binary(string="Upload NPWP")
    file_npwp = fields.Char(string="File NPWP")
    upload_slip1 = fields.Binary(string="Upload Rek Koran #1")
    file_slip1 = fields.Char(string="File Rek Koran #1")
    upload_slip2 = fields.Binary(string="Upload Rek Koran #2")
    file_slip2 = fields.Char(string="File Rek Koran #2")
    upload_slip3 = fields.Binary(string="Upload Rek Koran #3")
    file_slip3 = fields.Char(string="File Rek Koran #3")

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Nomor Pembiayaan must be unique!'),
    ]

    
    @api.depends('jangka_waktu','tanggal_akad')
    def _compute_jatuh_tempo(self):
        if self.tanggal_akad:
            jangka_waktu = int(self.jangka_waktu)
            self.jatuh_tempo = self.tanggal_akad + relativedelta(months=jangka_waktu)

    
    @api.depends('product_id')
    def _compute_total_investasi(self):
        if self.product_id:
            self.total_investasi = sum(self.env['simpin_syariah.investasi'].search([('product_id','=',self.product_id.id)]).mapped('total_investasi'))

    
    def action_submit(self):
        self.write({'state': 'submit'})

    
    def action_check(self):
        self.write({'state': 'check'})

    
    def action_approve(self,tanggal_akad=False):
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
        if not self.tanggal_akad:
            if isinstance(tanggal_akad, date):
#            raise UserError(_('tanggal akad %s')%(isinstance(tanggal_akad, date),))
                self.tanggal_akad = tanggal_akad 
            else:
                self.tanggal_akad = date.today()

        self.name = rekno
        raise UserError(_('Nomor Pembiayaan %s \ntanggal akad %s \n\n Selanjutnya Proses Pencairan')%(self.name,self.tanggal_akad,))
        if self.peruntukan.tipe=='service':
            invoice = self.proses_pencairan(rekno,False)
            self.action_create_so()
        self.write({'name': rekno, 'state': 'approve'})

    def proses_pencairan(self,rekno):
        inv_lines = []
        coa_debit = coa_credit = False
        akad_line = self.env['master.akad_journal'].search([('akad_id','=',self.akad_id.id),
                                                            ('type_journal','=','pencairan')],order='id')

        if not self.journal_id.default_debit_account_id: # or not self.journal_id.default_credit_account_id:
            raise UserError(_('Konfigurasi Journal belum Sesuai'))
        else:
            total = self.total_pembiayaan
                
            coa_debit = self.journal_id.default_debit_account_id.id
            coa_credit = self.journal_id.default_credit_account_id.id
            margin = 0
            for line in akad_line:
                if margin==0 and line.coa_kredit:
                    coa_name = 'Bagi Hasil Ditangguhkan: ' + rekno + " - " + self.member_id.name
                    margin = self.harga_jual - total
                    inv_lines += [(0, 0, self._prepare_inv_line(self,coa_name, line.coa_kredit.id,total))]
                else:
                    coa_name = 'Pencairan Pokok: ' + rekno + " - " + self.member_id.name
                    inv_lines += [(0, 0, self._prepare_inv_line(self,coa_name, line.coa_kredit.id,total))]

            invoice = self.env['account.invoice'].create({
                    'date_invoice': self.tanggal_akad,
                    'name': 'Pencairan : ' + rekno + " - " + self.member_id.name,
                    'origin': rekno,
                    'type': 'in_invoice',
                    'reference': rekno,
                    'account_id': coa_debit,
                    'partner_id': self.member_id.partner_id.id,
                    'invoice_line_ids': inv_lines,
                    'journal_id': self.journal_id.id,
                    'currency_id': self.currency_id.id,
                    'comment': 'Pencairan : ' + rekno,
                    'payment_term_id': 1,
                    'type_journal': 'pencairan',
                    'pembiayaan_id': self.id,
                    'pinjaman_id': False,
                    'investasi_id': False,
                    })
            invoice.action_invoice_open_syariah()
            csql = "update account_invoice set residual=%s, residual_signed=%s, residual_company_signed=%s, state='open' where id=%s"
            self.env.cr.execute(csql, (total,total,total,invoice.id,))

        return invoice
