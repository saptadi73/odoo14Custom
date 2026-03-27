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

    pembiayaan_id = fields.Many2one('simpin_syariah.pembiayaan',string='Pembiayaan')

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
                if move.pembiayaan_id:
                    if move.move_type == 'in_invoice' :
                        print ("=============paid===============")
                        move.pembiayaan_id.write({'state': 'active'})
                        move.pembiayaan_id.create_jurnal_margin()
                        move.pembiayaan_id.create_invoice_angsuran()
                        print ("============close=======")
                    if move.move_type == 'out_invoice' :
                        move.pembiayaan_id.create_jurnal_margin_angsuran()
        return res
    
class StockPicking(models.Model):
    _inherit = 'stock.picking'
    
    pembiayaan_id = fields.Many2one('simpin_syariah.pembiayaan',string='Pembiayaan')
    
    def _action_done(self):
        res = super(StockPicking, self)._action_done()
        for picking in self :
            if picking.state == 'done' :
                if picking.picking_type_id.code == 'outgoing':
                    if picking.pembiayaan_id :
                        print ("=================DO===============")
                        picking.pembiayaan_id.create_jurnal_margin()
                        picking.pembiayaan_id.create_invoice_angsuran()
                    
        return res
    
    
    
class StockMove(models.Model):
    _inherit = 'stock.move'
    
    def _account_entry_move(self, qty, description, svl_id, cost):
        """ Accounting Valuation Entries """
        self.ensure_one()
        if self.product_id.type == 'service':
            # no stock valuation for consumable products
            return False
        if self.restrict_partner_id:
            # if the move isn't owned by the company, we don't make any valuation
            return False

        location_from = self.location_id
        location_to = self.location_dest_id
        company_from = self._is_out() and self.mapped('move_line_ids.location_id.company_id') or False
        company_to = self._is_in() and self.mapped('move_line_ids.location_dest_id.company_id') or False

        journal_id, acc_src, acc_dest, acc_valuation = self._get_accounting_data_for_valuation()
        # Create Journal Entry for products arriving in the company; in case of routes making the link between several
        # warehouse of the same company, the transit location belongs to this company, so we don't need to create accounting entries
        if self._is_in():
            if self._is_returned(valued_type='in'):
                self.with_company(company_to)._create_account_move_line(acc_dest, acc_valuation, journal_id, qty, description, svl_id, cost)
            else:
                self.with_company(company_to)._create_account_move_line(acc_src, acc_valuation, journal_id, qty, description, svl_id, cost)

        # Create Journal Entry for products leaving the company
        if self._is_out():
            cost = -1 * cost
            if self._is_returned(valued_type='out'):
                self.with_company(company_from)._create_account_move_line(acc_valuation, acc_src, journal_id, qty, description, svl_id, cost)
            else:
                self.with_company(company_from)._create_account_move_line(acc_valuation, acc_dest, journal_id, qty, description, svl_id, cost)

        if self.company_id.anglo_saxon_accounting:
            # Creates an account entry from stock_input to stock_output on a dropship move. https://github.com/odoo/odoo/issues/12687
            if self._is_dropshipped():
                if cost > 0:
                    self.with_company(self.company_id)._create_account_move_line(acc_src, acc_valuation, journal_id, qty, description, svl_id, cost)
                else:
                    cost = -1 * cost
                    self.with_company(self.company_id)._create_account_move_line(acc_valuation, acc_dest, journal_id, qty, description, svl_id, cost)
            elif self._is_dropshipped_returned():
                if cost > 0:
                    self.with_company(self.company_id)._create_account_move_line(acc_valuation, acc_src, journal_id, qty, description, svl_id, cost)
                else:
                    cost = -1 * cost
                    self.with_company(self.company_id)._create_account_move_line(acc_dest, acc_valuation, journal_id, qty, description, svl_id, cost)

        if self.company_id.anglo_saxon_accounting:
            # Eventually reconcile together the invoice and valuation accounting entries on the stock interim accounts
            self._get_related_invoices()._stock_account_anglo_saxon_reconcile_valuation(product=self.product_id)


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    pembiayaan_id = fields.Many2one('simpin_syariah.pembiayaan',string='Pembiayaan')

    
    def action_view_invoice_syariah(self):
        '''
        This function returns an action that display existing vendor bills of given purchase order ids.
        When only one found, show the vendor bill immediately.
        '''
        action = self.env.ref('account.action_vendor_bill_template')
        result = action.read()[0]
        create_bill = self.env.context.get('create_bill', False)
        # override the context to get rid of the default filtering
        result['context'] = {
            'type': 'in_invoice',
            'default_purchase_id': self.id,
            'default_currency_id': self.currency_id.id,
            'default_company_id': self.company_id.id,
            'company_id': self.company_id.id,
            'default_pembiayaan_id': self.pembiayaan_id.id
        }
        # choose the view_mode accordingly
        if len(self.invoice_ids) > 1 and not create_bill:
            result['domain'] = "[('id', 'in', " + str(self.invoice_ids.ids) + ")]"
        else:
            res = self.env.ref('account.invoice_supplier_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            # Do not set an invoice_id if we want to create a new bill.
            if not create_bill:
                result['res_id'] = self.invoice_ids.id or False
        result['context']['default_origin'] = self.name
        result['context']['default_reference'] = self.partner_ref
        return result


# class ResPartnerBank(models.Model):
#     _inherit = 'res.partner.bank'

#     @api.model
#     def default_get(self, default_fields):
#         """If we're creating a new account through a many2one, there are chances that we typed the account code
#         instead of its name. In that case, switch both fields values.
#         """
#         default_name = self._context.get('default_bank_id.name')
#         default_code = self._context.get('default_acc_number')
#         if default_name and not default_code:
#             try:
#                 default_code = int(default_name)
#             except ValueError:
#                 pass
#             if default_code:
#                 default_name = False
#         contextual_self = self.with_context(default_name=default_name, default_code=default_code)
#         return super(ResPartnerBank, contextual_self).default_get(default_fields)

#     @api.model
#     def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
#         args = args or []
#         domain = []
#         cek_sp = name.find(' ')
#         if name:
#             if cek_sp>=0:
#                 domain = ['|', ('code', '=ilike', name.split(' ')[0] + '%'), ('name', operator, name)]
#             else:
#                 domain = ['|', ('code', '=ilike', name + '%'), ('name', operator, name)]

# #            raise UserError(_('name %s = cek_sp %s \n domain %s')%(name,cek_sp,domain))                
#             if operator in expression.NEGATIVE_TERM_OPERATORS:
#                 domain = ['&', '!'] + domain[1:]
#         account_ids = self._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid)
#         return self.browse(account_ids).name_get()

    
#     def name_get(self):
#         result = []
#         for bank in self:
#             name = bank.bank_id.name + ' ' + bank.acc_number
#             result.append((bank.id, name))
#         return result



class SimPinPembiayaan(models.Model):
    _name = "simpin_syariah.pembiayaan"
    _description = "Pembiayaan Anggota Simpin Syariah"
    _inherit = ['mail.thread', 'mail.activity.mixin']


    @api.model
    def _default_currency(self):
        return self.env.user.company_id.currency_id.id
    
    def _get_stock_type_ids(self):
        data = self.env['stock.picking.type'].search([])
        for line in data:
            if line.code == 'outgoing':
                return line

    name = fields.Char(string='Nomor Pembiayaan')
    member_id = fields.Many2one('simpin_syariah.member',string='Nama Anggota', required=True,
                                 domain=[('state', '=', 'done')])
    akad_kode = fields.Char(string='Akad Code',readonly=True, store=True)
    akad_id = fields.Many2one('master.akad_syariah',string='Jenis Akad')
    product_id = fields.Many2one('product.product',string='Produk', required=True, 
                              readonly=True, states={'draft': [('readonly', False)]}, copy=False,track_visibility='onchange',
                                 domain=[('is_syariah', '=', True), ('state', '=', 'open')])
    is_blokir = fields.Boolean('Blokir', default=False)
    currency_id = fields.Many2one('res.currency', string="Currency", readonly=True, default=_default_currency)
    balance = fields.Monetary(string='Balance',  currency_field='currency_id', compute='_compute_balance',store=True)
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
    account_analytic_id = fields.Many2one('account.analytic.account', required=True, string='Analytic Account')
    peruntukan = fields.Many2one('master.general', string='Peruntukan', required=True, 
                                     domain=[('type_umum', '=', 'peruntukan')], track_visibility='onchange')
    periode_angsuran = fields.Integer(string='Periode Angsuran', required=True, readonly=True, store=True,
                                      track_visibility='onchange', states={'draft': [('readonly', False)]}, default=12)
    margin = fields.Float(string='Margin (%)', compute='_compute_angsuran', readonly=True, store=True, track_visibility='onchange')
    angsuran = fields.Monetary(string='Angsuran',compute='_compute_angsuran',track_visibility='onchange', store=True)
    invoice_lines = fields.One2many('account.move', 'pembiayaan_id', string='Angsuran', copy=False, store=True, domain=[('move_type', '=', 'out_invoice')])
    tanggal_akad = fields.Date(string='Tanggal Akad', states={'approve': [('readonly', False)]}, index=True, default=datetime.today())
    total_pembiayaan = fields.Monetary(string='Nilai Pembiayaan',track_visibility='onchange',default=5000000,required=True)
    harga_jual = fields.Monetary(string='Harga Jual', compute='_compute_angsuran',readonly=True, store=True,track_visibility='onchange')
    payment_id = fields.Many2one('account.payment', string='Pencairan')
    journal_id = fields.Many2one('account.journal', string='Journal', related='akad_id.journal_id')
    biaya_lines = fields.One2many('pembiayaan.biaya', 'pembiayaan_id',  string='Komponen Biaya')
    allowance_lines = fields.One2many('pembiayaan.biaya.deduction', 'pembiayaan_id',  string='Komponen Biaya Deduction')
    deduction_lines = fields.One2many('pembiayaan.biaya.allowance', 'pembiayaan_id',  string='Komponen Biaya Allowance')
    jumlah_biaya = fields.Monetary(string='Total Biaya', currency_field='currency_id', track_visibility='onchange')
    jumlah_um = fields.Monetary(string='Uang Muka', currency_field='currency_id', track_visibility='onchange')
    total_um = fields.Monetary(string='Total Uang Muka', currency_field='currency_id', track_visibility='onchange')
    move_pencairan = fields.Many2one('account.move',readonly=True, store=True, string='Journal Pencairan')
    qty_available = fields.Float('Quantity On Hand', related='product_id.qty_available')
    akad_tipe = fields.Selection([
        ('product', 'Barang'),
        ('service', 'Jasa')], string='Product Type',readonly=True, store=True )
    notes = fields.Text(string='Keterangan')
    jenis_sewa = fields.Selection([
        ('nonsewa', 'Non Sewa'),
        ('sewa', 'Sewa tanpa pemindahan hak aset pada akhir periode'),
        ('sewabeli', 'Sewa dengan pemindahan hak aset pada akhir periode'),
        ], string='Jenis Sewa', default='nonsewa', readonly=True,related='akad_id.jenis_sewa')
    hibah_jual = fields.Selection([
        ('non_hibah', 'Non Hibah/Jual'),
        ('hibah', 'Hibah'),
        ('jual', 'Jual'),
        ], string='Pemindahan Hak', default='non_hibah', required=True)
    vendor_id = fields.Many2one('res.partner', string='Vendor / Pihak Ketiga', domain=[('supplier', '=', True)],states={'draft': [('readonly', False)]}, track_visibility='onchange', help="You can find a vendor by its Name, TIN, Email or Internal Reference.")
    vendor_bank_id = fields.Many2one('res.partner.bank', string='Rek Pihak Ketiga', states={'draft': [('readonly', False)]},
                                        track_visibility='onchange', help="You can find a vendor by its Name, TIN, Email or Internal Reference.")
    thp_gaji = fields.Monetary(string='THP Gaji Terakhir', store=True, default=False, currency_field='currency_id', track_visibility='onchange')
    cash_ratio = fields.Float('Cash Ratio (%)', store=True, default=100)
    src_bank_id = fields.Many2one('res.bank','Source Bank', store=True)
    src_bank_norek = fields.Char('Source Bank Account #', store=True)
    mitra_id = fields.Many2one('simpin_syariah.mitra', string='Mitra Kerja', related='member_id.mitra_id',store=True)
    mitra_bank_id = fields.Many2one('simpin_syariah.mitra.bank', string='Mitra Bank', related='product_id.product_tmpl_id.mitra_bank_id',store=True)
    jurnal_biaya = fields.Char(string='Jurnal Type', store=True)
    last_invoice = fields.Date(string='Tagihan Terakhir', readonly=True, store=True, index=True)
    loan_id = fields.Many2one('simpin_syariah.loan_detail',string='Loan Bank', readonly=True, store=True, index=True)
    invoice_dp = fields.Many2one('account.move',string='Invoice DP', copy=False, store=True)
    delivery = fields.Many2one('stock.move', string='Delivery Order', copy=False, store=True)
    tanggal_close = fields.Date(string='Tanggal Close', index=True)
    
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

    pembiayaan_picking_id = fields.Many2one('stock.picking', string="Picking Id", copy=False)
    do_status = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done')
    ], string='Status DO', compute='_compute_state', store=True)
    picking_type_id = fields.Many2one('stock.picking.type', 'Picking Type',
                                      default=_get_stock_type_ids)

    @api.depends('pembiayaan_picking_id.state')
    def _compute_state(self):
        for rec in self:
            if rec.pembiayaan_picking_id != False:
                if rec.pembiayaan_picking_id.state == 'done' :
                    rec.do_status = 'done'
                else :
                    rec.do_status = 'draft'
                if rec.do_status == 'done':
                    rec.state = 'active'



    
    # paid_status = fields.Boolean(string='Is Paid', compute='_cek_paid_status', store=True)

    # @api.depends('move_pencairan.payment_state')
    # def _cek_paid_status(self):
    #     for pmb in self :
    #         if pmb.move_pencairan.payment_state == 'paid':
    #             pmb.paid_status = True
    #             pmb.state = 'active'
    #             pmb.create_jurnal_margin()
    #             pmb.create_invoice_angsuran()

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Nomor Pembiayaan must be unique!'),
    ]
        
    @api.onchange('thp_gaji','member_id')
    def _onchange_thp_gaji(self):
        cash_rasio = False
        cash_ratio = self.env['master.general'].search([('type_umum','=','cash_ratio')],order='id',limit=1)
        if not cash_ratio and self.member_id and self.thp_gaji:
            raise UserError(_('Cash Ratio belum ada, Harap Melakukan Konfigurasi'))
        else:
            cash_rasio = cash_ratio[0].nominal

            
        if self.thp_gaji and self.member_id:       
            self.env.cr.execute("select sum(angsuran) as total from simpin_syariah_pembiayaan where state in ('active','approve') and member_id=%s",(self.member_id.id,))
            angs_biaya = self.env.cr.fetchone()
            if angs_biaya[0] != None:
                biaya = angs_biaya[0]
            else:
                biaya = 0

            self.env.cr.execute("select sum(angsuran) as total from simpin_syariah_pinjaman where state in ('active','approve') and member_id=%s",(self.member_id.id,))
            angs_pinjam = self.env.cr.fetchone()
            if angs_pinjam[0] != None:
                pinjam = angs_pinjam[0]
            else:
                pinjam = 0
                
            persentase = cash_rasio*self.thp_gaji
            sisa_angsuran = persentase - biaya - pinjam

            self.cash_ratio = round((persentase-sisa_angsuran)/self.thp_gaji,2)*100

        self.mitra_id = self.member_id.mitra_id.id


    
    #@api.depends('last_invoice','invoice_lines','invoice_lines.state')
    def _compute_balance(self):
        for rec in self:
            tgl_migrasi = datetime.strptime('2021-03-01 00:00:00','%Y-%m-%d %H:%M:%S')
            balance = rec.harga_jual
            if rec.tanggal_akad and rec.tanggal_akad<tgl_migrasi.date():
                awal = relativedelta(tgl_migrasi,rec.tanggal_akad)
                bln = awal.years*12 + awal.months
                balance = rec.harga_jual - (rec.angsuran * bln)
            tunggakan = 0
            for inv in rec.invoice_lines:
                if inv.state=='paid':
                    balance -= inv.amount_total
                elif inv.state=='open':
                    tunggakan += inv.residual
