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
from odoo.addons import decimal_precision as dp

from werkzeug.urls import url_encode
from dateutil.relativedelta import relativedelta

class MasterKodeTransaksi(models.Model):
    _name = "master.kode_transaksi"
    _description = "Kode Transaksi"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _order = "kode_trx"


    name = fields.Char(string='Nama Transaksi', required=True, track_visibility='onchange')
    kode_trx = fields.Char(string='Kode Transaksi', required=True, track_visibility='onchange')
    journal_id = fields.Many2one('account.journal', required=True, string='Journal', track_visibility='onchange')
    keterangan = fields.Text(string='Keterangan')

    _sql_constraints = [
        ('kode_uniq', 'unique(kode_trx)', 'Kode Transaksi must be unique!'),
    ]

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('kode_trx', '=ilike', name + '%'), ('name', operator, name)]
            if operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = ['&', '!'] + domain[1:]
        akad = self.search(domain + args, limit=limit)
        return akad.name_get()

    
    @api.depends('name', 'kode')
    def name_get(self):
        result = []
        for kode_trx in self:
            name = '[' + kode_trx.kode_trx + '] ' + kode_trx.name
            result.append((kode_trx.id, name))
        return result

class MasterGeneral(models.Model):
    _name = "master.general"
    _description = "tabel umum"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "type_umum"

    name = fields.Char(string='Deskripsi', copy=False,default=lambda self: _('Deskripsi'), required=True)
    type_umum = fields.Selection([
        ('agama', 'Agama'),
        ('identitas', 'Identitas'),
        ('gender', 'Jenis Kelamin'),
        ('marital', 'Status Perkawinan'),
        ('jabatan_id', 'Jabatan'),
        ('ahliwaris', 'Ahli Waris'),
        ('peruntukan', 'Peruntukan'),
        ('paket_investasi', 'Paket Investasi'),
        ('nisbah', 'Limit Nisbah Investasi'),
        ('setoran', 'Setoran Minimal'),
        ('cash_ratio', 'Cash Ratio'),
        ('lain', 'Lainnya'),
        ], string='Type', copy=False, index=True, required=True)
    akad_id = fields.Many2one('master.akad_syariah',string='Jenis Akad', 
                               track_visibility='onchange')
    tipe = fields.Selection([
        ('product', 'Barang'),
        ('service', 'Jasa')], string='Product Type', default='service',track_visibility='onchange')
    nominal = fields.Float(string='Nominal')
    journal_id = fields.Many2one('account.journal', string='Journal Simpanan')
    is_korporasi = fields.Boolean(string='Korporasi',default=False)

