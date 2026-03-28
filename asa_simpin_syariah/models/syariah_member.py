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
from werkzeug.urls import url_encode
import re
import psycopg2
from psycopg2 import DatabaseError, errorcodes
import psycopg2.extras
import json
import base64
from dateutil.relativedelta import relativedelta

class Followers(models.Model):
    _inherit = 'mail.followers'

    @api.model
    def create(self, vals):
        if 'res_model' in vals and 'res_id' in vals and 'partner_id' in vals:
            dups = self.env['mail.followers'].search([('res_model', '=',vals.get('res_model')), ('res_id', '=', vals.get('res_id')), ('partner_id', '=', vals.get('partner_id'))])
            
            if len(dups):
                for p in dups:
                    p.unlink()
        
        res = super(Followers, self).create(vals)
        
        return res


class SimPinMemberResign(models.TransientModel):
    _name = "simpin_syariah.member.resign"
    _description = "Resign Keanggotaan Simpin Syariah"

    @api.model
    def _default_currency(self):
        return self.env.user.company_id.currency_id.id


    name = fields.Char(string='Name', related='member_id.name')
    tanggal = fields.Date(string='Tanggal Resign')
    member_id = fields.Many2one('simpin_syariah.member',string='Nama Anggota', 
                                 domain=[('state', '=', 'done')])
    currency_id = fields.Many2one('res.currency', string="Currency", readonly=True, default=_default_currency)
    simpanan_ids = fields.Many2many('simpin_syariah.rekening','simpanan_resign_rel', 'simpanan_id', 'resign_id')
    simpanan_total = fields.Monetary(string='Total Simpanan',  currency_field='currency_id')
    pembiayaan_ids = fields.Many2many('simpin_syariah.pembiayaan','pembiayaan_resign_rel', 'pembiayaan_id', 'resign_id')
    pembiayaan_total = fields.Monetary(string='Total Pembiayaan',  currency_field='currency_id')
    pinjaman_ids = fields.Many2many('simpin_syariah.pinjaman', 'pinjaman_resign_rel','pinjaman_id','resign_id')
    pinjaman_total = fields.Monetary(string='Total Pinjaman',  currency_field='currency_id')
    investasi_ids = fields.Many2many('simpin_syariah.investasi','investasi_resign_rel','investasi_id','resign_id')
    investasi_total = fields.Monetary(string='Total investasi',  currency_field='currency_id')
    total_hak = fields.Monetary(string='Total Hak',  currency_field='currency_id')
    total_kewajiban = fields.Monetary(string='Total Kewajiban',  currency_field='currency_id')
    potongan_pelunasan = fields.Monetary(string='Total Kewajiban',  currency_field='currency_id')
    keterangan = fields.Text(string='Keterangan')

    
    def action_proses_resign(self):
        raise UserError(_('Resign %s \n simpanan %s \n pinjaman %s \n investasi %s \n investasi %s ')%(self.name,self.simpanan_total,self.pinjaman_total,self.investasi_total,self.pembiayaan_total,))

    
    def action_netting(self):
        raise UserError(_('Netting Pelunasan'))