#            raise UserError(_('rec %s = %s \n Balance %s \n Tunggakan %s')%(rec.name,rec.tanggal_akad,balance,tunggakan))
            rec.update({'balance': balance, 'tunggakan': tunggakan,})

    # @api.onchange('last_invoice','invoice_lines','invoice_lines.state')
    # def _onchange_invoice_lines(self):
    #     self._compute_balance
        
    # @api.onchange('biaya_lines')
    # def _onchange_biaya_lines(self):
    #     total = 0
    #     for line in self.biaya_lines:
    #         total += line.harga
    #     if self.jurnal_biaya=='biaya_murabahah':
    #         self.total_um = total
    #         self.jumlah_biaya = 0
    #     else:
    #         self.total_um = 0
    #         self.jumlah_um = 0
    #         self.jumlah_biaya = total

    @api.onchange('allowance_lines','deduction_lines')
    def _onchange_biaya_lines(self):
        total_allow = 0
        total_deduct = 0
        for line in self.allowance_lines:
            total_allow += line.amount
        for deduc in self.deduction_lines:
            total_deduct += deduc.amount
        if self.jurnal_biaya=='biaya_murabahah':
            self.total_um = total_allow + total_deduct


    
    @api.depends('periode_angsuran','total_pembiayaan','product_id','margin','jumlah_um','jurnal_biaya')
    def _compute_angsuran(self):
        if self.product_id and (self.state!='active' or self.state!='close'):
            margin = periode_max = nilai_max = nilai_min = periode_min = False
            for line in self.product_id.nisbah_lines:
                if not periode_max or line.periode_max>periode_max: 
                    periode_max = line.periode_max
                if not periode_min or line.periode_max<periode_min:
                    periode_min = line.periode_min

                if line.periode_max>=self.periode_angsuran:
                    nilai_max = line.nilai_max
                    nilai_min = line.nilai_min
                    margin = line.margin
                    self.margin = line.margin
                    break
            
            if nilai_min and self.total_pembiayaan<nilai_min:
                self.total_pembiayaan=nilai_min
#                raise UserError(_('Nilai Pinjaman Minimal %s')%('{:,}'.format(nilai_min),))
            elif nilai_max and self.total_pembiayaan>nilai_max:
                self.total_pembiayaan=nilai_max
#                raise UserError(_('Nilai Pinjaman melebihi Nilai Maksimal %s')%('{:,}'.format(nilai_max),))

            if periode_max and self.periode_angsuran > periode_max:
                self.periode_angsuran = periode_max
                raise UserError(_('Periode melebihi maksimal %s bulan')%(periode_max,))
            elif periode_min and self.periode_angsuran < periode_min:
                self.periode_angsuran = periode_min
#                raise UserError(_('Periode minimal %s bulan')%(periode_min,))

            if not margin:
                raise UserError(_('Belum ada Konfigurasi'))
            self.src_bank_id = self.product_id.sumber_dana.bank_id.id
            self.src_bank_norek = self.product_id.sumber_dana.bank_account_id.acc_number

            if self.biaya_lines:
                total_biaya = 0
                for line in self.biaya_lines:
                    if line.nilai_pct:
                        line.harga = self.total_pembiayaan * (line.nilai_pct/100)
                    if line.is_um:
                        self.jumlah_um = line.harga
                    total_biaya +=line.harga
                self.jumlah_biaya = total_biaya
            else:
                self.jumlah_biaya = 0

            if margin and self.total_pembiayaan>0:
                if self.state=='draft':
                    self.margin = margin

                if self.jurnal_biaya=='biaya_murabahah' or self.jurnal_biaya=='biaya_bank':
                    self.angsuran = round(self.calc_pmt(margin,self.periode_angsuran,self.total_pembiayaan-self.jumlah_um),0)
                    self.harga_jual = (self.angsuran * self.periode_angsuran) 
                else:
                    self.jumlah_um = 0
                    self.angsuran = round(self.calc_pmt(margin,self.periode_angsuran,self.total_pembiayaan),0)
                    self.harga_jual = (self.angsuran * self.periode_angsuran) + self.jumlah_biaya 


            if self.product_id.product_tmpl_id.type=='product' and self.peruntukan.tipe=='product':
                self.akad_tipe='product'
            else:
                self.akad_tipe='service'

            if not self.akad_id:
                self.akad_id = self.product_id.product_tmpl_id.jenis_syariah.id

        currency = self.currency_id or None
#        total = self.total_pembiayaan + self.jumlah_biaya

    
    def cron_update_balance(self):
        pembiayaan = self.env['simpin_syariah.pembiayaan'].search([('state','in',['active','close'])])
        for biaya in pembiayaan:
            balance=biaya.harga_jual
            paid_inv = self.env['account.invoice'].search([('type_journal','=','tagihan'),
                                                            ('pembiayaan_id','=',biaya.id),
                                                            ('state','=','paid'),
                                                            ],order='date_invoice desc',limit=1)
            open_inv = self.env['account.invoice'].search([('type_journal','=','tagihan'),
                                                            ('pembiayaan_id','=',biaya.id),
                                                            ('state','=','open'),
                                                            ],order='date_invoice desc')
            bulan_last = relativedelta(paid_inv.date_invoice,biaya.tanggal_akad)
            bulan_biaya = (bulan_last.years*12) + bulan_last.months 
            if bulan_biaya>biaya.periode_angsuran:
                balance = 0
            else:
                balance = biaya.harga_jual - (biaya.angsuran*bulan_biaya)
            
            tunggakan = 0
            for inv in open_inv:
                tunggakan += inv.residual