class AkadSyariah(models.Model):
    _name = "master.akad_syariah"
    _description = "Master Akad Syariah"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _order = "name"

    def _get_default_category_id(self):
        if self._context.get('categ_id') or self._context.get('default_categ_id'):
            return self._context.get('categ_id') or self._context.get('default_categ_id')
        category = self.env.ref('product.product_category_all', raise_if_not_found=False)
        if not category:
            category = self.env['product.category'].search([], limit=1)
        if category:
            return category.id
        else:
            err_msg = _('You must define at least one product category in order to be able to create products.')
            redir_msg = _('Go to Internal Categories')
            raise RedirectWarning(err_msg, self.env.ref('product.product_category_action_form').id, redir_msg)


    name = fields.Char(string='Name', required=True, copy=False, index=True, default=lambda self: _('New'))
    kode = fields.Char(string='Kode', size=4, copy=False, index=True, default=lambda self: _('New'))
    is_actived = fields.Boolean(string='Active', required=True, copy=False, default=True)
    description = fields.Text(string='Description')
    category_id = fields.Many2one(
        'product.category', 'Product Category',
        change_default=True, default=_get_default_category_id,
        required=True, help="Select category for the current product")
    journal_lines = fields.One2many('master.akad_journal','akad_id',string='Journal Lines')
    tipe = fields.Selection([
        ('product', 'Barang'),
        ('service', 'Jasa'),
        ], string='Product Type', default='service', required=True)
    journal_id = fields.Many2one('account.journal', required=True, string='Default Journal', track_visibility='onchange')
    jenis_sewa = fields.Selection([
        ('nonsewa', 'Non Ijarah'),
        ('sewa', 'Ijarah'),
        ('sewabeli', 'Ijarah Muntahiyah Bittamlik (IMBT)'),
        ], string='Jenis Ijarah', default='nonsewa', required=True)
    type_akad = fields.Selection([
        ('wajib', 'Simpanan Wajib'),
        ('pokok', 'Simpanan Pokok'),
        ('sukarela', 'Simpanan Sukarela'),
	('hariraya', 'Simpanan Hari Raya'),
        ('pinjaman', 'Pinjaman'),
        ('pembiayaan', 'Pembiayaan'),
        ('bil_wakalah', 'Pembiayaan Bil Wakalah'),
        ], string='Type Akad', required=True)
    property_account_payable_id = fields.Many2one('account.account', company_dependent=True,
        string="Account Payable",
        domain="[('internal_type', '=', 'payable'), ('deprecated', '=', False), ('company_id', '=', current_company_id)]",
        help="This account will be used instead of the default one as the payable account for the current partner",
        required=True)
    property_account_receivable_id = fields.Many2one('account.account', company_dependent=True,
        string="Account Receivable",
        domain="[('internal_type', '=', 'receivable'), ('deprecated', '=', False), ('company_id', '=', current_company_id)]",
        help="This account will be used instead of the default one as the receivable account for the current partner",
        required=True)
    
    _sql_constraints = [
        ('kode_uniq', 'unique(kode)', 'Kode Akad must be unique!'),
    ]


    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('kode', '=ilike', name + '%'), ('name', operator, name)]
            if operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = ['&', '!'] + domain[1:]
        akad = self.search(domain + args, limit=limit)
        return akad.name_get()

    
    @api.depends('name', 'kode')
    def name_get(self):
        result = []
        for akad in self:
            name = '[' + akad.kode + '] ' + akad.name
            result.append((akad.id, name))
        return result
    

class AkadJournal(models.Model):
    _name = "master.akad_journal"
    _description = "Master Journal Akad"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _order = "type_journal,id asc"


    name = fields.Char(string='Description', required=True, copy=False, index=True, default=lambda self: _('Journal Default'))
    akad_id = fields.Many2one('master.akad_syariah',string='Akad Syariah', ondelete="cascade")
    type_journal = fields.Selection([
        ('setoran', 'Setoran Simpanan/Investasi'),
        ('tarikan', 'Tarikan Simpanan/Investasi'),
        ('terima_um', 'Penerimaan Uang Muka'),
        ('terima_invest', 'Penerimaan Investasi'),
        ('perolehan_aset_jasa', 'Perolehan Aset/Jasa'),
        ('biaya_bank', 'Biaya Bank'),
        ('pencairan', 'Pencairan'),
        ('ditangguhkan', 'Margin Ditangguhkan'),
        ('margin', 'Margin'),
        ('bayar_untung', 'Pembayaran Keuntungan'),
        ('balik_modal', 'Pengembalian Modal'),
        ('um_bayar_piutang', 'UM sebagai Pembayaran Piutang'),
        ('tagihan', 'Tagihan'),
        ('sewa_angsur', 'Penerimaan Angsuran/Sewa'),
        ('sewa_akhir', 'Penerimaan Angsuran/Sewa Akhir'),
        ('pelunasan', 'Percepatan Pelunasan'),
        ('pengakuan_susut', 'Pengakuan Penyusutan'),
        ('pengakuan_pendapatan_keuntungan', 'Pengakuan Pendapatan/Keuntungan'),
        ('pengakuan_kerugian', 'Pengakuan Kerugian'),
        ('barang_disewakan', 'Barang Disewakan'),
        ], string='Type', copy=False, index=True,required=True)
    coa_debet = fields.Many2one('account.account', string='Debit Account')
    coa_kredit = fields.Many2one('account.account', string='Credit Account')