class SimPinMember(models.Model):
    _name = "simpin_syariah.member"
    _description = "Keanggotaan Simpin Syariah"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    @api.model
    def _default_currency(self):
        return self.env.user.company_id.currency_id.id

    @api.model
    def default_get(self, default_fields):
        """If we're creating a new account through a many2one, there are chances that we typed the account code
        instead of its name. In that case, switch both fields values.
        """
        default_name = self._context.get('default_name')
        default_nomor_induk = self._context.get('default_nomor_induk')
        if default_name and not default_nomor_induk:
            try:
                default_nomor_induk = int(default_name)
            except ValueError:
                pass
            if default_nomor_induk:
                default_name = False
        contextual_self = self.with_context(default_name=default_name, default_nomor_induk=default_nomor_induk)
        return super(SimPinMember, contextual_self).default_get(default_fields)

    @api.depends('tanggal_lahir')
    def _compute_age(self):
        for rec in self:
            if rec.tanggal_lahir:
                d1 = rec.tanggal_lahir
                d2 = fields.Date.today()
                rd = relativedelta(d2, d1)
                rec.age = "{}y {}m {}d".format(rd.years, rd.months, rd.days)
            else:
                rec.age = "No Date Of Birth!!"

    name = fields.Char(string='Name', required=True, copy=False, index=True)
    company_id = fields.Many2one('res.company', string='Company', required=True,
        copy=False, default=lambda self: self.env['res.company']._company_default_get())
    partner_id = fields.Many2one('res.partner', string='Partner')
    currency_id = fields.Many2one('res.currency', string="Currency", readonly=True, default=_default_currency)
    comp_partner_id = fields.Many2one('res.partner', string='Perusahaan', related='mitra_id.partner_id') #domain=[('is_company', '=', True)])
    nomor_anggota = fields.Char(string='Nomor Anggota', readonly=True, store=True)
    mitra_id = fields.Many2one('simpin_syariah.mitra', string='Mitra Kerja')
    address = fields.Char(string='Alamat', track_visibility='onchange')
    kelurahan_id = fields.Many2one('wilayah.kelurahan',string='Kelurahan', track_visibility='onchange')
    kecamatan_id = fields.Many2one('wilayah.kecamatan',string='Kecamatan', track_visibility='onchange')
    kabkota_id = fields.Many2one('wilayah.kabkota',string='Kab / Kota', track_visibility='onchange')
    provinsi_id = fields.Many2one('wilayah.provinsi', string='Provinsi')
    kodepos = fields.Char(string='Kodepos',store=True, track_visibility='onchange')
    tempat_lahir = fields.Char(string='Tempat Lahir', track_visibility='onchange')
    tanggal_lahir = fields.Date(string='Tanggal Lahir', track_visibility='onchange')
    age = fields.Char(compute='_compute_age', string='Usia')
    agama = fields.Selection([
        ('islam', 'Islam'),
        ('kristen', 'Kristen'),
        ('hindu', 'Hindu'),
        ('budha', 'Buddha'),
        ('katolik', 'Katolik'),
        ('kong', 'Kong Hu Chu'),
    ], string='Agama')
    gender = fields.Selection([
        ('laki', 'Laki-Laki'),
        ('p', 'Perempuan'),
        ('l', 'Lainnya'),
    ], string='Jenis Kelamin')
    # marital = fields.Many2one('master.general', string='Status Perkawinan',
    #                                  domain=[('type_umum', '=', 'marital')], track_visibility='onchange')
    jabatan_id = fields.Many2one('jabatan.group', 'Jabatan')
    # no_identitas = fields.Char(string='No Identitas')
    # npwp = fields.Char(string='NPWP')
    # divisi = fields.Char(string='Divisi', track_visibility='onchange')
    # status_karyawan = fields.Char(string='Status Karyawan', track_visibility='onchange')
    # jangka_waktu_kontrak = fields.Char(string='Jangka Waktu Kontrak', track_visibility='onchange')
    # akhir_kontrak = fields.Char(string='Akhir Kontrak', track_visibility='onchange')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submit', 'Submitted'),
        ('check', 'Check Document'),
        ('approve', 'Approved'),
        ('done', 'Active'),
        ('settlement', 'Settlement'),
        ('settled', 'Settled'),
        ('close', 'Closed'),
        ('cancel', 'Cancelled'),
        ], string='Status', copy=False, index=True, default='draft', track_visibility='onchange', readonly=True)
    email = fields.Char(string='Email', required=False)
    nomor_induk = fields.Char(string='No kTP/NIK')
    # nama_atasan = fields.Char(string='Nama Atasan')
    # jabatan_atasan = fields.Many2one('master.general', string='Jabatan', copy=False,
    #                                  domain=[('type_umum', '=', 'jabatan')], track_visibility='onchange')
    no_telp = fields.Char(string='Telepon', track_visibility='onchange')
    no_hp = fields.Char(string='Handphone', track_visibility='onchange')
    # keluarga_dekat = fields.Char(string='Keluarga Dekat', track_visibility='onchange')
    # no_keluarga = fields.Char(string='Handphone')
    # bank_id = fields.Many2one('res.bank','Bank',help='Nama Bank Penerima', track_visibility='onchange')
    # bank_norek = fields.Char('Account #',help='No Rekening Penerima', track_visibility='onchange')
    # bank_namarek = fields.Char('Beneficiary',help='Nama Pada Rekening', track_visibility='onchange')
    # waris_lines = fields.One2many('simpin_syariah.member.waris','member_id',string='Ahli Waris', track_visibility='onchange')
    simpanan_ids = fields.One2many('simpin_syariah.rekening', 'member_id', 'Simpanan', readonly=False, copy=True, track_visibility='onchange')
    # simpanan_count = fields.Integer(string='Jumlah Simpanan', compute='_compute_simpanan_count', readonly=True)
    simpanan_total = fields.Monetary(string='Total Simpanan', compute='_compute_simpanan_count', currency_field='currency_id', readonly=False, store=True)
    pembiayaan_ids = fields.One2many('simpin_syariah.pembiayaan', 'member_id','Pembiayaan', readonly=False, copy=True, track_visibility='onchange')
    pembiayaan_count = fields.Integer(string='Jumlah Pembiayaan', compute='_compute_pembiayaan_count', readonly=True)
    pembiayaan_total = fields.Monetary(string='Total Pembiayaan',  compute='_compute_pembiayaan_count', currency_field='currency_id', readonly=False, store=True)
    pinjaman_ids = fields.One2many('simpin_syariah.pinjaman', 'member_id','Pinjaman', readonly=False, copy=True, track_visibility='onchange')
    pinjaman_count = fields.Integer(string='Jumlah Pinjaman', compute='_compute_pinjaman_count', readonly=True)
    pinjaman_total = fields.Monetary(string='Total Pinjaman', compute='_compute_pinjaman_count', currency_field='currency_id', readonly=False, store=True)
    investasi_ids = fields.One2many('simpin_syariah.investasi', 'member_id','Investasi', readonly=False, copy=True, track_visibility='onchange')
    investasi_count = fields.Integer(string='Jumlah investasi', compute='_compute_investasi_count', readonly=True)
    investasi_total = fields.Monetary(string='Total investasi', compute='_compute_investasi_count', currency_field='currency_id', readonly=False, store=True)
   
    dummy = fields.Char(string='Button Menu')
    mobile_active = fields.Boolean(string='Mobile Apps', default=False)
    simpanan_pokok = fields.Many2one('simpin_syariah.rekening',string='Simpanan Pokok',readonly=True, store=True)
    simpanan_wajib = fields.Many2one('simpin_syariah.rekening',string='Simpanan Wajib',readonly=True, store=True)
    simpanan_sukarela = fields.Many2one('simpin_syariah.rekening',string='Simpanan Sukarela',readonly=True, store=True)
    simpanan_pokoks = fields.Many2one('form.simpanan', string='Simpanan Pokok', readonly=True, store=True)
    simpanan_wajibs = fields.Many2one('form.simpanan', string='Simpanan Wajib', readonly=True, store=True)
    simpanan_hari_raya = fields.Many2one('form.simpanan', string='Simpanan Hari Raya', readonly=True, store=True)
    simpanan_sukarelas = fields.Many2one('form.simpanan', string='Simpanan Sukarela', readonly=True,
                                        store=True)
    employee_id = fields.Integer(string='Employee ID', store=True)
    is_sukarela = fields.Boolean(string='Simpanan Sukarela ?')

    kk_line = fields.One2many('anggota.pendidikan.line', 'anggota_line_id', string='PENDIDIKAN (dalam 1 KK)')

    ########## DOCUMENT PENDUKUNG ###########
    upload_ktp = fields.Binary(string="KTP")
    file_ktp = fields.Char(string="File KTP")
    upload_ktp_pasangan = fields.Binary(string="KTP Pasangan")
    file_ktp_pasangan = fields.Char(string="File KTP Pasangan")
    upload_kk = fields.Binary(string="Kartu Keluarga")
    file_kk = fields.Char(string="File KK")
    upload_dok_lain = fields.Binary(string="Dokumen Lainnya")
    file_dok_lain = fields.Char(string="File Dokumen Lain")

    wilayah_id = fields.Many2one('master.wilayah', 'Wilayah', required=True)
    ko_id = fields.Many2one('peternak.sapi', 'KO')
    ka_id = fields.Many2one('peternak.sapi', 'KA')
    jns_keanggotan = fields.Selection([
        ('ca', 'CA'),
        ('ap', 'AP'),
        ('u', 'U'),
        ('kan', 'KAN'),
        ('m', 'Mitra'),
        ('r', 'Resign')
    ], string='Jenis Keanggotaan', compute='_compute_jns_keanggotan')
    sk = fields.Char('SK')
    indikator = fields.Selection([
        ('1', 'Aktif / Komitmen'),
        ('2', 'Tidak Aktif / Tidak Komitmen'),
    ], string='Indikator Khusus KA/KO')
    nilai_indikator = fields.Integer(compute='_hitung_nilai', string='Nilai', readonly=True)

    pelatihan = fields.Integer(string='Pelatihan')
    stdi_banding = fields.Integer(string='Studi Banding')
    peny_rutin = fields.Integer(string='Penyuluhan Rutin')
    peny_segmen = fields.Integer(string='Penyuluhan Segmentasi')
    peng_sdm = fields.Integer(string='Pengembangan SDM Anggota Khusus')
    pend_teknis = fields.Integer(string='Pendamoingan Teknis')

    prog_wajib = fields.Char('Program Wajib')
    prog_pkp = fields.Selection([
        ('1', 'Dengan Pembiayaan Kan Jabung'),
        ('2', 'Kredit - Kredit Lain yang diakses diluar Pembiayaan'),
        ('3', 'Jenis PKP yang pernah diakses Saper'),
        ('4', 'Mandiri'),
    ], string='Program PKP')

    prod_prog = fields.Char('Produktif Program')
    prod_non_prog = fields.Char('Produktif Non Program')
    kons = fields.Char('Konsumtif')

    gmbr = fields.Binary('Image')
    tgl_join = fields.Date('Tanggal Bergabung')
    tgl_pengangkatan = fields.Date('Tanggal Pengangkatan')
    kode_anggota = fields.Char('Kode Anggota')
    kode_peternak = fields.Char('Kode Peternak')
    usaha_id = fields.Many2one('usaha.peternak', 'Unit Usaha')
    tps_id = fields.Many2one('tps.liter', 'Pos Penampungan')
    kode_tps = fields.Char('Kode Pos Penampungan')
    status_perkawinan = fields.Selection([
        ('1', 'Kawin'),
        ('2', 'Tidak Kawin'),
    ], string='Status Perkawinan')
    jumlah_sapi_kering = fields.Integer('Jumlah Induk Kering')
    jumlah_sapi_laktasi = fields.Integer('Jumlah Induk Laktasi')
    jumlah_sapi_dara = fields.Integer('Jumlah Sapi Dara')
    count_sapi = fields.Integer('Jumlah Sapi')
    # peternak_sapi_ids = fields.One2many('peternak.sapi', 'member_anggota_id', string='Peternak Sapi')
    peternak_id = fields.Many2one('peternak.sapi', 'Peternak')

    simpanan_count = fields.Integer(compute='compute_simpanan_count')

    def get_simpanan(self):
        action = self.env.ref('asa_simpin_syariah.'
                              'form_simpanan_action').read()[0]
        action['domain'] = [('member_id', 'in', self.ids)]
        return action

    def compute_simpanan_count(self):
        for record in self:
            record.simpanan_count = self.env['form.simpanan'].search_count(
                [('member_id', 'in', self.ids)])

    @api.depends('peternak_id')
    def _compute_jns_keanggotan(self):
        for record in self:
            peternak_state = record.peternak_id.state if record.peternak_id else False
            if peternak_state == 'cln_anggota':
                record.jns_keanggotan = 'ca'
            elif peternak_state == 'anggota':
                record.jns_keanggotan = 'ap'
            elif peternak_state == 'resign':
                record.jns_keanggotan = 'r'
            else:
                record.jns_keanggotan = False

    # @api.onchange('provinsi_id')
    # def _onchange_provinsi_id(self):
    #     if self.provinsi_id:
    #         self.provinsi_id_clone = self.provinsi_id.provinsi
    #     else:
    #         self.provinsi_id_clone = False
    #
    # @api.onchange('wilayah_id')
    # def _onchange_wilayah_id(self):
    #     if self.wilayah_id:
    #         self.wilayah_id = self.wilayah_id.wilayah_id
    #     else:
    #         self.wilayah_id_clone = False

    @api.depends('indikator')
    def _hitung_nilai(self):
        for record in self:
            if record.indikator == '1':
                record.nilai_indikator = 1
            elif record.indikator == '2':
                record.nilai_indikator = 0
            else:
                record.nilai_indikator = 0

    def cek_paid_status(self):
        for member in self:
            simpanan_wajib = self.env['simpin_syariah.rekening'].search([('member_id','=',member.id),('product_id.name','=','SIMPANAN WAJIB')], limit=1)
            invoice_wajib = self.env['account.move'].search([('simpanan_id','=',simpanan_wajib.id)], limit=1)
            simpanan_pokok = self.env['simpin_syariah.rekening'].search([('member_id','=',member.id),('product_id.name','=','SIMPANAN POKOK')], limit=1)
            invoice_pokok = self.env['account.move'].search([('simpanan_id','=',simpanan_pokok.id)], limit=1)
            if invoice_wajib.payment_state == 'paid' and invoice_pokok.payment_state == 'paid' :
                print ("########invoice wajib pokok########", invoice_wajib.name, invoice_pokok.name)
                member.state = 'done'       

                    
    @api.onchange('nomor_induk','name')
    def _cek_employee(self):
        if self.mitra_id.notif_metode=='db_h2h':
            employee_id = self.mitra_id.h2h_get_employee_id(self.nomor_induk)
            employee_name = self.mitra_id.h2h_get_employee_id_by_name(self.name)
            if employee_id:
                self.employee_id = employee_id
            elif employee_name:
                self.employee_id = employee_name
            else:
                raise UserError(_('Nama dan NIK tidak terdaftar di Mitra %s')%(self.mitra_id.name,))

    
    @api.depends('investasi_ids')
    def _compute_investasi_count(self):
        for rec in self:
            rec.investasi_count = len(rec.mapped('investasi_ids'))

            total_investasi = 0.0
            for investasi in rec.investasi_ids:
                total_investasi += investasi.total_investasi            

            rec.update({'investasi_total': total_investasi,})