#            raise UserError(_('pembiayaan %s : %s == %s')%(biaya.name,balance,tunggakan))
            biaya.write({'balance': balance,'tunggakan': tunggakan})



    def cron_recount_pembiayaan(self):
        product = self.env['product.product'].search([('is_syariah', '=', True),
                                                      '|',('product_tmpl_id.categ_id.parent_id.name', '=', 'Pembiayaan'),
                                                      ('product_tmpl_id.categ_id.name', '=', 'Pembiayaan')
                                                          ])
        if product:
            for line in product:
                total_pengajuan = total_pembiayaan = 0.0
                pembiayaan = self.env['simpin_syariah.pembiayaan'].search([('product_id','=',line.id)])
                if pembiayaan:
                    for pline in pembiayaan:
                        if pline.state=='active' or pline.state=='approve':
                            total_pembiayaan += pline.total_pembiayaan
                        else:
                            total_pengajuan += pline.total_pembiayaan

                if total_pembiayaan==0.0 and total_pengajuan==0.0 and line.product_tmpl_id.state!='draft' and line.product_tmpl_id.state!='open':
                    line.product_tmpl_id.write({'total_pengajuan': total_pengajuan, 'total_pembiayaan': total_pembiayaan,  'state': 'close',})
                else:
                    line.product_tmpl_id.write({'total_pengajuan': total_pengajuan, 'total_pembiayaan': total_pembiayaan,'state': 'open',})
            

    def calc_total_pembiayaan(self):
        pengajuan = self.env['simpin_syariah.pembiayaan'].search([('state','in',['draft','submit','check']),('product_id','=',self.product_id.id)])
        pencairan = self.env['simpin_syariah.pembiayaan'].search([('state','in',['active','approve']),('product_id','=',self.product_id.id)])
        total_ajuan = total_cair = 0
        for line in pengajuan:
            total_ajuan += line.total_pembiayaan
        for line in pencairan:
            total_cair += line.total_pembiayaan
            
#        raise UserError(_('product_id %s \n pengajuan %s -- pencairan %s')%(self.product_id,total_ajuan, total_cair,))
        self.product_id.product_tmpl_id.write({'total_pengajuan': total_ajuan, 'total_pembiayaan': total_cair})


    def calc_pmt(self,margin,periode_angsuran,nilai_pinjaman):
        annual_rate = margin/100
        interest_rate = annual_rate / 12
        present_value = nilai_pinjaman * interest_rate

        angsuran = present_value / (1-((1 + interest_rate)**-periode_angsuran))
        return angsuran

    def get_data_angsuran(self):
        periode = self.periode_angsuran
        angsuran = self.angsuran
        if self.tanggal_akad:
            bulan = self.tanggal_akad
        else:
            bulan = date.today()
            
        if self.jurnal_biaya=='biaya_murabahah':
            pokok_pinjaman = self.total_pembiayaan - self.jumlah_um
            angsuran_margin = pokok_pinjaman * (self.margin/1200)
            angsuran_pokok = angsuran - angsuran_margin
        else:
            pokok_pinjaman = self.total_pembiayaan
            angsuran_margin = pokok_pinjaman * (self.margin/1200)
            angsuran_pokok = angsuran - angsuran_margin

        result = []
        for i in range(1,periode+1):
            isi_data ={}
            bulan += relativedelta(months=1)
            if i>1:
#                pokok_pinjaman = self.total_pembiayaan
#                angsuran_margin = pokok_pinjaman * (self.margin/1200)
#                angsuran_pokok = angsuran - angsuran_margin
#            else:
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

    def update_data(self):
        pelunasan = tagihan = False
        cek = []
        tagihan = self.env['account.invoice'].search([('type_journal','=','tagihan'),('state','=','open'),('file_name','=',False),
#                                                      ('date_invoice','<','2021-06-30'),
                                                      ('pembiayaan_id','!=',False)],order='date_invoice desc',limit =100)
#        pelunasan = self.env['account.invoice'].search([('type_journal','=','pelunasan'),('state','=','open'),
#                                                        ('date_invoice','<','2021-06-30')])

#        if tagihan:
        for inv in tagihan:
            coa_credit = inv.pembiayaan_id.akad_id.journal_id.default_credit_account_id
            akad_line = self.env['master.akad_journal'].search([('akad_id','=',inv.pembiayaan_id.akad_id.id),
                                                            ('type_journal','=','tagihan')])
            margin = 0
            for line in akad_line:
                if line.coa_debet and margin==0:
                    margin = 100
                    coa_pokok = line.coa_debet.id
                elif line.coa_debet and margin>0:
                    coa_margin = line.coa_debet.id
                    
            for line in inv.invoice_line_ids:
                margin = 0
                pokok = line.name.find("Angsuran Pokok")
                margin = line.name.find("Angsuran Margin")
                if pokok>=0:
                    line.update({'account_id': coa_pokok,})
                elif margin>=0:
                    line.update({'account_id': coa_margin,})
                cek.append({'COA': line.account_id.id,
                            'name': line.name,
                            'account': line.account_id.name,
                            'price_subtotal': line.price_subtotal,
                            })

            move_id = inv.move_id
            inv.update({'account_id': coa_credit.id,'move_id': False,'state': 'draft','file_name': 'nn'})
            move_id.update({'state': 'draft',})
            move_id.unlink()
            inv.action_invoice_open_syariah()
            aml = []
            for line in inv.move_id.line_ids:
                aml.append({'COA': line.account_id.id,
                            'account': line.account_id.name,
                            'name': line.name,
                            'debit': line.debit,
                            'credit': line.credit,
                            'amount_residual': line.amount_residual,
                            'currency_id': line.currency_id.id,})

#            raise UserError(_('jml tagihan %s \n inv coa %s - %s\n inv lines %s\n\naml %s')%(len(tagihan),inv.account_id.name,inv.amount_total,cek,aml,))
            
        if pelunasan:
#        for inv in pelunasan:
            last_inv = self.env['account.invoice'].search([('type_journal','=','tagihan'),
                                                           ('pembiayaan_id','=',inv.pembiayaan_id.id),
#                                                           ('date_invoice','<','2021-06-30')
                                                           ],order='date_invoice desc',limit=1)
            bulan_last = relativedelta(last_inv.date_invoice,inv.pembiayaan_id.tanggal_akad)
            kewajiban = False
            bulan_biaya = (bulan_last.years*12) + bulan_last.months
            data_tagihan = inv.pembiayaan_id.get_data_angsuran()
            for bulan in self.product_id.product_tmpl_id.pelunasan_lines:
                if bulan_biaya>=bulan.periode_min and bulan_biaya<=bulan.periode_max:
                    kewajiban = bulan.pelunasan

            if kewajiban:
                pokok_byr = data_tagihan[bulan_biaya]['pokok_pinjaman']
                pendapatan = mytd = kas = potongan = i = 0
                kas = pokok_byr
                for bl in range(bulan_biaya-1,inv.pembiayaan_id.periode_angsuran):
                    pendapatan += inv.pembiayaan_id.angsuran
                    mytd += data_tagihan[bl]['angsuran_margin']
                    if bl>=bulan_biaya+kewajiban:
                        potongan += data_tagihan[bl]['angsuran_margin']
                    i+=1
            
                akad_line = self.env['master.akad_journal'].search([('akad_id','=',inv.pembiayaan_id.akad_id.id),
                                                            ('type_journal','=','tagihan')])
                coa_debit = inv.pembiayaan_id.akad_id.journal_id.default_debit_account_id
                coa_credit = inv.pembiayaan_id.akad_id.journal_id.default_credit_account_id
                coa_pokok = coa_margin = coa_potong = False

                margin = amount_total = 0
                invoice_lines = []
                for line in akad_line:
                    if line.coa_debet and not line.coa_kredit:
                        coa_name = 'Pelunasan Pokok : ' + self.name + " - " + self.member_id.name
                        coa_pokok = line.coa_debet.id
#                        invoice_lines += [(0, 0, self._prepare_inv_line(self,coa_name, line.coa_debet.id,kas))]
                    elif line.coa_kredit and margin<=0:
                        margin = pendapatan
                        coa_name = 'Pelunasan Margin : ' + self.name + " - " + self.member_id.name
                        coa_margin = line.coa_debet.id
#                        invoice_lines += [(0, 0, self._prepare_inv_line(self,coa_name, line.coa_debet.id,mytd))]
                        coa_name_pot = 'Potongan Pelunasan : ' + self.name + " - " + self.member_id.name
                        coa_potong = line.coa_kredit.id
#                            invoice_lines += [(0, 0, self._prepare_inv_line(self,coa_name, line.coa_kredit.id,-potongan))]

                cek = []
                for line in inv.invoice_line_ids:
                    pokok = line.name.find("Pelunasan Pokok")
                    margin = line.name.find("Pelunasan Margin")
                    potong = line.name.find("Potongan Pelunasan")
#                    if pokok>=0:
#                        line.update({'account_id': coa_pokok,'price_unit': kas,'price_subtotal': kas,'price_subtotal_signed': kas,'price_total': kas,})
#                    elif margin>=0:
#                        line.update({'account_id': coa_margin,'price_unit': mytd,'price_subtotal': mytd,'price_subtotal_signed': mytd,'price_total': mytd,})
#                    elif potong>=0:
#                        line.update({'account_id': coa_potong,'price_unit': -potongan,'price_subtotal': -potongan,'price_subtotal_signed': -potongan,'price_total': -potongan,})
                    cek.append({'COA': line.account_id.id,
                            'name': line.name,
                            'account': line.account_id.name,
                            'price_subtotal': line.price_subtotal,
                            })
                amount_total = kas+mytd-potongan
                inv.update({'account_id':coa_credit.id,
                            'amount_untaxed_signed': amount_total,
                            'amount_total': amount_total,
                            'amount_total_signed': amount_total,
                            'amount_total_company_signed': amount_total,
                            'residual': amount_total,
                            'residual_signed': amount_total,
                            'residual_company_signed': amount_total,
                            })

#                move_id = inv.move_id
#                inv.update({'move_id': False,'state': 'draft'})
#                move_id.update({'state': 'draft',})
#                move_id.unlink()
#                inv.action_invoice_open_syariah()
                aml = []
                for line in inv.move_id.line_ids:
                    aml.append({'COA': line.account_id.id,
                            'account': line.account_id.name,
                            'name': line.name,
                            'debit': line.debit,
                            'credit': line.credit,
                            'amount_residual': line.amount_residual,
                            'currency_id': line.currency_id.id,})

#                raise UserError(_("""paid %s \nlast_inv %s \n bl_periode %s - sisa pokok %s - sisa margin %s - pot %s \n
#                                    inv_coa %s - %s == %s - %s \n\n inv pelunasan %s \n\n aml %s""")
#                                %(len(pelunasan),last_inv.date_invoice,bulan_biaya,kas,mytd,potongan,
#                                  inv.account_id.name,inv.amount_total,coa_credit.name,kas+mytd-potongan,
#                                  cek,aml,))

    def get_data_simulasi(self):
        self.env.cr.execute("select id,name,periode_min,periode_max,margin,nilai_min,nilai_max from master_nisbah where product_tmpl_id=%s",(self.product_id.product_tmpl_id.id,))
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
                        angsuran = round(self.calc_pmt(line['margin'],periode,harga_beli),0) #round(harga_beli/periode,0)
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

    @api.model
    def create(self, vals):
        res = super(SimPinPembiayaan, self).create(vals)
#        raise UserError(_('CP res %s')%(res,))
        return res

    
    def write(self, vals):
        for keys in vals.keys():
            if keys=='tanggal_akad':