class MasterNisbah(models.Model):
    _name = "master.nisbah"
    _description = "Master Nisbah"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _order = "periode_max"


    name = fields.Char(string='Description', required=True, copy=False, index=True, default=lambda self: _('Nisbah Default'))
    product_tmpl_id = fields.Many2one('product.template',string='Product Template',required=True, ondelete="cascade")
    periode_min = fields.Integer(string='Periode Min(bulan)', copy=False, index=True, required=True, default=12)
    periode_max = fields.Integer(string='Periode Max(bulan)', copy=False, index=True, required=True, default=24)
    margin = fields.Float(string='Margin (%)', required=True, copy=False, default=15)
    nilai_min =  fields.Float(string='Nilai Min', required=True, copy=False, default=5000000)
    nilai_max =  fields.Float(string='Nilai Max', required=True, copy=False, default=20000000)

class MasterPelunasan(models.Model):
    _name = "master.pelunasan"
    _description = "Master Pelunasan"
    _order = "periode_max"


    name = fields.Char(string='Description', required=True, copy=False, index=True, default=lambda self: _('Pelunasan Tahun pertama'))
    product_tmpl_id = fields.Many2one('product.template',string='Product Template',required=True, ondelete="cascade")
    periode_min = fields.Integer(string='Periode Min(bulan)', copy=False, index=True, required=True, default=3)
    periode_max = fields.Integer(string='Periode Max(bulan)', copy=False, index=True, required=True, default=12)
    pelunasan = fields.Selection([
        ('0', 'Tanpa Kewajiban'),
        ('1', 'Bulan Berjalan'),
        ('2', 'Bulan Berjalan +1'),
        ('3', 'Bulan Berjalan +2'),
        ('4', 'Bulan Berjalan +3'),
        ], string='Kewajiban Pelunasan', copy=False, index=True, default=0)