#        raise UserError(_('total_pinjaman %s \n %s')%(total_pinjaman,self.pinjaman_total,))

    
    # @api.depends('simpanan_ids')
    # def _compute_simpanan_count(self):
    #     for rec in self:
    #         rec.simpanan_count = len(rec.mapped('simpanan_ids'))
    #         total_simpanan = 0.0
    #         for simpanan in rec.simpanan_ids:
    #             total_simpanan += simpanan.balance
    #         rec.update({'simpanan_total': total_simpanan,})
    #
    #         if total_simpanan>0:
    #             if rec.simpanan_pokok.balance>=rec.simpanan_pokok.product_id.product_tmpl_id.minimal_setor and rec.simpanan_wajib.balance>=rec.simpanan_wajib.product_id.product_tmpl_id.minimal_setor:
    #                 rec.write({'state': 'done'})



    
    @api.depends('pinjaman_ids')
    def _compute_pinjaman_count(self):
        for rec in self:
            rec.pinjaman_count = len(rec.mapped('pinjaman_ids'))

            total_pinjaman = 0.0
            for pinjaman in rec.pinjaman_ids:
                total_pinjaman += pinjaman.balance            

            rec.update({'pinjaman_total': total_pinjaman,})
#        raise UserError(_('total_pinjaman %s \n %s')%(total_pinjaman,self.pinjaman_total,))

                                 
    @api.depends('pembiayaan_ids')
    def _compute_pembiayaan_count(self):
        for rec in self:
            rec.pembiayaan_count = len(rec.mapped('pembiayaan_ids'))

            total_pembiayaan = 0.0
            for line in self.pembiayaan_ids:
                total_pembiayaan += line.balance            

            self.update({'pembiayaan_total': total_pembiayaan,})

    @api.onchange('email')
    def validate_mail(self):
        if self.email:
            match = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', self.email)
            if match == None:
                raise ValidationError(_('Not a valid E-mail ID %s')%(self.email,))

    
    def action_view_simpanan(self):
        action = self.env.ref(
            'asa_simpin_syariah.simpin_syariah_rekening_action').read()[0]
        lines = self.mapped('simpanan_ids')
        if len(lines) > 1:
            action['domain'] = [('id', 'in', lines.ids)]
        elif lines:
            action['views'] = [(self.env.ref(
                'asa_simpin_syariah.simpin_syariah_rekening_form').id, 'form')]
            action['res_id'] = lines.ids[0]
        return action

    
    def action_view_investasi(self):
        action = self.env.ref(
            'asa_simpin_syariah.simpin_syariah_investasi_action').read()[0]
        lines = self.mapped('investasi_ids')
        if len(lines) > 1:
            action['domain'] = [('id', 'in', lines.ids)]
        elif lines:
            action['views'] = [(self.env.ref(
                'asa_simpin_syariah.simpin_syariah_investasi_form').id, 'form')]
            action['res_id'] = lines.ids[0]
        return action

    
    def action_view_pembiayaan(self):
        action = self.env.ref(
            'asa_simpin_syariah.simpin_syariah_pembiayaan_action').read()[0]
        lines = self.mapped('pembiayaan_ids')
        if len(lines) > 1:
            action['domain'] = [('id', 'in', lines.ids)]
        elif lines:
            action['views'] = [(self.env.ref(
                'simpin_syariah.simpin_syariah_pembiayaan_form').id, 'form')]
            action['res_id'] = lines.ids[0]
        return action

    
    def action_view_pinjaman(self):
        action = self.env.ref(
            'asa_simpin_syariah.simpin_syariah_pinjaman_action').read()[0]
        lines = self.mapped('pinjaman_ids')
        if len(lines) > 1:
            action['domain'] = [('id', 'in', lines.ids)]
        elif lines:
            action['views'] = [(self.env.ref(
                'asa_simpin_syariah.simpin_syariah_pinjaman_form').id, 'form')]
            action['res_id'] = lines.ids[0]
        return action

 
    
    def action_resign(self):
        view_id = self.env['ir.ui.view'].search([('name', '=', 'simpin_syariah.member.resign')], limit=1).id
        simpanan_total = pinjaman_total = investasi_total = pembiayaan_total = 0.0
        for simpanan in self.simpanan_ids:
            simpanan_total+=simpanan.balance
        for pinjaman in self.pinjaman_ids:
            pinjaman_total+=pinjaman.balance
        for investasi in self.investasi_ids:
            investasi_total+=investasi.total_investasi
        for pembiayaan in self.pembiayaan_ids:
            pembiayaan_total+=pembiayaan.balance
        total_hak = simpanan_total + investasi_total
        total_kewajiban = pinjaman_total + pembiayaan_total
        
        return {
            'name': _('Member Resign'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_id': view_id,
            'res_model': 'simpin_syariah.member.resign',
            'target': 'new',
            'context': {
                    'default_tanggal': date.today(),
                    'default_member_id': self.id,
                    'default_simpanan_ids': [(6,0,self.simpanan_ids.ids)],
                    'default_simpanan_total': simpanan_total,
                    'default_pinjaman_ids': [(6,0,self.pinjaman_ids.ids)],
                    'default_pinjaman_total': pinjaman_total,
                    'default_investasi_ids': [(6,0,self.investasi_ids.ids)],
                    'default_investasi_total': investasi_total,
                    'default_pembiayaan_ids': [(6,0,self.pembiayaan_ids.ids)],
                    'default_pembiayaan_total': pembiayaan_total,
                    'default_total_hak': total_hak,
                    'default_total_kewajiban': total_kewajiban,
                    }
                }

    
    def action_submit(self):
        self.validate_mail()
        self.write({'state': 'submit'})

    
    def action_check(self):
        self.validate_mail()
        self.write({'state': 'check'})

    
    def action_approve_all(self):
        members = self.env['simpin_syariah.pembiayaan'].search([('vendor_id','=',False)])
        for member in members:
            member.write({'vendor_id': member.member_id.partner_id.id,
                          'vendor_bank_id': member.member_id.partner_id.bank_ids[0].id,
                })
                
            

    # def simp_name(self,akad):
    #     ak_id = self.env['master.akad_syariah'].search([('id','=',akad.id)])
    #     akad_id = ak_id.name + " sequence"
    #     rekno = self.env['ir.sequence'].next_by_code(akad_id)
    #     if not rekno:
    #         cr_seq = self.env['ir.sequence'].create({
    #                         'name': ak_id.name,
    #                         'code': akad_id,
    #                         'implementation': 'standard',
    #                         'active': True,
    #                         'prefix': ak_id.kode + '/%(year)s/%(month)s/',
    #                         'padding': 5,
    #                         'company_id': self.env.user.company_id.id,
    #                         'use_date_range': False,
    #                         })
    #         if cr_seq:
    #             rekno = self.env['ir.sequence'].next_by_code(akad_id)
    #         else:
    #             raise UserError('Sequence Error')
    #     return rekno

    
    def action_approve(self):
        self.validate_mail()
        self.write({'state': 'done'})
        self.nomor_anggota = self.env['ir.sequence'].next_by_code('simpin_syariah.member')

        #Sekaligus Create User Akses dan simpanan wajib/pokok/sukarela
        s_pokok = self.env['product.product'].search(['|',('product_tmpl_id.name','=','SIMPANAN POKOK'),('product_tmpl_id.name','=','Simpanan Pokok')])
        s_wajib = self.env['product.product'].search(['|',('product_tmpl_id.name','=','SIMPANAN WAJIB'),('product_tmpl_id.name','=','Simpanan Wajib')])
        s_sukarela = self.env['product.product'].search(['|',('product_tmpl_id.name','=','SIMPANAN SUKARELA'),('product_tmpl_id.name','=','Simpanan Sukarela')])
        s_hari_raya = self.env['product.product'].search(['|', ('product_tmpl_id.name', '=', 'SIMPANAN HARI RAYA'), ('product_tmpl_id.name', '=', 'Simpanan Hari Raya')])
        # akad_syariah_pokok = self.env['master.akad_syariah'].search([('type_akad','=','pokok')],limit=1)
        # akad_syariah_wajib = self.env['master.akad_syariah'].search([('type_akad','=','wajib')],limit=1)
        # akad_syariah_sukarela = self.env['master.akad_syariah'].search([('type_akad','=','sukarela')],limit=1)
        # akad_syariah_hari_raya = self.env['master.akad_syariah'].search([('type_akad', '=', 'hariraya')], limit=1)
        # account_analytic_id = self.env['account.analytic.account'].search([('name','=','Wadiah')],limit=1)

        # Cari partner berdasarkan nama dan email
        partner = self.env['res.partner'].sudo().search([('name', '=', self.name), ('kode_peternak', '=', self.kode_peternak)])

        if partner:
            # Jika partner sudah ada, gunakan partner yang sudah ada
            partner_id = partner[0]
        else:
            # Jika partner belum ada, buat partner baru
            partner_id = self.env['res.partner'].sudo().create({
                                'name': self.name,
                                'email': self.email,
                                'is_company': False,
                                'active': True,
                                'customer': True,
                                'supplier': False,
                                'employee': False,
                                'parent_id': self.comp_partner_id.id,
                                })

            # Setelah mendapatkan partner_id, isi field partner_id pada objek saat ini
            self.partner_id = partner_id

            user_id = self.env['res.users'].sudo().create({
                                'login': self.email,
                                'password': 'user',
                                'active': True,
                                'partner_id': partner_id.id,
                                'share': True,
                                'sel_groups_1_9_10': 9,
                                })

        partner_id.update({'user_id': user_id.id,'display_name': self.name,})

        simp_pokok = self.env['form.simpanan'].sudo().create({
            'name': 'simpanan pokok',
            'member_id': self.id,
            'partner_id': partner_id.id,
            'product_id': s_pokok.id,
            'state': 'active',
        })

        simp_wajib = self.env['form.simpanan'].sudo().create({
            'name': 'simpanan wajib',
            'member_id': self.id,
            'partner_id': partner_id.id,
            'product_id': s_wajib.id,
            'state': 'active',
        })

        simp_hari_raya = self.env['form.simpanan'].sudo().create({
            'name': 'simpanan hari raya',
            'member_id': self.id,
            'partner_id': partner_id.id,
            'product_id': s_hari_raya.id,
            'state': 'active',
        })

        simp_sukarela = self.env['form.simpanan'].sudo().create({
            'name': '/',
            'member_id': self.id,
            'partner_id': partner_id.id,
            'product_id': s_sukarela.id,
            'state': 'active',
        })

        self.write({
            'state': 'done',
            'partner_id': partner_id.id,
            'simpanan_pokoks': simp_pokok.id,
            'simpanan_wajibs': simp_wajib.id,
            'simpanan_hari_raya': simp_hari_raya.id,
            'simpanan_sukarelas': simp_sukarela.id,
        })
    
    def action_settlement(self):
        member = self.env['simpin_syariah.member'].search([('state','=','settlement')])
        if member:
            for line in member:
                if line.pembiayaan_ids:
                    for bline in line.pembiayaan_ids:
                        if bline.state=='active':
                            bline.action_pelunasan()
                            invoice = self.env['account.invoice'].search([('pembiayaan_id','=',bline.id),('state','=','open')])
                            for inv in invoice:
                                pdf = self.env.ref('account.account_invoices').sudo().render_qweb_pdf([inv.id])[0]
                                inv.update({'file_data': base64.b64encode(pdf), 'file_name': inv.number.replace('/','_') + ".pdf",})
                            
                if line.pinjaman_ids:
                    for pline in line.pinjaman_ids:
                        if pinjaman.state=='active':
                            pline.action_pelunasan()
                            invoice = self.env['account.invoice'].search([('pinjaman_id','=',pline.id),('state','=','open')])
                            for inv in invoice:
                                pdf = self.env.ref('account.account_invoices').sudo().render_qweb_pdf([inv.id])[0]
                                inv.update({'file_data': base64.b64encode(pdf), 'file_name': inv.number.replace('/','_') + ".pdf",})

                line.update({'state': 'settled'})
                line.simpin_update_member("update simpin_member set state='settled' where email=%s",line.email)        

    
    def action_mobile(self):
        if self.mobile_active:
            self.write({'mobile_active': True})
        else:
            self.write({'mobile_active': False})

    def action_mobile_deactivate(self):
        if self.mobile_active:
            self.write({'mobile_active': True})
        else:
            self.write({'mobile_active': False})

    @api.onchange('provinsi_id')
    def _onchange_provinsi_id(self):
        if self.provinsi_id:
            kabkota = self.env['wilayah.kabkota'].search([('provinsi_id', '=', self.provinsi_id.id)])
            return {'domain': {'kabkota_id': [('id', 'in', kabkota.ids)]}}

    @api.onchange('kabkota_id')
    def _onchange_kabkota_id(self):
        if self.kabkota_id:
            kecamatan = self.env['wilayah.kecamatan'].search([('kabkota_id', '=', self.kabkota_id.id)])
            return {'domain': {'kecamatan_id': [('id', 'in', kecamatan.ids)]}}

    @api.onchange('kecamatan_id')
    def _onchange_kecamatan_id(self):
        if self.kecamatan_id:
            kelurahan = self.env['wilayah.kelurahan'].search([('kecamatan_id', '=', self.kecamatan_id.id)])
            return {'domain': {'kelurahan_id': [('id', 'in', kelurahan.ids)]}}

    @api.onchange('kelurahan_id')
    def _onchange_kelurahan_id(self):
        if self.kelurahan_id:
            self.kodepos = self.kelurahan_id.kodepos


class SimPinMemberWaris(models.Model):
    _name = "simpin_syariah.member.waris"
    _description = "Ahli Waris Keanggotaan Simpin Syariah"
    _inherit = ['mail.thread', 'mail.activity.mixin']


    name = fields.Char(string='Name', required=True, copy=False, index=True)
    type_identitas = fields.Many2one('master.general', string='Type Identitas', copy=False,
                                     domain=[('type_umum', '=', 'identitas')], track_visibility='onchange')
    agama = fields.Many2one('master.general', string='Agama', copy=False,
                                     domain=[('type_umum', '=', 'agama')], track_visibility='onchange')
    gender = fields.Many2one('master.general', string='Jenis Kelamin', copy=False,  
                                     domain=[('type_umum', '=', 'gender')], track_visibility='onchange')
    hubungan = fields.Many2one('master.general', string='Hubungan', copy=False, required=True,
                                     domain=[('type_umum', '=', 'ahliwaris')], track_visibility='onchange')
    hub_lain = fields.Char(string='Lainnya')
    member_id = fields.Many2one('simpin_syariah.member',string='Nomor Keanggotaan')
    address = fields.Char(string='Alamat')
    rukun_tetangga = fields.Char(string='RT')
    rukun_warga = fields.Char(string='RW')
    kelurahan_id = fields.Many2one('wilayah.kelurahan',string='Kelurahan')
    kecamatan_id = fields.Many2one('wilayah.kecamatan',string='Kecamatan')
    kabkota_id = fields.Many2one('wilayah.kabkota',string='Kab / Kota')
    provinsi_id = fields.Many2one('wilayah.provinsi',string='Provinsi')
    kodepos =  fields.Char(string='Kodepos',store=True)
    tempat_lahir = fields.Char(string='Tempat Lahir')
    tanggal_lahir = fields.Date(string='Tanggal Lahir')
    no_identitas = fields.Char(string='No Identitas')
    no_telp = fields.Char(string='Telepon')
    no_hp = fields.Char(string='Handphone')

    @api.onchange('provinsi_id')
    def _onchange_provinsi_id(self):
        if self.provinsi_id:
            kabkota = self.env['wilayah.kabkota'].search([('provinsi_id', '=', self.provinsi_id.id)])
            return {'domain': {'kabkota_id': [('id', 'in', kabkota.ids)]}}

    @api.onchange('kabkota_id')
    def _onchange_kabkota_id(self):
        if self.kabkota_id:
            kecamatan = self.env['wilayah.kecamatan'].search([('kabkota_id', '=', self.kabkota_id.id)])
            return {'domain': {'kecamatan_id': [('id', 'in', kecamatan.ids)]}}

    @api.onchange('kecamatan_id')
    def _onchange_kecamatan_id(self):
        if self.kecamatan_id:
            kelurahan = self.env['wilayah.kelurahan'].search([('kecamatan_id', '=', self.kecamatan_id.id)])
            return {'domain': {'kelurahan_id': [('id', 'in', kelurahan.ids)]}}

    @api.onchange('kelurahan_id')
    def _onchange_kelurahan_id(self):
        if self.kelurahan_id:
            self.kodepos = self.kelurahan_id.kodepos

    
class AnggotaPendidikan(models.Model):
    _name = 'anggota.pendidikan.line'
    _description = 'Anggota Pendidikan'

    anggota_line_id = fields.Many2one('simpin_syariah.member', string='Peternak Sapi')
    stts_dlm_perkawinan = fields.Selection([
        ('1', 'Ayah'),
        ('2', 'Ibu'),
        ('a1', 'Anak Ke-1'),
        ('a2', 'Anak Ke-2'),
        ('a3', 'Anak Ke-3'),
        ('a4', 'Anak Ke-4'),
        ('a5', 'Anak Ke-5')
    ], string='Status Dalam Keluarga', default=False, required=True)
    tingkat_pend = fields.Selection([
        ('sd', 'SD'),
        ('smp', 'SMP'),
        ('sma', 'SMA/SMK'),
        ('d3', 'D3'),
        ('s1', 'S1'),
        ('s2', 'S2'),
        ('s3', 'S3')
    ], string='Tingkat Pendidikan', default=False, required=True)