#                if isinstance(vals['tanggal_akad'], date):
#                    raise UserError(_('tanggal akad %s')%(isinstance(vals['tanggal_akad'], date),))
                if self.tanggal_akad:
                     vals.update({'tanggal_akad': self.tanggal_akad})
                else:
                     vals.update({'tanggal_akad': False})
#                raise UserError(_('CP vals %s')%(vals,))
        res = super(SimPinPembiayaan, self).write(vals)
#        self.calc_total_pembiayaan()
        return res

    
    def action_blokir(self):
        raise UserError('Sub Modul Blokir Pembiayaan')

    
    def action_pelunasan(self):
        sale_order = self.env['sale.order'].search([('pembiayaan_id','=',self.id)])
        inv_obj = self.env['account.invoice']
        last_invoice = self.env['account.invoice'].search([('pembiayaan_id','=',self.id),
                                                            ('state','in',['open','paid']),
                                                            ('type','=','out_invoice'),],order="date_invoice desc")
        akad_line = self.env['master.akad_journal'].search([('akad_id','=',self.akad_id.id),
                                                            ('type_journal','=','tagihan')])
        xbulan = bulan_biaya = 0
        tanggal_inv = False
        kas = pokok = mytd = potongan = pendapatan = 0.0
        pokok_pinjaman = self.total_pembiayaan
        angsuran_pokok = angsuran_lain = margin_byr = pokok_byr = bulan_pembiayaan = 0
        selisih_akad = relativedelta(date.today(),self.tanggal_akad)
        hari_jalan = (selisih_akad.years*360)+(selisih_akad.months*30)+ selisih_akad.days
        if last_invoice and last_invoice[0].pembiayaan_id.state=='active': # 
            bulan_pembiayaan = relativedelta(last_invoice[0].date_due,self.tanggal_akad)
            kewajiban = False
            k_bulan = False
            bulan_biaya = (bulan_pembiayaan.years*12) + bulan_pembiayaan.months
            bulan_invoice = relativedelta(date.today(),last_invoice[0].date_due)
            if bulan_invoice.months==0:
                cur_mon = 0
            elif bulan_invoice.months>0:
                cur_mon = bulan_invoice.months

            for bulan in self.product_id.product_tmpl_id.pelunasan_lines:
                if not k_bulan:
                    k_bulan = bulan.periode_min
                #if bulan_pembiayaan.months>=bulan.periode_min and
                if bulan_biaya>=bulan.periode_min and bulan_biaya<=bulan.periode_max:
                    kewajiban = bulan.pelunasan

            if not kewajiban :
                raise UserError(_('Pelunasan minimal telah melakukan %s pembayaran')%(k_bulan,))
            elif kewajiban>0:
                data_tagihan = self.get_data_angsuran()
                pokok_byr = data_tagihan[bulan_biaya + cur_mon]['pokok_pinjaman']
                i = 0
                kas = pokok_byr
                bulan_biaya += cur_mon
                kewajiban -= cur_mon
#                pendapatan = (self.angsuran * -cur_mon)
                for bl in range(bulan_biaya,self.periode_angsuran):
                    pendapatan += self.angsuran
                    mytd += data_tagihan[bl]['angsuran_margin']
                    if bl>=bulan_biaya+kewajiban:
                        potongan += data_tagihan[bl]['angsuran_margin']
                    i+=1

            tanggal_inv = last_invoice[0].date_invoice
            if tanggal_inv<date.today():
                tanggal_inv = date.today()
            tanggal = relativedelta(date.today(),tanggal_inv)
            
#            raise UserError(_('kewajiban %s \n kas %s \n pendapatan %s \n mytd %s \n potongan %s \n bln_inv %s')%(kewajiban,kas,pendapatan,mytd,potongan,bulan_invoice))

        elif not last_invoice and hari_jalan>0:
            data_tagihan =self.get_data_angsuran()
                
            bulan_pembiayaan = relativedelta(date.today(),self.tanggal_akad)
            tanggal_inv = date.today()
            tanggal = relativedelta(date.today(),tanggal_inv)

            kewajiban = False
            k_bulan = False
            bulan_biaya = (bulan_pembiayaan.years*12) + bulan_pembiayaan.months
            for bulan in self.product_id.product_tmpl_id.pelunasan_lines:
                if not k_bulan:
                    k_bulan = bulan.periode_min
                #if bulan_pembiayaan.months>=bulan.periode_min and
                if bulan_biaya>=bulan.periode_min and bulan_biaya<=bulan.periode_max:
                    kewajiban = bulan.pelunasan

            pokok_byr = data_tagihan[bulan_biaya]['pokok_pinjaman']
            i = 0
            kas = pokok_byr
            for bl in range(bulan_biaya,self.periode_angsuran):
                pendapatan += self.angsuran
                mytd += data_tagihan[bl]['angsuran_margin']
                if bl>=bulan_biaya+kewajiban:
                    potongan += data_tagihan[bl]['angsuran_margin']
                i+=1

#        else:
#            raise UserError(_('Belum ada Invoice yang dilunasi'))

#        raise UserError(_('kewajiban %s \n kas %s \n mytd %s \n pokok %s \n potongan %s \n margin_bayar %s')%(kewajiban,kas,mytd,pokok,potongan,margin_byr))

        if tanggal_inv:
            coa_debit = self.journal_id.default_debit_account_id
            coa_credit = self.journal_id.default_credit_account_id
            total = self.harga_jual
            margin = amount_total = 0
            invoice_lines = []
            for line in akad_line:
                if line.coa_debet and not line.coa_kredit:
                    coa_name = 'Pelunasan Pokok : ' + self.name + " - " + self.member_id.name
                    invoice_lines += [(0, 0, self._prepare_inv_line(self,coa_name, line.coa_debet.id,kas))]
                    coa_debit = line.coa_debet
                elif line.coa_kredit and margin<=0:
                    margin = pendapatan
                    coa_name = 'Pelunasan Margin : ' + self.name + " - " + self.member_id.name
                    invoice_lines += [(0, 0, self._prepare_inv_line(self,coa_name, line.coa_debet.id,mytd))]
                    #Potongan Pelunasan
                    if potongan>0:
                        coa_name = 'Potongan Pelunasan : ' + self.name + " - " + self.member_id.name
                        invoice_lines += [(0, 0, self._prepare_inv_line(self,coa_name, line.coa_kredit.id,-potongan))]
#            elif line.coa_kredit and margin>0:
#                coa_name = 'Pelunasan Pokok : ' + self.name + " - " + self.member_id.name
#                invoice_lines += [(0, 0, self._prepare_inv_line(self,coa_name, line.coa_debet.id,kas))]