class ProductProduct(models.Model):
    _inherit = ['product.product']

    mitra_bank_id = fields.Many2one('simpin_syariah.mitra.bank',string='Mitra Bank', related="product_tmpl_id.mitra_bank_id")

    
    def action_open(self):
        self.product_tmpl_id.write({'state': 'open'})
        self.calc_total_pembiayaan()

    
    def action_submit(self):
        self.product_tmpl_id.write({'state': 'submit'})
        
    
    def action_bank_approve(self):
        csql = """
select product_id,periode_angsuran from simpin_syariah_pembiayaan
where product_id=%s and state in ('approve','active')
group by product_id,periode_angsuran
        """
        self.env.cr.execute(csql,(self.id,))
        loan = self.env.cr.dictfetchall()
        for line in loan:
            jatuh_tempo = date.today() + relativedelta(months=line['periode_angsuran'])
            csql = """
                    select sum(total_pembiayaan) as total_pembiayaan from simpin_syariah_pembiayaan
                    where product_id=%s and periode_angsuran=%s and state='approve'
                    """
            self.env.cr.execute(csql,(self.id,line['periode_angsuran'],))
            total_pembiayaan = self.env.cr.dictfetchall()
            ld_detil = self.env['simpin_syariah.loan_detail'].create({
                                                                    'name': self.get_ld_sequence(),
                                                                    'mitra_bank_id': self.mitra_bank_id.id,
                                                                    'periode_angsuran': line['periode_angsuran'],
                                                                    'total_pembiayaan': total_pembiayaan[0]['total_pembiayaan'],
                                                                    'tanggal_akad': date.today(),
                                                                    'jatuh_tempo': jatuh_tempo,
                                                                    'product_id': self.id,
                                                                    'margin': 0,
                                                                    'credit_account': self.mitra_bank_id.journal_id.default_debit_account_id.id,
                                                                })

            pembiayaan = self.env['simpin_syariah.pembiayaan'].search([('product_id','=',self.id),
                                                                       ('periode_angsuran','=',line['periode_angsuran']),
                                                                       ('state','in',['approve','active']),
                                                                       ],order='akad_id, periode_angsuran')
            if pembiayaan:
                total_pembiayaan = total_angsuran = saldo = 0.0
                akad = {}
                for biaya in pembiayaan:
                    biaya.loan_id = ld_detil.id
                    total_pembiayaan += biaya.total_pembiayaan
                    if biaya.akad_id.id in akad:
                        akad[biaya.akad_id.id] += biaya.total_pembiayaan
                    else:
                        akad[biaya.akad_id.id] = biaya.total_pembiayaan

                ld_detil.total_pembiayaan = total_pembiayaan
                ld_detil.credit_account = self.mitra_bank_id.journal_id.default_debit_account_id.id

        self.product_tmpl_id.state = 'approve'


    def get_ld_sequence(self):
        rekno = self.env['ir.sequence'].next_by_code('ld_sequence')
        if not rekno:
            cr_seq = self.env['ir.sequence'].create({
                            'name': 'Loan Detail Sequence',
                            'code': 'ld_sequence',
                            'implementation': 'standard',
                            'active': True,
                            'prefix': 'LD-',
                            'padding': 5,
                            'company_id': self.env.user.company_id.id,
                            'use_date_range': False,
                            })
            if cr_seq:
                rekno = self.env['ir.sequence'].next_by_code('ld_sequence')
            else:
                raise UserError('Sequence Error')
        return rekno


    
    def action_print(self):
        pengajuan = self.env['simpin_syariah.pembiayaan'].search([('state','=','check'),('product_id','=',self.id)])
        return self.env.ref('simpin_syariah.action_daftar_definitif_pembiayaan').report_action(self)

    def get_data_definitif(self):
        pengajuan = self.env['simpin_syariah.pembiayaan'].search([('state','=','check'),('product_id','=',self.id)])
        return pengajuan        

    def calc_total_pembiayaan(self):
        pengajuan = self.env['simpin_syariah.pembiayaan'].search([('state','in',['draft','submit','check']),('product_id','=',self.id)])
        pencairan = self.env['simpin_syariah.pembiayaan'].search([('state','in',['active','approve','closed']),('product_id','=',self.id)])
        total_ajuan = total_cair = 0
        for line in pengajuan:
            total_ajuan += line.total_pembiayaan
        for line in pencairan:
            total_cair += line.total_pembiayaan
            
        self.product_tmpl_id.write({'total_pengajuan': total_ajuan, 'total_pembiayaan': total_cair})