#        raise UserError(_('invoice_lines %s ')%(invoice_lines,))
            
            invoice = inv_obj.create({
                    'date_invoice': tanggal_inv,
                    'name': 'Pelunasan ' + self.name + " : " + self.member_id.name,
                    'origin': self.name,
                    'type': 'out_invoice',
                    'reference': False,
                    'account_id': coa_credit.id,
                    'partner_id': self.member_id.partner_id.id,
                    'invoice_line_ids': invoice_lines,
                    'currency_id': self.currency_id.id,
                    'comment': 'Pelunasan ' + self.name + " : " + self.member_id.name,
                    'payment_term_id': 1,
                    'pembiayaan_id': self.id,
                    'type_journal': 'pelunasan',
                    'operating_unit_id': self.env.user.default_operating_unit_id.id,
                    'mitra_id': self.mitra_id.id,
#                    'mitra_bank_id': self.mitra_bank_id.id,
#                    'loan_id': self.loan_id.id,
#                           'residual': kas+mytd-potongan,
#                           'residual_signed': pokok+pendapatan,
#                           'state': 'open',
                    })

            invoice.action_invoice_open_syariah()   ##invoice.post harus ke syariah

            invoice.message_post_with_view('mail.message_origin_link',
                                values={'self': invoice, 'origin': self},
                                subtype_id=self.env.ref('mail.mt_note').id)
            if sale_order.order_line:
                for so_line in sale_order.order_line:
                    so_line.update({'invoice_lines': [(4,inv.id) for inv in invoice.invoice_line_ids]})
            csql = "update account_invoice set residual=amount_total, residual_signed=amount_total, residual_company_signed=amount_total, state='open' where id=%s"
            self.env.cr.execute(csql, (invoice.id,))

            self._compute_balance()
            self.update({'state': 'close',})
        return

           


    
    def action_create_so(self):
        sale_order_id = self.env['sale.order'].search([('pembiayaan_id','=',self.id)])
        if not sale_order_id:
            order_line = [(0,0,({
                        'product_id': self.product_id.id,
                        'name': self.product_id.name + " : " + self.name + " - " + self.member_id.name,
                        'product_uom_qty': 1,
                        'price_unit': self.harga_jual,
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
                                'client_order_ref': 'Pengadaan '+ self.name,
                                'analytic_account_id': self.account_analytic_id.id,
                                'state': 'sale',
                                'pembiayaan_id': self.id,
                                'user_id': self.env.uid,
                                'confirmation_date': date.today(),
#                                'invoice_status': 'no',
                                            })
            sale_order.action_confirm()

        if self.product_id.qty_available>0: #proses DO
            sale_order.action_view_delivery()
            for picking in sale_order.picking_ids:
                picking.note = 'Pengadaan ' + self.product_id.name + ' : ' + self.name
                for stock_move in picking.move_ids_without_package:
                    stock_move.quantity_done = 1
                                
            sale_order.picking_ids[0].button_validate()
            move = self.env['account.move'].search([('stock_move_id','=',stock_move.id)])
            akad_line = self.env['master.akad_journal'].search([('akad_id','=',self.akad_id.id),
                                                                        ('type_journal','=','pencairan')])
            coa_pokok = coa_margin = coa_mydt = False
            for jline in akad_line:
                if jline.coa_debet and jline.coa_kredit:
                    coa_margin = jline.coa_kredit
                    coa_mydt = jline.coa_debet
                elif jline.coa_kredit:
                    coa_pokok = jline.coa_kredit
                    
            cdebit = ckredit = grdebit = grkredit = 0.0
            cek = cek_gr = aml = []
            partner = False
            ### Update jurnal GR, penambahan POTONGAN ##
            move.update({'state': 'draft'})
            if self.invoice_dp and self.biaya_lines:
                for biaya in self.biaya_lines:
                    potong = biaya.name.find('Potongan')
                    uangmuka = biaya.name.find('Uang Muka')
                    if uangmuka>=0:
                        uang_muka = biaya.subtotal
                        coa_um = biaya.biaya_id.coa_credit
                        coa_um_name = biaya.biaya_id.coa_credit.name + ' ' + self.name
                    elif potong>=0:
                        potongan = biaya.subtotal
                        coa_potongan = biaya.biaya_id.coa_debit
                        coa_name = biaya.biaya_id.coa_debit.name + ' ' + self.name
                po_id = self.env['purchase.order'].search([('pembiayaan_id','=',self.id)])
                st_move = self.env['stock.move'].search([('purchase_line_id','in',tuple(po_id.order_line.ids))])
                gr_move = self.env['account.move'].search([('stock_move_id','in',tuple(st_move.ids))],limit=1)    
                gr_move.update({'state': 'draft'})
                for line in gr_move.line_ids:
                    partner = line.partner_id
                    if line.debit>0:
                        amount = line.debit+potongan
                        csql = """update account_move_line set debit=%s, balance=%s, debit_cash_basis=%s,
                                balance_cash_basis=%s, amount_residual=%s where id=%s"""
                        self.env.cr.execute(csql,(amount,amount,amount,amount,amount,line.id))

                gr_aml = [(0, 0, self._prepare_move_line_syariah(coa_potongan,-potongan,0,False,coa_name,partner))]
                gr_move.update({'line_ids': gr_aml, 'state': 'posted'})
                    
                for line in gr_move.line_ids:
                    potong = line.name.find('Potongan')
                    if potong>=0:
                        line.update({'amount_residual': line.debit})
            ### Update jurnal DO, penambahan POTONGAN ##
                for line in move.line_ids:
                    partner = line.partner_id
                    if line.debit>0:
                        amount = line.debit-uang_muka
                        csql = """update account_move_line set account_id=%s,name=%s,debit=%s, balance=%s, debit_cash_basis=%s,
                                balance_cash_basis=%s, amount_residual=%s where id=%s"""
                        self.env.cr.execute(csql,(coa_pokok.id,coa_pokok.name,amount,amount,amount,amount,amount,line.id))
                        aml += [(0, 0, self._prepare_move_line_syariah(coa_um,uang_muka,0,False,coa_um_name,partner))]
                    elif line.credit>0:
                        amount = line.credit+potongan
                        csql = """update account_move_line set credit=%s, balance=%s, credit_cash_basis=%s,
                                balance_cash_basis=%s, amount_residual=%s where id=%s"""
                        self.env.cr.execute(csql,(amount,-amount,amount,-amount,-amount,line.id))
                        aml += [(0, 0, self._prepare_move_line_syariah(coa_potongan,0,-potongan,False,coa_name,partner))]

                margin = self.harga_jual - self.total_pembiayaan + uang_muka
                        
            else:
                for line in move.line_ids:
                    if line.debit>0:
                        line.update({'account_id': coa_pokok.id,
                                     'name': coa_pokok.name,})

                margin = self.harga_jual - self.total_pembiayaan
            aml += [(0, 0, self._prepare_move_line_syariah(coa_margin,margin,0,False,self.name,partner))]
            aml += [(0, 0, self._prepare_move_line_syariah(coa_mydt,0,margin,False,self.name,partner))]
            move.update({'line_ids': aml,'state': 'posted'})
                
            cek = []
            for line in move.line_ids:
                cek.append({'COA': line.account_id.id,
                            'COA_name': line.account_id.name,
                            'name': line.name,
                            'debit': line.debit,
                            'credit': line.credit,
                            'amount_residual': line.amount_residual,
                            'currency_id': line.currency_id.id,})
                cdebit  += line.debit
                ckredit += line.credit

#            raise UserError(_('DO Entries %s= %s \n debit %s \n credit %s ')%(move.id,cek,cdebit,ckredit,))

#            move = self.create_aml(self.name,False,self.akad_id.tipe) #nilai jurnal pencairan seharusnya harga jual!!!
            ### Pembiayaan Barang ###
            self.write({'state': 'active',
                        'tanggal_akad': date.today(),
                        'balance': self.harga_jual,
                        'move_pencairan': move.id,
                        'delivery': stock_move.id,
                        'last_invoice': date.today(),
                    })
            sale_order.update({'state': 'done','invoice_status': 'no',})
        else:
            if self.peruntukan.tipe!='service':
                raise UserError(_('Belum ada Stock untuk Product %s')%(self.product_id.name,))

     
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
            if self.akad_id.type_akad == 'bil_wakalah' :
                po_obj = self.env['purchase.order']    
                po_lines = self.prepare_po_lines_vals()
                po_vals = self.prepare_po_vals(rekno,po_lines)
                po_vals.update({'state': 'purchase', 'date_approve': date.today()})
                po_dummy = po_obj.create(po_vals)
                self.create_invoice_dp()
                self.action_stock_move()
                self.write({ 'state': 'approve',
                            'balance': self.total_pembiayaan + self.jumlah_biaya,
                            'name': rekno,})   
                
            else :
                invoice = self.proses_pencairan(rekno)
                #self.create_jurnal_margin(rekno)
                #self.create_invoice_angsuran(rekno)
                self.write({ 'state': 'approve',
                            'balance': self.total_pembiayaan + self.jumlah_biaya,
                            'name': rekno,})   
                
    def prepare_po_vals(self,origin,po_lines):
        print ("============po line============", po_lines)
        notes = 'Pengadaan Wakalah ' + origin
        if self.akad_id.tipe=='product':
            notes = 'Pengadaan ' + origin
        return {
                'name': self.env['ir.sequence'].next_by_code('purchase.order'),
                'partner_id': self.vendor_id.id,
                'partner_ref': origin,
                'order_line': po_lines,
                'notes': notes ,
                'date_order': datetime.today(),
                #'account_analytic_id': self.account_analytic_id.id or False,
                'user_id': self.env.uid,
                'payment_term_id': 1,
                'date_approve': datetime.today(),
                'pembiayaan_id': self.id,
                }
    
    
    
    def prepare_po_lines_vals(self):
        po_line_list =[]
        if self.product_id :
            po_line_vals = {
                                'product_id': self.product_id.id,
                                'name': self.product_id.name,
                                'product_qty': 1,
                                'product_uom': self.product_id.uom_po_id.id,
                                'date_planned': datetime.today(),
                                'price_unit': self.total_pembiayaan,
                                }
 
 
            po_line_list = [(0, 0,po_line_vals)]
                
        for deduc in self.deduction_lines :
            if deduc.product_id.add_po :
                po_line_vals = {
                                    'product_id': deduc.product_id.id,
                                    'name': deduc.product_id.name,
                                    'product_qty': 1,
                                    'product_uom': deduc.product_id.uom_po_id.id,
                                    'date_planned': datetime.today(),
                                    'price_unit': deduc.amount,
                                    }
 
 
                po_line_list += [(0, 0,po_line_vals)]
            
             
        return po_line_list
    
    def action_stock_move(self):
        if not self.picking_type_id:
            raise UserError(_(
                " Please select a picking type"))
        for order in self:
            if not self.pembiayaan_picking_id:
                pick = {}
                if self.picking_type_id.code == 'outgoing':
                    pick = {
                        'picking_type_id': self.picking_type_id.id,
                        'partner_id': self.member_id.partner_id.id,
                        'origin': self.name,
                        'location_dest_id': self.member_id.partner_id.property_stock_customer.id,
                        'location_id': self.picking_type_id.default_location_src_id.id,
                        'move_type': 'direct'
                    }
                    
                    picking = self.env['stock.picking'].create(pick)
                    picking.pembiayaan_id = self.id
                    self.pembiayaan_picking_id = picking.id
                    moves = self._create_stock_moves(picking)
                    move_ids = moves._action_confirm()
                    move_ids._action_assign()


#     def _reverse_moves(self, default_values_list=None, cancel=False):
#         ''' Reverse a recordset of account.move.
#         If cancel parameter is true, the reconcilable or liquidity lines
#         of each original move will be reconciled with its reverse's.
# 
#         :param default_values_list: A list of default values to consider per move.
#                                     ('type' & 'reversed_entry_id' are computed in the method).
#         :return:                    An account.move recordset, reverse of the current self.
#         '''
# 
#         if self.picking_type_id.code == 'outgoing':
#             data = self.env['stock.picking.type'].search(
#                 [('company_id', '=', self.company_id.id), ('code', '=', 'incoming')], limit=1)
#             self.picking_type_id = data.id
#         elif self.picking_type_id.code == 'incoming':
#             data = self.env['stock.picking.type'].search(
#                 [('company_id', '=', self.company_id.id), ('code', '=', 'outgoing')], limit=1)
#             self.picking_type_id = data.id
#         reverse_moves = super(SimPinPembiayaan, self)._reverse_moves()
#         return reverse_moves
    
    def _create_stock_moves(self, picking):
        moves = self.env['stock.move']
        done = self.env['stock.move'].browse()
        for line in self:
            if picking.picking_type_id.code == 'outgoing':
                template = {
                    'name': line.name or '',
                    'product_id': line.product_id.id,
                    'product_uom': line.product_id.uom_id.id,
                    'location_id': picking.picking_type_id.default_location_src_id.id,
                    'location_dest_id': line.member_id.partner_id.property_stock_customer.id,
                    'picking_id': picking.id,
                    'state': 'draft',
                    'picking_type_id': picking.picking_type_id.id,
                    'route_ids': 1 and [
                        (6, 0, [x.id for x in self.env['stock.location.route'].search([('id', 'in', (2, 3))])])] or [],
                    'warehouse_id': picking.picking_type_id.warehouse_id.id,
                }
            diff_quantity = 1
            tmp = template.copy()
            tmp.update({
                'product_uom_qty': diff_quantity,
            })
            template['product_uom_qty'] = diff_quantity
            done += moves.create(template)
        return done
    
    
    
#     def prepare_po_lines_vals(self,origin):
#         name = 'Pengadaan Wakalah ' + origin
#         if self.akad_tipe=='product':
#             name = self.notes 
#         return {
#                 'product_id': self.product_id.id,
#                 'name': name,
#                 'product_qty': 1,
#                 'product_uom': self.product_id.uom_po_id.id,
#                 'date_planned': datetime.today(),
#                 'price_unit': self.total_pembiayaan,
#                 #'account_analytic_id': self.account_analytic_id.id or False,
#                 }

    def create_jurnal_margin(self):
        akad_line = self.env['master.akad_journal'].search([('akad_id','=',self.akad_id.id),
                                                            ('type_journal','=','ditangguhkan')], limit=1)
        #coa_name = 'Ditangguhkan : ' + self.name + " - " + self.member_id.name
        coa_name = 'Ditangguhkan : ' + " - " + self.member_id.name
        amount = self.total_pembiayaan - self.harga_jual
        if akad_line :
            debit_account = akad_line.coa_debet
            credit_account = akad_line.coa_kredit

        debit_vals = {
                        'name': 'Margin ditangguhkan',
                        'debit': abs(amount),
                        'credit': 0.0,
                        'account_id': debit_account.id

                        }
        credit_vals = {
                            'name': '',
                            'debit': 0.0,
                            'credit': abs(amount),
                            'account_id': credit_account.id
                        }

        vals =      {   
                        #'name'      : coa_name,
                        'journal_id': 3,
                        'date': date.today(),
                        'state': 'draft',
                        'line_ids': [(0, 0, debit_vals), (0, 0, credit_vals)]
                    }

        move = self.env['account.move'].create(vals)

    def create_jurnal_margin_angsuran(self):
        akad_line = self.env['master.akad_journal'].search([('akad_id','=',self.akad_id.id),
                                                            ('type_journal','=','margin')], limit=1)
        coa_name = 'Margin : ' + self.name + " - " + self.member_id.name
        amount = self.total_pembiayaan - self.harga_jual
        margin_amount = amount / self.periode_angsuran
        if akad_line :
            debit_account = akad_line.coa_debet
            credit_account = akad_line.coa_kredit

        debit_vals = {
                        'name': 'Margin Pencairan',
                        'debit': abs(margin_amount),
                        'credit': 0.0,
                        'account_id': debit_account.id

                        }
        credit_vals = {
                            'name': '',
                            'debit': 0.0,
                            'credit': abs(margin_amount),
                            'account_id': credit_account.id
                        }

        vals =      {   
                        #'name'      : coa_name,
                        'journal_id': 3,
                        'date': date.today(),
                        'state': 'draft',
                        'line_ids': [(0, 0, debit_vals), (0, 0, credit_vals)]
                    }

        move = self.env['account.move'].create(vals)


    def proses_pencairan(self,rekno):
        invoice_lines = inv_lines = []
        coa_debet = coa_credit = False
        if not self.journal_id.default_account_id: # or not self.journal_id.default_credit_account_id:
            raise UserError(_('Konfigurasi Journal belum Sesuai'))
        else:
            coa_debit = self.product_id.property_account_expense_id.id
            coa_name = 'Pencairan : ' + rekno + " - " + self.member_id.name
            coa_credit = self.akad_id.property_account_payable_id.id
                
            invoice_vals_list =[]
            
            invoice_vals = {
                                'product_id': self.product_id.id,
                                'name': self.product_id.name,
                                'account_id': coa_debit,
                                'quantity': 1,
                                'price_unit': self.total_pembiayaan
                                }

            invoice_vals_list.append(invoice_vals)


            invoice_vals = {
                            'partner_id': self.member_id.partner_id.id,
                            'state': 'draft',
                            'name': coa_name,
                            'ref': rekno,
                            'invoice_date': self.tanggal_akad,
                            'move_type': 'in_invoice',
                            'pembiayaan_id' : self.id,
                            'invoice_line_ids': invoice_vals_list
                            }
            invoice = self.env['account.move'].sudo().create(invoice_vals)
            movelines = self.env['account.move.line'].search([('move_id','=',invoice.id),('account_id.code','=','21100010')])
            if movelines:
                movelines.write({'account_id' : coa_credit}) 
            invoice.action_post()
            self.write({
                            'move_pencairan': invoice.id,})

    def create_invoice_angsuran(self):
        for trans in self:
            invoice_vals_list =[]
            if trans.product_id :
                if not trans.product_id.property_account_income_id:
                    raise UserError(_('You must add Income Account Product %s.')%(trans.product_id.name))
            
                bayar_pokok = self.total_pembiayaan / self.periode_angsuran
                invoice_vals = {
                                    'product_id': trans.product_id.id,
                                    'name': trans.product_id.name,
                                    'account_id': trans.product_id.property_account_income_id.id,
                                    'quantity': 1,
                                    'price_unit': bayar_pokok
                                    }

                invoice_vals_list.append(invoice_vals)
                print ("==============inv==============", invoice_vals_list)
                akad_line = self.env['master.akad_journal'].search([('akad_id','=',self.akad_id.id),
                                                            ('type_journal','=','sewa_angsur')], limit=1)

                lebih_bayar =  self.angsuran - bayar_pokok
                if akad_line :
                    credit_account = akad_line.coa_kredit

                invoice_vals = {
                                    'product_id': trans.product_id.id,
                                    'name': trans.product_id.name,
                                    'account_id': credit_account.id,
                                    'quantity': 1,
                                    'price_unit': lebih_bayar
                                    }

                invoice_vals_list.append(invoice_vals)

                print ("==============inv 2==============", invoice_vals_list)

            #coa_name = 'Angsuran Pembiayaan : ' + self.name + " - " + self.member_id.name
            coa_name = 'Angsuran Pembiayaan : ' + " - " + self.member_id.name
            invoice_vals = {
                            'partner_id': self.member_id.partner_id.id,
                            'state': 'draft',
                            #'name': coa_name,
                            'ref': self.name,
                            'invoice_date': self.tanggal_akad,
                            'move_type': 'out_invoice',
                            'pembiayaan_id' : self.id,
                            'invoice_line_ids': invoice_vals_list
                            }

            invoice = self.env['account.move'].sudo().create(invoice_vals)
            movelines = self.env['account.move.line'].search([('move_id','=',invoice.id),('account_id.code','=','11210010')])
            if movelines:
                movelines.write({'account_id' : trans.akad_id.property_account_receivable_id.id}) 
            invoice.action_post()

            print ("==============invoice==============", invoice)
            
    def create_invoice_dp(self):
        for trans in self:
            invoice_vals_list =[]
            for biaya in trans.allowance_lines :
                if biaya.product_id :
                    if not biaya.product_id.property_account_income_id:
                        raise UserError(_('You must add Income Account Product %s.')%(biaya.product_id.name))
                    invoice_vals = {
                                        'product_id': biaya.product_id.id,
                                        'name': biaya.product_id.name,
                                        'account_id': biaya.product_id.property_account_income_id.id,
                                        'quantity': 1,
                                        'price_unit': biaya.amount
                                        }
    
                    invoice_vals_list.append(invoice_vals)
            for deduc in trans.deduction_lines :
                if deduc.product_id :
                    if not deduc.product_id.property_account_expense_id:
                        raise UserError(_('You must add Income Account Product %s.')%(deduc.product_id.name))
                    invoice_vals = {
                                        'product_id': deduc.product_id.id,
                                        'name': deduc.product_id.name,
                                        'account_id': deduc.product_id.property_account_expense_id.id,
                                        'quantity': 1,
                                        'price_unit': deduc.amount
                                        }
    
                    invoice_vals_list.append(invoice_vals)

            coa_name = 'Angsuran Pembiayaan : ' + " - " + self.member_id.name
            invoice_vals = {
                            'partner_id': self.member_id.partner_id.id,
                            'state': 'draft',
                            #'name': coa_name,
                            'ref': self.name,
                            'invoice_date': self.tanggal_akad,
                            'move_type': 'out_invoice',
                            'pembiayaan_id' : self.id,
                            'invoice_line_ids': invoice_vals_list
                            }

            invoice = self.env['account.move'].sudo().create(invoice_vals)
            movelines = self.env['account.move.line'].search([('move_id','=',invoice.id),('account_id.code','=','11210010')])
            if movelines:
                movelines.write({'account_id' : trans.akad_id.property_account_receivable_id.id}) 
            invoice.action_post()

            print ("==============invoice==============", invoice)
            

#    
    @api.onchange('mitra_bank_id')
    def onchange_mitra_bank_id(self):
        if self.mitra_bank_id:
            self.update({'biaya_lines': False,})
            biaya_lines = []
            for biaya in self.mitra_bank_id.biaya_lines:
                harga = subtotal = 0.0
                is_um = False
                if biaya.nilai_pct>0:
                    harga = round(self.total_pembiayaan * (biaya.nilai_pct/100),0)
                elif biaya.nominal>0:
                    harga = biaya.nominal

                if biaya.tipe=='uangmuka':
                    is_um = True

                subtotal = harga * 1
                biaya_lines += [(0,0,{'name': biaya.name,
                                      'pembiayaan_id': self.id,
                                      'quantity': 1,
                                      'nilai_pct': biaya.nilai_pct,
                                      'is_edit': biaya.is_edit,
                                      'is_um': is_um,
                                      'harga': harga,
                                      'biaya_id': biaya.id,
                                      'subtotal': subtotal,
                                      })]
            self.update({'biaya_lines': biaya_lines,})
            self.jurnal_biaya = 'biaya_bank'
#            raise UserError(_('biaya_lines %s = %s')%(self.mitra_bank_id,biaya_lines,))
#        else:
#            self.update({'biaya_lines': False,})
#            self.jurnal_biaya = False

        self.cek_komponen_biaya()                
            
 #   
    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            if not self.product_id.jenis_syariah:
                self.akad_id = self.product_id.jenis_syariah.id
            else:
                self.akad_id = False
        
        self.cek_komponen_biaya()
        self.onchange_mitra_bank_id()


    def cek_komponen_biaya(self):
        if self.akad_id and len(self.product_id.product_tmpl_id.biaya_lines)>0 and self.akad_id.name.upper()=='MURABAHAH' and not self.mitra_bank_id:
            biaya_lines = []
            self.update({'allowance_lines': False,})
            for biaya in self.product_id.product_tmpl_id.biaya_lines:
                harga = subtotal = 0.0
                if biaya.nilai_pct>0:
                    harga = round(self.total_pembiayaan * (biaya.nilai_pct/100),0)
                elif biaya.nominal!=0:
                    harga = biaya.nominal

                subtotal = harga * 1
                biaya_lines += [(0,0,{
                                      'pembiayaan_id': self.id,
                                      'persen': biaya.nilai_pct,
                                      'amount': harga,
                                      'product_id': biaya.product_id.id,
                                      })]
            self.update({'allowance_lines': biaya_lines,'jurnal_biaya': 'biaya_murabahah'})
        elif not self.mitra_bank_id:
            self.update({'allowance_lines': False,})
            self.jurnal_biaya = False

    # def cek_komponen_biaya(self):
    #     if self.akad_id and len(self.product_id.product_tmpl_id.biaya_lines)>0 and self.akad_id.name.upper()=='MURABAHAH' and not self.mitra_bank_id:
    #         biaya_lines = []
    #         self.update({'biaya_lines': False,})
    #         for biaya in self.product_id.product_tmpl_id.biaya_lines:
    #             harga = subtotal = 0.0
    #             is_um = False
    #             if biaya.nilai_pct>0:
    #                 harga = round(self.total_pembiayaan * (biaya.nilai_pct/100),0)
    #             elif biaya.nominal!=0:
    #                 harga = biaya.nominal

    #             if biaya.tipe=='uangmuka':
    #                 is_um = True

    #             subtotal = harga * 1
    #             biaya_lines += [(0,0,{'name': biaya.name,
    #                                   'pembiayaan_id': self.id,
    #                                   'quantity': 1,
    #                                   'nilai_pct': biaya.nilai_pct,
    #                                   'is_edit': biaya.is_edit,
    #                                   'is_um': is_um,
    #                                   'harga': harga,
    #                                   'biaya_id': biaya.id,
    #                                   'subtotal': subtotal,
    #                                   })]
    #         self.update({'biaya_lines': biaya_lines,'jurnal_biaya': 'biaya_murabahah'})
    #     elif not self.mitra_bank_id:
    #         self.update({'biaya_lines': False,})
    #         self.jurnal_biaya = False
        
#    
    @api.onchange('vendor_id')
    def _onchange_vendor_id(self):
        t_domain = False
        if self.vendor_id:
            rek_vendor = self.env['res.partner.bank'].search([('partner_id','=',self.vendor_id.id)])
            t_domain = {'domain': {'vendor_bank_id': [('id', 'in', rek_vendor.ids)]}}
            self.vendor_bank_id = False
        return t_domain

    @api.onchange('akad_id')
    def _onchange_akad_id(self):
        t_domain = False
#        if self.akad_id:
#            product = self.env['product.product'].search([('is_syariah', '=', True),('active', '=', True),('state', '=', 'open'),
#                                                      ('jenis_syariah', '=', self.akad_id.id),
##                                                      '|',('product_tmpl_id.categ_id.parent_id.name', '=', 'Pembiayaan'),
##                                                      ('product_tmpl_id.categ_id.name', '=', 'Pembiayaan')
#                                                          ])
#        else:
#            product = self.env['product.product'].search([('is_syariah', '=', True),('active', '=', True),('state', '=', 'open'),
##                                                      ('jenis_syariah', '=', self.akad_id.id),
#                                                      '|',('product_tmpl_id.categ_id.parent_id.name', '=', 'Pembiayaan'),
#                                                      ('product_tmpl_id.categ_id.name', '=', 'Pembiayaan')
#                                                          ])
#        t_domain = {'domain': {'product_id': [('id', 'in', product.ids)]}}
        self.cek_komponen_biaya()                

        return t_domain

#     @api.onchange('peruntukan')
#     def _onchange_peruntukan(self):
#         t_domain = False
#         product = self.env['product.product'].search([('is_syariah', '=', True),('active', '=', True),('state', '=', 'open'),
#                                                       ('product_tmpl_id.type', '=', self.peruntukan.tipe),
#                                                       '|',('product_tmpl_id.categ_id.parent_id.name', '=', 'Pembiayaan'),
#                                                       ('product_tmpl_id.categ_id.name', '=', 'Pembiayaan')
#                                                           ])
#         akad = self.env['master.akad_syariah'].search([('is_actived', '=', True),
#                                                            ('tipe', '=', self.peruntukan.tipe),
#                                                           '|',('category_id.parent_id.name', '=', 'Pembiayaan'),
#                                                           ('category_id.name', '=', 'Pembiayaan')
#                                                            ])
#         if product:
#             self.product_id = product[0].id
#         else:
#             self.product_id = False
# 
#         self.cek_komponen_biaya()                
# 
#         if akad:
#             self.akad_id = akad[0].id
#             
#         t_domain = {'domain': {'product_id': [('id', 'in', product.ids)], 'akad_id': [('id', 'in', akad.ids)]}}
# 
#         if self.product_id.product_tmpl_id.type=='product' and self.peruntukan.tipe=='product':
#             self.akad_tipe='product'
#         else:
#             self.akad_tipe='service'
# 
# #        if self.product_id and self.product_id.product_tmpl_id.type=='product':
# #            self.total_pembiayaan = self.product_id.product_tmpl_id.list_price
# #        else:
# #            self.total_pembiayaan = 5000000
# 
#         return t_domain

    
    
    def action_submit(self):
        self.calc_total_pembiayaan()
        cash_rasio = False
        cash_ratio = self.env['master.general'].search([('type_umum','=','cash_ratio')],order='id',limit=1)
        if not cash_ratio:
            raise UserError(_('Cash Ratio belum ada, Harap Melakukan Konfigurasi'))
        else:
            cash_rasio = cash_ratio[0].nominal
        self._onchange_thp_gaji()

        if self.cash_ratio>cash_rasio:
            raise UserError(_('Cash Ratio Melebihi Batasan %s Persen')%(cash_ratio[0].nominal,))
        elif self.thp_gaji==0 or self.cash_ratio==100:
            raise UserError(_('THP Gaji Wajib memiliki Nilai'))
            
        self.update({'state': 'submit'})

    
    def action_check(self):
        self.write({'state': 'check'})

    
    def action_active(self):
        raise UserError('Sub Modul Pencairan Pembiayaan')
        self.write({'state': 'active'})


    
    def create_invoice_syariah_daily(self):
        date_today = date.today()
        pembiayaan = self.env['simpin_syariah.pembiayaan'].search([('state','=','active'),('last_invoice','<',date_today)])
        counter = 0

        if pembiayaan and date_today.day>=12:
            for line in pembiayaan:
                end_periode = relativedelta(date_today,line.tanggal_akad) 
                end_month = end_periode.years*12 + end_periode.months +1
#                raise UserError(_('end %s == %s')%(end_month,line.periode_angsuran))
                last_invoice = self.env['account.invoice'].search([('pembiayaan_id','=',line.id),
                                                                   ('state','in',['open','paid']),('type_journal','=','tagihan'),
                                                                   ('type','=','out_invoice'),],order="id desc")
                if last_invoice:
                    last_tagihan = relativedelta(date_today,last_invoice[0].date_invoice)
#                raise UserError(_('rec last_tagihan %s = %s')%(last_tagihan.months,line.last_invoice))

                if end_month>line.periode_angsuran and line.tunggakan==0 and line.balance==0:
                    line.update({'state': 'close'})
#                    raise UserError(_('pembiayaan %s - end %s')%(line,end_periode,))
                elif line.last_invoice and last_tagihan.months>=1:
#                    raise UserError(_('pembiayaan %s - end %s')%(line,end_periode,))
                    data_inv = line.create_invoice_syariah_migrasi()  ###
                
                    counter += 1
                if counter>100:
                    break

#    
    def create_inv_dp(self,biaya_lines):
        invoice_lines = []
        for line in biaya_lines:
            if line.harga > 0:
                coa = line.biaya_id.coa_credit.id
            else:
                coa = line.biaya_id.coa_debit.id

            invoice_lines += [(0, 0,{
                'name': line.name,
                'origin': self.name,
                'account_id': coa,
                'price_unit': line.harga,
                'quantity': 1.0,
                'discount': 0.0,
                'product_id': self.product_id.id,
                'account_analytic_id': self.account_analytic_id.id or False,
                'operating_unit_id': self.env.user.default_operating_unit_id.id,
                }
                )]
        invoice = self.env['account.invoice'].create({
                        'date_invoice': date.today(),
                        'name': " Uang Muka " + self.product_id.name,
                        'origin': self.name,
                        'type': 'out_invoice',
                        'reference': False,
                        'account_id': self.journal_id.default_credit_account_id.id,
                        'partner_id': self.member_id.partner_id.id,
                        'invoice_line_ids': invoice_lines,
                        'currency_id': self.currency_id.id,
                        'comment': 'Uang Muka ' + self.product_id.product_tmpl_id.name + " : " + self.member_id.name,
                        'payment_term_id': 1,
                        'pembiayaan_id': self.id,
                        'type_journal': 'biaya_bank',
#                        'pembiayaan_id': self.id,
#                        'type_journal': 'tagihan',
#                        'residual': biaya.angsuran,
#                        'residual_signed': biaya.angsuran,
#                        'mitra_id': biaya.member_id.mitra_id.id,
#                           'state': 'open',
                        })

        invoice.action_invoice_open_syariah()   ##invoice.post harus ke syariah

        return invoice


###### Button Modif Journal Pembiayaan BDS
    
    def button_modif(self):
        pembiayaan = pencairan = pengajuan = False
        pembiayaan = self.env['simpin_syariah.pembiayaan'].search([('product_id','in',[254,255]),
                                                                   ('state','=','active')])
        payment_id = invoice_id = False
        for rec in pembiayaan:
            cek_inv = []
            cek_pay = []
            coa_transfer = self.env['account.account'].search([('id','=',402)]) 
            coa_hutang = rec.akad_id.journal_id.default_debit_account_id
            tf_new = 2900.0
            tf_res = 4600.0

            for line in rec.move_pencairan.line_ids:
                if line.payment_id:
                    payment_id = line.payment_id
                if line.invoice_id:
                    invoice_id = line.invoice_id

            for line in invoice_id.move_id.line_ids:
                if line.account_id.id==coa_transfer.id:
                    csql = "update account_move_line set credit=%s, balance=%s, credit_cash_basis=%s, balance_cash_basis=%s where id=%s"
                    self.env.cr.execute(csql, (tf_new,-tf_new,tf_new,-tf_new, line.id,))
                    csql = "update account_invoice_line set price_unit=%s, price_subtotal=%s, price_total=%s, price_subtotal_signed=%s where invoice_id=%s and account_id=%s"
                    self.env.cr.execute(csql, (-tf_new,-tf_new,-tf_new,-tf_new, invoice_id.id,coa_transfer.id))

                if line.account_id.id==coa_hutang.id:
                    new_amount = line.credit + tf_res
                    csql = "update account_move_line set credit=%s, balance=%s, credit_cash_basis=%s, balance_cash_basis=%s where id=%s"
                    self.env.cr.execute(csql, (new_amount,-new_amount,new_amount,-new_amount, line.id,))
                    invoice_id.update({'amount_untaxed': new_amount,'amount_untaxed_signed': new_amount,'amount_total': new_amount,'amount_total_signed': new_amount,'amount_total_company_signed': new_amount,})

            for line in invoice_id.move_id.line_ids:
                cek_inv.append({'COA': line.account_id.name,
                            'desc': line.name,
                            'debit': line.debit,
                            'credit': line.credit,
                            'balance': line.balance,
                            'debit_cash_basis': line.debit_cash_basis,
                            'credit_cash_basis': line.credit_cash_basis,
                            'balance_cash_basis': line.balance_cash_basis,
                            'amount_residual': line.amount_residual,
                            'currency_id': line.currency_id.id,})


            aml_cek = self.env['account.move.line'].search([('payment_id','=',payment_id.id)])
            for line in aml_cek:
                if line.account_id.id==payment_id.journal_id.default_debit_account_id.id:
                    new_amount = line.credit + tf_res
                    csql = "update account_move_line set credit=%s, balance=%s, credit_cash_basis=%s, balance_cash_basis=%s where id=%s"
                    self.env.cr.execute(csql, (new_amount,-new_amount,new_amount,-new_amount, line.id,))

                if line.account_id.id==coa_hutang.id:
                    new_amount = line.debit + tf_res
                    csql = "update account_move_line set debit=%s, balance=%s, debit_cash_basis=%s, balance_cash_basis=%s where id=%s"
                    self.env.cr.execute(csql, (new_amount,new_amount,new_amount,new_amount, line.id,))
                    csql = "update account_partial_reconcile set amount=%s where debit_move_id=%s"
                    self.env.cr.execute(csql, (new_amount, line.id,))

            for line in aml_cek:
                cek_pay.append({'COA': line.account_id.name,
                            'desc': line.name,
                            'debit': line.debit,
                            'credit': line.credit,
                            'balance': line.balance,
                            'debit_cash_basis': line.debit_cash_basis,
                            'credit_cash_basis': line.credit_cash_basis,
                            'balance_cash_basis': line.balance_cash_basis,
                            'amount_residual': line.amount_residual,
                            'currency_id': line.currency_id.id,})
#            raise UserError(_('jurnal invoice %s \n payment %s')%(cek_inv,cek_pay,))
#            break

    
    def create_invoice_syariah_migrasi(self):
        res = last_tagih = bln_inv = False
#        raise UserError(_('non schedule self %s')%(self,))
        biaya = self
            
        sale_order = self.env['sale.order'].search([('pembiayaan_id','=',biaya.id)])
        inv_obj = self.env['account.invoice']

        coa_debet = coa_credit = False
        invoice_lines = []
        akad_line = self.env['master.akad_journal'].search([('akad_id','=',biaya.akad_id.id),
                                                            ('type_journal','=','tagihan')])

        total_tagihan = angsuran_lain = angsuran_pokok= 0
        angsuran = biaya.angsuran
        tanggal_inv = False

        if akad_line and biaya.tanggal_akad and biaya.state=='active' and biaya.balance>biaya.tunggakan:
            last_invoice = self.env['account.invoice'].search([('pembiayaan_id','=',biaya.id),
                                                               ('state','in',['open','paid']),('type_journal','=','tagihan'),
                                                               ('type','=','out_invoice'),],order="id desc")
            pokok_pinjaman = biaya.total_pembiayaan
            angsuran_lain = round(pokok_pinjaman * (biaya.margin/1200),0)
            angsuran_pokok = angsuran - angsuran_lain
            umur_inv = 0
            if last_invoice:
                last_tagihan = relativedelta(last_invoice[0].date_invoice,biaya.tanggal_akad)
                bulan = last_tagihan.years*12 + last_tagihan.months 

                for ll_inv in range(1,bulan):
                    total_tagihan += biaya.angsuran
                    pokok_pinjaman -= angsuran_pokok
                    angsuran_lain = round(pokok_pinjaman * (biaya.margin/1200),0)
                    angsuran_pokok = angsuran - angsuran_lain

                data_angsuran = biaya.get_data_angsuran()
                if bulan<len(data_angsuran):
#                    raise UserError(_('bulan %s \n pembiayaan_id %s %s ')%(bulan,biaya.id,biaya.name))
                    angsuran_pokok = data_angsuran[bulan]['angsuran_pokok'] 
                    angsuran_lain = data_angsuran[bulan]['angsuran_margin']
                
                    if biaya.tunggakan < biaya.balance or biaya.balance==0:
                        tanggal_inv = last_invoice[0].date_invoice + relativedelta(months=1)
                    elif biaya.tunggakan == biaya.balance:
                        tanggal_inv = last_invoice[0].date_invoice
                        last_tagih = True
                    else:
                        tanggal_inv = False
#                   raise UserError(_('Inv nama %s \n bulan_jalan %s=%s \n total_tagihan %s \n angsuran_pokok %s \n angsuran_lain %s')%(self.id,bulan_jalan,bulan,total_tagihan,angsuran_pokok,angsuran_lain,))
            else:
                tanggal_migrasi = date.today()  #####datetime.strptime('2021-03-22 00:00:00','%Y-%m-%d %H:%M:%S')
                bulan_jalan = relativedelta(tanggal_migrasi,biaya.tanggal_akad)
                bulan = 1
#                raise UserError(_('bulan_jalan %s = %s')%(bulan_jalan,bulan,))
            
                for ll_inv in range(1,bulan):
                    total_tagihan += biaya.angsuran
                    pokok_pinjaman -= angsuran_pokok
                    angsuran_lain = round(pokok_pinjaman * (biaya.margin/1200),0)
                    angsuran_pokok = angsuran - angsuran_lain
                
                tanggal_inv = biaya.tanggal_akad + relativedelta(months=bulan)
#                raise UserError(_('NoInv nama %s \n bulan_jalan %s=%s \n total_tagihan %s \n angsuran_pokok %s \n angsuran_lain %s')%(biaya.member_id.name,bulan_jalan,bulan,total_tagihan,angsuran_pokok,angsuran_lain,))

            if tanggal_inv:
                coa_debit = biaya.journal_id.default_debit_account_id
                coa_credit = biaya.journal_id.default_credit_account_id
                total = biaya.harga_jual
                margin = 0
                for line in akad_line:
                    if line.coa_debet and line.coa_kredit:
                        margin = angsuran_lain
                        coa_name = 'Angsuran Margin : ' + biaya.name + " - " + biaya.member_id.name
                        invoice_lines += [(0, 0, self._prepare_inv_line(biaya,coa_name, line.coa_debet.id,angsuran_lain ))]
                    elif line.coa_debet:
                        coa_name = 'Angsuran Pokok : ' + biaya.name + " - " + biaya.member_id.name
                        invoice_lines += [(0, 0, self._prepare_inv_line(biaya,coa_name, line.coa_debet.id,angsuran_pokok))]

                tanggal = relativedelta(date.today(),tanggal_inv)
                if last_invoice:
#                    bln_inv = date.today().month-last_invoice[0].date_invoice.month
                    bln_inv = (date.today().year*12 + date.today().month)-((last_invoice[0].date_invoice.year * 12) + last_invoice[0].date_invoice.month)
                else:
                    bln_inv = 1

#                raise UserError(_('pembiayaan %s \n tanggal %s \n bln_inv %s \n last_tagih %s \n angsuran_lain %s \n angsuran_pokok %s ')%(str(biaya.id) + biaya.name,tanggal_inv,bln_inv,last_tagih,angsuran_lain,angsuran_pokok,))

                if (tanggal.days>=0 or bln_inv>=1) and angsuran_pokok<biaya.angsuran and not last_tagih:
#                    raise UserError(_('cr_inv tanggal %s \n bln_inv %s \n last_tagih %s')%(tanggal.days,bln_inv,last_tagih,))
                    invoice = inv_obj.create({
                        'date_invoice': tanggal_inv,
                        'name': biaya.name + " : " + biaya.member_id.name,
                        'origin': biaya.name,
                        'type': 'out_invoice',
                        'reference': False,
                        'account_id': coa_credit.id,
                        'partner_id': biaya.member_id.partner_id.id,
                        'invoice_line_ids': invoice_lines,
                        'currency_id': biaya.currency_id.id,
                        'comment': 'Angsuran ' + biaya.name + " : " + biaya.member_id.name,
                        'payment_term_id': 1,
                        'pembiayaan_id': biaya.id,
                        'type_journal': 'tagihan',
                        'residual': biaya.angsuran,
                        'residual_signed': biaya.angsuran,
                        'mitra_id': biaya.mitra_id.id,
#                        'mitra_bank_id': biaya.mitra_bank_id.id,
#                        'loan_id': biaya.loan_id.id,
#                           'state': 'open',
                        })

                    if invoice.amount_total<=0:
                        raise UserError(_('pembiayaan id %s \n Invoice Amount %s \n Pokok %s \n Margin %s')%(biaya.id,invoice.amount_total,angsuran_pokok,angsuran_lain,))
                    invoice.action_invoice_open_syariah()   ##invoice.post harus ke syariah
                    biaya.update({'last_invoice': tanggal_inv,})
#                    raise UserError(_('invoice %s : %s = %s')%(str(biaya.id) + ' ' + biaya.name,invoice,invoice.amount_total,))
                    print('invoice ',str(biaya.id) + ' ' + biaya.name,invoice,invoice.amount_total)

                    invoice.message_post_with_view('mail.message_origin_link',
                                    values={'self': invoice, 'origin': biaya},
                                    subtype_id=self.env.ref('mail.mt_note').id)
                    for so_line in sale_order.order_line:
                        so_line.update({'invoice_lines': [(4,inv.id) for inv in invoice.invoice_line_ids]})
                    for pick_line in sale_order.picking_ids:
                        if pick_line.state=='done':
                            sale_order.update({'invoice_status': 'no','state': 'done',})
                            break
                    csql = "update account_invoice set residual=%s, residual_signed=%s, residual_company_signed=%s, state='open' where id=%s"
                    self.env.cr.execute(csql, (biaya.angsuran,biaya.angsuran,biaya.angsuran,invoice.id,))
                    res = invoice

        biaya._compute_balance()
        return res

    def _prepare_inv_line(self, line, name, coa, amount,rekno=False):
        '''
        This function prepares move line of account.move related to an cash_advance
        '''
        origin = line.name
        if rekno:
            origin=rekno
            
        return {
                'name': name,
                'origin': origin,
                'account_id': coa,
                'price_unit': amount,
                'quantity': 1.0,
                'discount': 0.0,
                'product_id': line.product_id.id,
                'account_analytic_id': line.account_analytic_id.id or False,
                'operating_unit_id': self.env.user.default_operating_unit_id.id,
                }

class PembiayaanBiaya(models.Model):
    _name = "pembiayaan.biaya"
    _description = "Komponen Biaya Pembiayaan Anggota Simpin Syariah"


    @api.model
    def _default_currency(self):
        return self.env.user.company_id.currency_id.id

    name = fields.Char(string='Item Biaya')
    pembiayaan_id = fields.Many2one('simpin_syariah.pembiayaan',string='Pembiayaan',track_visibility='onchange')
    biaya_id = fields.Many2one('mitra_bank.biaya',string='Pembiayaan',track_visibility='onchange')
    quantity = fields.Integer(string='Qty',track_visibility='onchange', default=1)
    harga = fields.Monetary(string='Jumlah', currency_field='currency_id', track_visibility='onchange')
    subtotal = fields.Monetary(string='Sub Total', compute='_compute_harga', currency_field='currency_id', track_visibility='onchange')
    currency_id = fields.Many2one('res.currency', string="Currency", readonly=True, default=_default_currency)
    nilai_pct = fields.Float(string='Pct(%)',store=True,track_visibility='onchange')
    is_edit = fields.Boolean(string='Editable', related='biaya_id.is_edit',store=True,track_visibility='onchange')
    is_um = fields.Boolean(string='Uang Muka', default=False,store=True,track_visibility='onchange')
#    biaya_bank_id = fields.Many2one('mitra_bank.biaya',string='Biaya Bank id',required=True,store=True)

    
    
    @api.depends('quantity','harga')
    def _compute_harga(self):
        self.subtotal = float(self.quantity) * float(self.harga)

   
    @api.onchange('quantity')
    def _onchange_quantity(self):
        self.subtotal = float(self.quantity) * float(self.harga)

    @api.onchange('harga')
    def _onchange_quantity(self):
        self.subtotal = float(self.quantity) * float(self.harga)

    @api.onchange('nilai_pct')
    def _onchange_nilai_pct(self):
        self.harga = round(float(self.nilai_pct/100) * float(self.pembiayaan_id.total_pembiayaan),0)

class PembiayaanBiayaDeduction(models.Model):
    _name = "pembiayaan.biaya.deduction"
    _description = "Komponen Biaya Pembiayaan Deduction Anggota Simpin Syariah"
    
    product_id = fields.Many2one('product.product', string='Componen')
    amount = fields.Float('Amount')
    persen = fields.Float('Persen(%)')
    pembiayaan_id = fields.Many2one('simpin_syariah.pembiayaan',string='Pembiayaan',track_visibility='onchange')
    
    @api.onchange('persen')
    def _onchange_persen(self):
        for x in self :
            x.amount = 0
            if x.persen > 0 :
                harga = round(x.pembiayaan_id.total_pembiayaan * (x.persen/100),0)
                x.amount = harga
            # else :
            #     harga = round((x.amount/x.pembiayaan_id.total_pembiayaan) ,0)
            #     x.persen = harga

    @api.onchange('amount')
    def _onchange_amount(self):
        for x in self :
            x.persen = 0
            if x.amount !=0:
                harga = round((x.amount/x.pembiayaan_id.total_pembiayaan) * 100 ,0)
                x.persen = harga
            # else :
            #     x.amount = 0
            #     x.persen = 0





        
class PembiayaanBiayaAllowance(models.Model):
    _name = "pembiayaan.biaya.allowance"
    _description = "Komponen Biaya Pembiayaan Allowance Anggota Simpin Syariah"
    
    product_id = fields.Many2one('product.product', string='Componen')
    amount = fields.Float('Amount')
    persen = fields.Float('Persen(%)')
    pembiayaan_id = fields.Many2one('simpin_syariah.pembiayaan',string='Pembiayaan',track_visibility='onchange')
    
    
    
    
    