class ProductTemplate(models.Model):
    _inherit = ['product.template']

    is_syariah = fields.Boolean(string='Syariah')
    add_po = fields.Boolean(string='Add On PO')
    jenis_syariah = fields.Many2one('master.akad_syariah', string='Jenis Akad Syariah')
    nisbah_kopin = fields.Float(default=0.0,string='Nisbah Koperasi (%)')
    nisbah_lines = fields.One2many('master.nisbah','product_tmpl_id',string='Margin')
    minimal_setor = fields.Monetary(string='Minimal Setoran', currency_field='currency_id', track_visibility='onchange', default=10000)
    sumber_dana = fields.Many2one('account.journal', string='Journal Sumber Dana', domain=[('type', '=', 'bank')])
    pelunasan_lines = fields.One2many('master.pelunasan','product_tmpl_id',string='Kewajiban Pelunasan')
    mitra_bank_id = fields.Many2one('simpin_syariah.mitra.bank',string='Mitra Bank',compute="_get_mitra_bank",store=True)
    total_pengajuan = fields.Monetary(string='Total Pengajuan', currency_field='currency_id',store=True)
    total_pembiayaan = fields.Monetary(string='Total Pembiayaan', currency_field='currency_id',store=True)
    tanggal_mulai = fields.Date(string='Mulai', index=True)
    tanggal_akhir = fields.Date(string='Akhir', index=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('open', 'Open'),
        ('submit', 'Submit'),
        ('approve', 'Approve'),
        ('running', 'Running'),
        ('close', 'Closed'),
        ], string='Status', copy=False, index=True, default='open', track_visibility='onchange', store=True)
    biaya_lines = fields.One2many('mitra_bank.biaya','product_tmpl_id',string='Komponen Biaya')
    coa_um = fields.Many2one('account.account', store=True,string='Account Uang Muka')


    @api.depends('is_syariah')
    def _get_is_syariah(self):
        if self.is_syariah:
            self.type = 'service'

    @api.onchange('jenis_syariah')
    def _onchange_jenis_syariah(self):
        if self.jenis_syariah:
            self.categ_id = self.jenis_syariah.category_id.id

    @api.onchange('mitra_bank_id')
    def _onchange_mitra_bank_id(self):
        if self.mitra_bank_id and self.state=='open':
            self.state = 'draft'
        elif not self.mitra_bank_id:
            self.state = 'open'

    @api.depends('sumber_dana')
    def _get_mitra_bank(self):
        for tmpl in self:
            bank_id = tmpl.sumber_dana.bank_account_id.bank_id.id
            if bank_id:
                mitra_bank = self.env['simpin_syariah.mitra.bank'].search([('bank_id','=',bank_id)])
                tmpl.update({'mitra_bank_id': mitra_bank.id,})
            else:
                tmpl.update({'mitra_bank_id': False,})

    
class TrxBiaya(models.Model):
    _name = "transaksi.biaya"
    _description = "Komponen Biaya"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'resource.mixin']

    name = fields.Char(string='Deskripsi',required=True, copy=False,default=lambda self: _('Deskripsi'))
    kode = fields.Char(string='kode',required=True, copy=False,default=lambda self: _('Kode'))
    nilai_pct = fields.Float(default=0.0, string='Pct (%)')
    nominal = fields.Float(default=0.0, string='Nominal')
    coa_debet = fields.Many2one('account.account', required=True,string='Debet Account')
    coa_kredit = fields.Many2one('account.account',required=True,string='Kredit Account')
    tipe = fields.Selection([
        ('administrasi', 'Administrasi'),
        ('margin', 'Margin'),
        ('notaris', 'Notaris'),
        ('asuransi', 'Asuransi'),
        ('transfer', 'Transfer Bank'),
        ('lain', 'Lainnya'),
        ], string='Type', copy=False, index=True, default='pokok',required=True)
    is_actived = fields.Boolean(string='Active', required=True, copy=False, default=True)

class ConfigSchedule(models.Model):
    _name = "config.schedule"
    _description = "Konfigurasi terkait Schedule"

    name = fields.Text(string='Deskripsi',required=True, copy=False, default=lambda self: _('Deskripsi'))
    tipe_schedule = fields.Selection([('invoice', 'Invoice')], string='Type Schedule', copy=False, required=True)
    date_day = fields.Selection([
                    ('1', '1'),
                    ('2', '2'),
                    ('3', '3'),
                    ('4', '4'),
                    ('5', '5'),
                    ('6', '6'),
                    ('7', '7'),
                    ('8', '8'),
                    ('9', '9'),
                    ('10', '10'),
                    ('11', '11'),
                    ('12', '12'),
                    ('13', '13'),
                    ('14', '14'),
                    ('15', '15'),
                    ('16', '16'),
                    ('17', '17'),
                    ('18', '18'),
                    ('19', '19'),
                    ('20', '20'),
                    ('21', '21'),
                    ('22', '22'),
                    ('23', '23'),
                    ('24', '24'),
                    ('25', '25'),
                    ('26', '26'),
                    ('27', '27'),
                    ('28', '28'),
                    ('29', '29'),
                    ('30', '30'),
                    ('31', '31'),
                ], string="Date Day")


