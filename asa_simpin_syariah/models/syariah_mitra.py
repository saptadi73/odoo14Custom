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


class SimPinMitraNotifSend(models.Model):
    _name = "simpin_syariah.mitra.send"


    @api.model
    def _default_currency(self):
        return self.env.user.company_id.currency_id.id

    name = fields.Char(string='Name', required=True, copy=False, index=True)
    tanggal = fields.Date(string='Tanggal Kirim')
    mitra_id = fields.Many2one("simpin_syariah.mitra", string='Mitra Kerja', required=True)
    email = fields.Char(string='Email to')
    message = fields.Text(string='Message')
    attach_pdf = fields.Binary(string="Data PDF")
    file_pdf = fields.Char(string="File Data PDF")
    attach_xls = fields.Binary(string="Data xls", store=True)
    file_xls = fields.Char(string="File Data xls", store=True)
    currency_id = fields.Many2one('res.currency', string="Currency", readonly=True, default=_default_currency)
    total_simpanan = fields.Monetary(string='Total Simpanan',  currency_field='currency_id')
    total_pinjaman = fields.Monetary(string='Total Pinjaman',  currency_field='currency_id')
    total_pembiayaan = fields.Monetary(string='Total Pembiayaan',  currency_field='currency_id')
    total_investasi = fields.Monetary(string='Total Investasi',  currency_field='currency_id')
    notif_metode = fields.Selection([
        ('manual', 'Manual'),
        ('email', 'Corporate Email'),
        ('personal', 'Personal Email'),
        ('db_h2h', 'Database Host2Host'),
        ('web', 'Web Interface'),
        ('api', 'API Interface'),
        ], string='Metode Notif', copy=False, index=True)
    send_lines = fields.One2many('simpin_syariah.mitra.send.line','send_id')
    state = fields.Char(string='Status')

class SimPinMitraNotifSendLine(models.Model):
    _name = "simpin_syariah.mitra.send.line"

    @api.model
    def _default_currency(self):
        return self.env.user.company_id.currency_id.id

    name = fields.Char(string='Name', copy=False, index=True)
    send_id = fields.Many2one('simpin_syariah.mitra.send',string='Notifikasi ID',ondelete="cascade")
    member_id = fields.Many2one('simpin_syariah.member',string='Nama Anggota')
    employee_id = fields.Integer(string='Employee ID')
    nama_anggota = fields.Char(string='Nama')
    nik_anggota = fields.Char(string='NIK')
    nomor_anggota = fields.Char(string='Nomor Anggota')
    currency_id = fields.Many2one('res.currency', string="Currency", readonly=True, default=_default_currency)
    simpanan_pokok = fields.Float(string='Simpanan Pokok')
    simpanan_wajib = fields.Float(string='Simpanan Wajib')
    pinjaman_bank = fields.Float(string='Pinjaman Bank')
    pinjaman_internal = fields.Float(string='Pinjaman Internal')
    line_details = fields.One2many('simpin_syariah.mitra.send.line.detail','send_line_id')

class SimPinMitraNotifSendLineDetail(models.Model):
    _name = "simpin_syariah.mitra.send.line.detail"


    @api.model
    def _default_currency(self):
        return self.env.user.company_id.currency_id.id


    send_line_id = fields.Many2one('simpin_syariah.mitra.send.line',string='Notif Line ID',ondelete="cascade")
    product_id = fields.Many2one('product.product', string='Nama Produk')
    currency_id = fields.Many2one('res.currency', string="Currency", readonly=True, default=_default_currency)
    amount = fields.Monetary(string='Amount',  currency_field='currency_id',store=True)
    #invoice_id = fields.Many2one('account.invoice',string='Invoice#')
    state = fields.Char(string='Status')
    name = fields.Char(string='No Pembiayaan')

class SimPinMitraNotifLineDetail(models.TransientModel):
    _name = "simpin_syariah.mitra.notif.line.detail"

    @api.model
    def _default_currency(self):
        return self.env.user.company_id.currency_id.id


    notif_line_id = fields.Many2one('simpin_syariah.mitra.notif.line',string='Notif Line ID')
    product_id = fields.Many2one('product.product', string='Nama Produk')
    currency_id = fields.Many2one('res.currency', string="Currency", readonly=True, default=_default_currency)
    amount = fields.Monetary(string='Balance',  currency_field='currency_id',store=True)
    #invoice_id = fields.Many2one('account.invoice',string='Invoice#')
    state = fields.Char(string='Status')
    name = fields.Char(string='No Pembiayaan')

    
class SimPinMitraNotifLine(models.TransientModel):
    _name = "simpin_syariah.mitra.notif.line"

    @api.model
    def _default_currency(self):
        return self.env.user.company_id.currency_id.id

    name = fields.Char(string='Name', copy=False, index=True)
    notif_id = fields.Many2one('simpin_syariah.mitra.notif',string='Notifikasi ID')
    member_id = fields.Many2one('simpin_syariah.member',string='Nama Anggota')
    employee_id = fields.Integer(string='Employee ID')
    nama_anggota = fields.Char(string='Nama')
    nik_anggota = fields.Char(string='NIK')
    nomor_anggota = fields.Char(string='Nomor Anggota')
    currency_id = fields.Many2one('res.currency', string="Currency", readonly=True, default=_default_currency)
    simpanan_pokok = fields.Float(string='Simpanan Pokok')
    simpanan_wajib = fields.Float(string='Simpanan Wajib')
    pinjaman_bank = fields.Float(string='Pinjaman Bank')
    pinjaman_internal = fields.Float(string='Pinjaman Internal')
    line_details = fields.One2many('simpin_syariah.mitra.notif.line.detail','notif_line_id')
                               
class SimPinMitraNotif(models.TransientModel):
    _name = "simpin_syariah.mitra.notif"

    @api.model
    def _default_currency(self):
        return self.env.user.company_id.currency_id.id

    name = fields.Char(string='Name', copy=False, index=True)
    notif_lines = fields.One2many('simpin_syariah.mitra.notif.line','notif_id')
    tanggal = fields.Date(string='Tanggal Kirim')
    mitra_id = fields.Many2one("simpin_syariah.mitra", string='Mitra Kerja', required=True)
    email = fields.Char(string='Email to')
    message = fields.Text(string='Message')
    attach_pdf = fields.Binary(string="Data PDF")
    file_pdf = fields.Char(string="File Data PDF")
    attach_xls = fields.Binary(string="Data xls", store=True)
    file_xls = fields.Char(string="File Data xls")
    currency_id = fields.Many2one('res.currency', string="Currency", readonly=True, default=_default_currency)
    total_simpanan = fields.Float(string='Total Simpanan')
    total_pinjaman = fields.Float(string='Total Pinjaman')
    total_pembiayaan = fields.Float(string='Total Pembiayaan')
    total_investasi = fields.Float(string='Total Investasi')
    notif_metode = fields.Selection([
        ('manual', 'Manual'),
        ('email', 'Corporate Email'),
        ('personal', 'Personal Email'),
        ('db_h2h', 'Database Host2Host'),
        ('web', 'Web Interface'),
        ('api', 'API Interface'),
        ], string='Metode Notif', copy=False, index=True)

    @api.onchange('email')
    def validate_mail(self):
       if self.email:
        match = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', self.email)
        if match == None:
            raise ValidationError('Not a valid E-mail ID')

    
    def action_send_notifikasi(self):
        attachment = self.env['ir.attachment'].create({'name': 'rekap_data_potongan.xls',
                                  'datas_fname': self.file_xls,
                                  'datas': self.attach_xls})
        template = self.env['mail.template'].search([('name','=','Mitra Notif: Send by email')])
        template.attachment_ids.unlink()
        template.attachment_ids = [(6,0,[attachment.id])]

        template.send_mail(self.id, raise_exception=False, force_send=True)
        
        notif_send = self.env['simpin_syariah.mitra.send'].create({
                                'name': 'Notifikasi',
                                'tanggal': self.tanggal,
                                'mitra_id': self.mitra_id.id,
                                'email': self.email,
                                'message': self.message,
                                'attach_xls': self.attach_xls,
                                'file_xls': self.file_xls,
                                'total_simpanan': self.total_simpanan,
                                'total_pinjaman': self.total_pinjaman,
                                'total_pembiayaan': self.total_pembiayaan,
                                'total_investasi': self.total_investasi,
            })
        if not notif_send:
            raise UserError(_('Terjadi Kesalahan'))
        return {
                'type': 'ir.actions.client',
                'tag': 'reload',
                }

class SimPinMitra(models.Model):
    _name = "simpin_syariah.mitra"
    _description = "Mitra Kerja Simpin Syariah"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'resource.mixin']
#    _inherit = 'res.partner'

    @api.model
    def _default_currency(self):
        return self.env.user.company_id.currency_id.id


    name = fields.Char(string='Name', required=True, copy=False, index=True)
    company_id = fields.Many2one('res.company', string='Company', required=True,
        copy=False, default=lambda self: self.env['res.company']._company_default_get())
    partner_id = fields.Many2one('res.partner', string='Partner',domain=[('is_company','=',True)])
    email = fields.Char(string='Email')
    currency_id = fields.Many2one('res.currency', string="Currency", readonly=True, default=_default_currency)
    member_lines = fields.One2many('simpin_syariah.member','mitra_id', string='Anggota', copy=False, store=True, domain=[('state', '=', 'done')])
    notif_lines = fields.One2many('simpin_syariah.mitra.send','mitra_id', string='Notifikasi')
    total_simpanan = fields.Monetary(string='Total Simpanan',  currency_field='currency_id', compute='_compute_total')
    total_pinjaman = fields.Monetary(string='Total Pinjaman',  currency_field='currency_id', compute='_compute_total')
    total_pembiayaan = fields.Monetary(string='Total Pembiayaan',  currency_field='currency_id', compute='_compute_total')
    total_investasi = fields.Monetary(string='Total Investasi',  currency_field='currency_id', compute='_compute_total')
    total_angsuran = fields.Monetary(string='Total Angsuran/bulan',  currency_field='currency_id', compute='_compute_total')
    attach_xls = fields.Binary(string="Data xls")
    file_xls = fields.Char(string="File Data xls")
    contact_person = fields.Many2one('res.partner', string='Contact Person')

    ### INTEGRASI DATABASE
    db_host = fields.Char(string='Host',store=True) #'192.168.15.10'
    db_port = fields.Integer(string='Port #', store=True, default=5432)
    db_username = fields.Char(string='Username',store=True) #'erpkopindosat'
    db_password = fields.Char(string='Password',store=True, password=True) #'t3r53r4h'
    db_dbname = fields.Char(string='Database',store=True) #'production_new'
    db_tablename = fields.Char(string='Tablename',store=True)
    notif_metode = fields.Selection([
        ('manual', 'Manual'),
        ('email', 'Corporate Email'),
        ('personal', 'Personal Email'),
        ('db_h2h', 'Database Host2Host'),
        ('web', 'Web Interface'),
        ('api', 'API Interface'),
        ], string='Metode Notif', copy=False, index=True, default='email')
    metode_kirim = fields.Selection([
        ('manual', 'Manual'),
        ('jadwal', 'Jadwal'),
        ], string='Metode Pengiriman', copy=False, index=True, default='manual')
    tanggal_kirim = fields.Date("Tanggal Pengiriman",default=date.today())
    
    @api.onchange('tanggal_kirim')
    def onchange_tanggal_kirim(self):
        if self.tanggal_kirim<date.today():
            self.tanggal_kirim = date.today() + relativedelta(days=1)


    @api.onchange('email')
    def validate_mail(self):
       if self.email:
        match = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', self.email)
        if match == None:
            raise ValidationError('Not a valid E-mail ID')

    
    @api.depends('member_lines')
    def _compute_total(self):
        total_simpanan = 0.0
        total_pinjaman = 0.0
        total_pembiayaan = 0.0
        total_investasi = 0.0
        total_angsuran = 0.0
        for member in self.member_lines:
            for simpanan in member.simpanan_ids:
                total_simpanan += simpanan.balance
            for pinjaman in member.pinjaman_ids:
                total_pinjaman += pinjaman.balance
                total_angsuran += pinjaman.angsuran
            for pembiayaan in member.pembiayaan_ids:
                total_pembiayaan += pembiayaan.balance
                total_angsuran += pembiayaan.angsuran
            for investasi in member.investasi_ids:
                total_investasi += investasi.total_investasi

        self.total_simpanan = total_simpanan
        self.total_pinjaman = total_pinjaman
        self.total_pembiayaan = total_pembiayaan
        self.total_investasi = total_investasi
        self.total_angsuran = total_angsuran

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        t_domain = False
        if self.partner_id:
            contact_person = self.env['res.partner'].search([('parent_id','=',self.partner_id.id)])
            t_domain = {'domain': {'contact_person': [('id', 'in', contact_person.ids)]}}
            self.name = self.partner_id.name
        return t_domain

    def get_nodin(self):
        rekno = self.env['ir.sequence'].next_by_code('NDN')
        if not rekno:
            cr_seq = self.env['ir.sequence'].create({
                            'name': 'Noda Dinas Notifikasi',
                            'code': 'NDN',
                            'implementation': 'standard',
                            'active': True,
                            'prefix': 'NDS/%(year)s/%(month)s/',
                            'padding': 5,
                            'company_id': self.env.user.company_id.id,
                            'use_date_range': False,
                            })
            if cr_seq:
                rekno = self.env['ir.sequence'].next_by_code('NDN')
        return rekno
    
    
    def cron_send_notifikasi(self):
        mitra_ids = self.env['simpin_syariah.mitra'].search([('metode_kirim','=','jadwal')])
        for mitra in mitra_ids:
            bulan = relativedelta(date.today(),mitra.tanggal_kirim)
            if bulan.months>=1:
                mitra.action_create_notifikasi()
                next_kirim = mitra.tanggal_kirim + relativedelta(months=1)
                mitra.update({'tanggal_kirim': next_kirim})

    
    def action_create_notifikasi(self):
#        if self.notif_metode=='email':
#            self.action_email_notifikasi()
#        elif self.notif_metode=='personal':
#            self.action_personal_notifikasi()
#        elif self.notif_metode=='db_h2h':
        mitra_ids = self.env['simpin_syariah.mitra'].search([('id','!=',0)])
#            raise UserError(_('CP Mitra %s')%(mitra_ids,))
            ### khusus Kopindosat
        for mitra in mitra_ids:
            self.action_dbh2h_notifikasi(mitra)
            

    def action_personal_notifikasi(self):
        list_anggota = self.env['simpin_syariah.member'].search([('mitra_id','=',self.id),('state','=','done')])
#        raise UserError(_('member %s')%(list_anggota,))
        for anggota in list_anggota:
            simpanan_total = pinjaman_total = pembiayaan_total = 0.0
            attachment = []
            for simpanan in anggota.simpanan_ids:
                if simpanan.product_id.product_tmpl_id.name.upper()=='SIMPANAN WAJIB':
                    simpanan_total=simpanan.product_id.product_tmpl_id.minimal_setor

            invoice_lines = self.env['account.invoice'].search([
                                                                ('partner_id','=',anggota.partner_id.id),
                                                                ('type','=','out_invoice'),
                                                                ('state','=','open')
                                                                ])
            if invoice_lines:
                for line in invoice_lines:
                    if line.pinjaman_id:
                        pinjaman_total+=line.amount_total
                    elif line.pembiayaan_id:
                        pembiayaan_total+=line.amount_total

                    pdf = self.env.ref('account.account_invoices').sudo().render_qweb_pdf([line.id])[0]
                    attach = self.env['ir.attachment'].create({
                            'name': line.number.replace('/','_') + ".pdf",
                            'type': 'binary',
                            'res_id': line.id,
                            'res_model': 'account.invoice',
                            'datas': base64.b64encode(pdf),
                            'mimetype': 'application/x-pdf',
                            'datas_fname': line.number.replace('/','_') + ".pdf"
                            })
                    attachment += [(6,0,attach.ids)]
                
            total = simpanan_total + pinjaman_total + pembiayaan_total
            message = """
            Dengan Hormat, <br/><br/>

            1. Bersama surat ini kami sampaikan Pemberitahuan Tagihan Pembiayaan Syariah """
            message += anggota.name
            message += " periode " + datetime.strftime(date.today(),'%B %Y') 
            message += "<br/>           sebesar Rp. " + str(f"{total:,.2f}") + " dengan rincian sebagai berikut:"
        
            message += "<br/>           a. Simpanan Wajib dan Pokok   Rp. "  + str(f"{simpanan_total:,.2f}")
            message += "<br/>           b. Potongan Pinjaman          Rp. "  + str(f"{pinjaman_total:,.2f}")
            message += "<br/>           c. Potongan Pembiayaan        Rp. "  +  str(f"{pembiayaan_total:,.2f}")

            message += """<br/>
               (rincian terlampir)<br/>

            2. Demikian kami sampaikan, atas perhatian dan kerjasamanya kami ucapkan terima kasih.<br/><br/>
        
        
            Hormat Kami,<br/>
            """ + self.company_id.name

            vals = {
                'subject': 'Notifikasi Tagihan',
                'body_html': message,
                'email_to': anggota.email,
                'email_cc': '',
                'auto_delete': False,
                'email_from': 'odoo@kopindosat.co.id',
                }

#            raise UserError(_('message %s - %s - %s')%(vals,invoice_lines,attachment,))
            mail_id = self.env['mail.mail'].sudo().create(vals)
            mail_id.mail_message_id.attachment_ids = attachment
#            raise UserError(_('mail_id %s \n mail_message_id %s attachment_ids %s')%(mail_id,mail_id.mail_message_id,mail_id.mail_message_id.attachment_ids,))
            mail_id.sudo().send()
            notif_send = self.env['simpin_syariah.mitra.send'].create({
                                'name': 'Notifikasi Personal',
                                'tanggal': date.today(),
                                'mitra_id': self.id,
                                'email': anggota.email,
                                'message': message,
                                'total_simpanan': total_simpanan,
                                'total_pinjaman': total_pinjaman,
                                'total_pembiayaan': total_pembiayaan,
                                'total_investasi': total_investasi,
                                'notif_metode': anggota.notif_metode,
                                'state': 'sent',
                            })
        
    def action_send_email_notifikasi(self,subject,message,email_to,att_name,att_file,att_data):
            body = """
Dengan Hormat, <br/><br/>
Good job, you've just created your first e-mail template <br/>
Regards,<br/>
      """
            vals = {
                'subject': subject,
                'body_html': message,
                'email_to': email_to,
                'email_cc': '',
                'auto_delete': False,
                'email_from': 'odoo@kopindosat.co.id',
                }
            attachment = self.env['ir.attachment'].create({'name': att_name,
                                  'datas_fname': att_file,
                                  'datas': att_data})

            mail_id = self.env['mail.mail'].sudo().create(vals)
            mail_id.mail_message_id.attachment_ids = [(6,0,[attachment.id])]
#            raise UserError(_('mail_id %s \n mail_message_id %s attachment_ids %s')%(mail_id,mail_id.mail_message_id,mail_id.mail_message_id.attachment_ids,))
            mail_id.sudo().send()


    def action_dbh2h_notifikasi(self,mitra):
        total_simpanan_pokok = total_simpanan_wajib = total_pinjaman_internal = total_pinjaman_bank = 0.0
        notif_line = []
        for member in mitra.member_lines:
            line_detail = []
            simpanan_pokok = simpanan_wajib = pinjaman_internal = pinjaman_bank = 0.0
            for simpanan in member.simpanan_ids:
                if simpanan.state=='active' and simpanan.product_id.product_tmpl_id.name.upper()=='SIMPANAN WAJIB':
                    simpanan_wajib += simpanan.product_id.product_tmpl_id.minimal_setor
                    line_detail += [(0,0,{'product_id': simpanan.product_id.id,
                                     'product_name': simpanan.product_id.name,
                                     'amount': simpanan.product_id.product_tmpl_id.minimal_setor,
                                     'invoice_id': 0,
                                     'invoice_number': '',
                                     'state': 'sent',
                                })]
                if simpanan.state=='active' and simpanan.product_id.product_tmpl_id.name.upper()=='SIMPANAN POKOK' and simpanan.balance==0:
                    simpanan_pokok += simpanan.product_id.product_tmpl_id.minimal_setor
                    line_detail += [(0,0,{'product_id': simpanan.product_id.id,
                                     'product_name': simpanan.product_id.name,
                                     'amount': simpanan.product_id.product_tmpl_id.minimal_setor,
                                     'invoice_id': 0,
                                     'invoice_number': '',
                                     'state': 'sent',
                                })]
            for pinjaman in member.pinjaman_ids:
                invoice = self.env['account.invoice'].search([('pinjaman_id','=',pinjaman.id),('state','=','open'),('date_invoice','<=',date.today())])
                tot_inv = 0.0
                if invoice:
                    for inv in invoice:
                        if inv.pinjaman_id.id==pinjaman.id and pinjaman.state=='active':
                            pinjaman_internal += inv.amount_total
                            tot_inv += inv.amount_total
                            line_detail += [(0,0,{'product_id': pinjaman.product_id.id,
                                                  'product_name':  pinjaman.product_id.name,
                                                  'amount': inv.amount_total,
                                                  'invoice_id': inv.id,
                                                  'invoice_number': inv.number,
                                                  'state': 'sent',
                                                  'name': pinjaman.name,
                                            })]

            for pembiayaan in member.pembiayaan_ids:
                invoice = self.env['account.invoice'].search([('pembiayaan_id','=',pembiayaan.id),('state','=','open')])
                tot_inv = 0.0
                if invoice:
                    for inv in invoice:
#                        raise UserError(_('CP Pembiayaan %s \n Invoice year %s \n month %s')%(pembiayaan.state,inv.date_invoice.year,inv.date_invoice.month,))
                        if inv.pembiayaan_id.id==pembiayaan.id and pembiayaan.state=='active' and inv.date_invoice.year==date.today().year and inv.date_invoice.month==date.today().month:
                            if pembiayaan.src_bank_id:
                                pinjaman_bank += inv.amount_total
                            else:
                                pinjaman_internal += inv.amount_total
                            tot_inv += inv.amount_total
                            line_detail += [(0,0,{'product_id': pembiayaan.product_id.id,
                                                  'product_name':  pembiayaan.product_id.name,
                                                  'amount': inv.amount_total,
                                                  'invoice_id': inv.id,
                                                  'invoice_number': inv.number,
                                                  'state': 'sent',
                                                  'name': pembiayaan.name,
                                            
                                            })]

#                            raise UserError(_('CP Pembiayaan %s \n Invoice %s \n line_detail %s')%(pembiayaan.state,invoice,line_detail,))
        
            if pinjaman_bank==0 and pinjaman_internal==0:
                continue
            else:
                notif_line += [(0,0,{'member_id': member.id,
                                 'employee_id': self.h2h_get_employee_id(member.email) if member.email else False,
                                 'nama_anggota': member.name,
                                 'nik_anggota': member.nomor_induk,
                                 'nomor_anggota': member.nomor_anggota,
                                 'simpanan_pokok': simpanan_pokok,
                                 'simpanan_wajib': simpanan_wajib,
                                 'pinjaman_bank': pinjaman_bank,
                                 'pinjaman_internal': pinjaman_internal,
                                 'line_details': line_detail,
                            })]

            total_simpanan_pokok += simpanan_pokok
            total_simpanan_wajib += simpanan_wajib
            total_pinjaman_bank += pinjaman_bank
            total_pinjaman_internal += pinjaman_internal

#        raise UserError(_('notif_line %s \n %s')%(mitra.name,notif_line,))

        if total_pinjaman_bank==0 and total_pinjaman_internal==0:
            TotalPinjaman =0
        else:
            nodin = self.get_nodin()+ " - " + mitra.name

            notif_send = self.env['simpin_syariah.mitra.send'].create({
                                        'name': nodin,
                                        'send_lines': notif_line,
                                        'tanggal': date.today(),
                                        'mitra_id': mitra.id,
                                        'total_simpanan': total_simpanan_pokok + total_simpanan_wajib,
                                        'total_pinjaman': total_pinjaman_bank + total_pinjaman_internal,
                                        'notif_metode': 'db_h2h',
                                        'state': 'Sent',
                                })

            send_sql = "insert into simpin_syariah_mitra_send(name,tanggal,total_simpanan,total_pinjaman,state,mitra_id) values('" + nodin + "',%s,%s,%s,'draft',%s)"
            detil_sql = """
                insert into simpin_syariah_mitra_send_line_detail(send_line_id,product_id,product_name,amount,
                invoice_id, invoice_number,state,name) values(%s,%s,%s,%s,%s,%s,'draft',%s)
                        """
        
            nsend_id = self.h2h_write_send('simpin_syariah_mitra_send',send_sql,date.today(),total_simpanan_pokok + total_simpanan_wajib,total_pinjaman_bank + total_pinjaman_internal,mitra.id)

            for nline in notif_line:
                xx = 0
                for notif in nline:
                    if xx>=2: # and notif['employee_id']>0:
                        member_id = self.get_dest_member_id(notif['nomor_anggota'])
                        if notif['employee_id']:
                            notif_line_sql = """
                                insert into simpin_syariah_mitra_send_line(name,send_id,member_id,employee_id,nama_anggota,nik_anggota,
                                simpanan_pokok,simpanan_wajib,pinjaman_bank,pinjaman_internal,nomor_anggota) values('Notif Line',%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                                """
                            nline_id = self.h2h_write_send_line('simpin_syariah_mitra_send_line',
                                                        notif_line_sql,nsend_id,member_id,
                                                        notif['employee_id'],notif['nama_anggota'],
                                                        notif['nik_anggota'],notif['simpanan_pokok'],
                                                        notif['simpanan_wajib'],notif['pinjaman_bank'],
                                                        notif['pinjaman_internal'],notif['nomor_anggota']
                                                        )
                        else:
                            notif_line_sql = """
                                insert into simpin_syariah_mitra_send_line(name,send_id,member_id,employee_id,nama_anggota,nik_anggota,
                                simpanan_pokok,simpanan_wajib,pinjaman_bank,pinjaman_internal,nomor_anggota) values('Notif Line',%s,%s,null,%s,%s,%s,%s,%s,%s,%s)
                                """
                            nline_id = self.h2h_write_send_line('simpin_syariah_mitra_send_line',
                                                        notif_line_sql,nsend_id,member_id,
                                                        False, notif['nama_anggota'],
                                                        notif['nik_anggota'],notif['simpanan_pokok'],
                                                        notif['simpanan_wajib'],notif['pinjaman_bank'],
                                                        notif['pinjaman_internal'],notif['nomor_anggota']
                                                        )
                        for ldet in notif['line_details']:
#                            raise UserError(_('ldet %s')%(ldet,))
                            yy = 0
                            for ldetail in ldet:
                                if yy>=2:
                                    det_id = self.h2h_write_send_line_detil('simpin_syariah_mitra_send_line_detail',
                                                        detil_sql,nline_id,ldetail['product_id'],
                                                        ldetail['product_name'],ldetail['amount'],
                                                        ldetail['invoice_id'],ldetail['invoice_number'],
                                                        ldetail['name']
                                                        )
                                yy += 1
                    xx+=1
            
    
    def action_email_notifikasi(self):
        """ Open a window to compose an email, with the edi invoice template
            message loaded by default
        """
#        raise UserError(_('Email Notif'))
        total_simpanan = total_pinjaman = total_pembiayaan = total_investasi = 0.0
        for member in self.member_lines:
            for simpanan in member.simpanan_ids:
                if simpanan.state=='active' and (simpanan.product_id.product_tmpl_id.name=='Simpanan Wajib' or simpanan.product_id.product_tmpl_id.name=='Simpanan Pokok'):
                    total_simpanan += simpanan.product_id.product_tmpl_id.minimal_setor
            for pinjaman in member.pinjaman_ids:
                if pinjaman.state=='active':
                    total_pinjaman += pinjaman.angsuran
            for pembiayaan in member.pembiayaan_ids:
                if pembiayaan.state=='active':
                    total_pembiayaan += pembiayaan.angsuran
#            for simpanan in member.investasi_ids:
#                total_investasi += investasi.balance
        total = total_simpanan + total_pinjaman + total_pembiayaan
        nodin = self.get_nodin()

        message = """
        Dengan Hormat, <br/><br/>

        1. Bersama surat ini kami sampaikan Pemberitahuan data potongan Karyawan """
        message += self.name
        message += " periode " + datetime.strftime(date.today(),'%B %Y') 
        message += "<br/>           sebesar Rp. " + str(f"{total:,.2f}") + " dengan rincian sebagai berikut:"
        
        message += "<br/>           a. Simpanan Wajib dan Pokok   Rp. "  + str(f"{total_simpanan:,.2f}")
        message += "<br/>           b. Potongan Pinjaman          Rp. "  + str(f"{total_pinjaman:,.2f}")
        message += "<br/>           c. Potongan Pembiayaan        Rp. "  +  str(f"{total_pembiayaan:,.2f}")

        message += """<br/>
           (rincian terlampir)<br/>

        2. Mohon agar Divisi HR dapat melakukan pemotongan atas gaji karyawan sesuai dengan data tersebut.<br/>

        3. Demikian kami sampaikan, atas perhatian dan kerjasamanya kami ucapkan terima kasih.<br/><br/>
        
        
        Hormat Kami,<br/>
        """ + self.company_id.name
        
        data_xls,filename = self.prepare_xls(self.id)
        subject = nodin + ': Pemberitahuan Rekapitulasi Potongan Karyawan ' + self.name.upper()
        email_to = self.email
        att_name = 'Rekapitulasi Potongan Karyawan ' + self.name.upper()
        att_file = self.file_xls
        att_data = self.attach_xls
        
        self.action_send_email_notifikasi(subject,message,email_to,att_name,att_file,att_data)
        notif_send = self.env['simpin_syariah.mitra.send'].create({
                                'name': 'Notifikasi ' + nodin,
                                'tanggal': date.today(),
                                'mitra_id': self.id,
                                'email': self.email,
                                'message': message,
                                'attach_xls': self.attach_xls,
                                'file_xls': self.file_xls,
                                'total_simpanan': total_simpanan,
                                'total_pinjaman': total_pinjaman,
                                'total_pembiayaan': total_pembiayaan,
                                'total_investasi': total_investasi,
                                'notif_metode': 'email',
                                'state': 'sent',
                        })
        if not notif_send:
            raise UserError(_('Terjadi Kesalahan'))

    def prepare_xls(self,mitra_id):
        filedata = filename = False
        workbook = xlwt.Workbook(encoding="utf-8")
        judul = "REKAP POTONGAN GAJI KARYAWAN "
        periode = " PERIODE PENGGAJIAN " + datetime.strftime(date.today(),'%B %Y').upper() 
        worksheet = workbook.add_sheet(judul)
        style_title = xlwt.easyxf("font:height 250; font: name Liberation Sans, bold on,color black; align: horiz center")
        style_table_header = xlwt.easyxf("font:height 220; font: name Liberation Sans, bold on,color black; align: horiz center")
        title = judul  + self.name.upper()
        worksheet.write_merge(0, 1, 0, 7,title, style = style_title)
        worksheet.write_merge(2, 3, 0, 7,periode, style = style_title)

        worksheet.col(0).width = 256 * 10
        worksheet.col(1).width = 256 * 25
        worksheet.col(2).width = 256 * 30
        worksheet.col(3).width = 256 * 30
        worksheet.col(4).width = 256 * 30
        worksheet.col(5).width = 256 * 30
        worksheet.col(6).width = 256 * 30
        worksheet.col(7).width = 256 * 40

        row = 4
        col = 0
        table_header = ['No','NIK','N A M A','Simpanan Pokok','Simpanan Wajib','Pinjaman Bank', 'Pinjaman Kopindosat','T O T A L']
        worksheet.row(row).height_mismatch = True
        worksheet.row(row).height = 256*2
        for i in range(len(table_header)):
            worksheet.write(row,col,table_header[i], style=style_table_header)
            col+=1

        baris = 1
        for member in self.member_lines:
            total_simpanan_pokok = total_simpanan_wajib = total_pinjaman_internal = total_pinjaman_bank = 0.0
            for simpanan in member.simpanan_ids:
                if simpanan.state=='active' and simpanan.product_id.product_tmpl_id.name.upper()=='SIMPANAN WAJIB':
                    total_simpanan_wajib += simpanan.product_id.product_tmpl_id.minimal_setor
                if simpanan.state=='active' and simpanan.product_id.product_tmpl_id.name.upper()=='SIMPANAN POKOK':
                    total_simpanan_pokok += simpanan.product_id.product_tmpl_id.minimal_setor
            for pinjaman in member.pinjaman_ids:
                if pinjaman.state=='active' and pinjaman.src_bank_id:
                    total_pinjaman_bank += pinjaman.angsuran
                else:
                    total_pinjaman_internal += pinjaman.angsuran
                    
            for pembiayaan in member.pembiayaan_ids:
                if pembiayaan.state=='active' and pembiayaan.src_bank_id:
                    total_pinjaman_bank += pembiayaan.angsuran
                else:
                    total_pinjaman_internal += pembiayaan.angsuran
                
#            for simpanan in member.investasi_ids:
#                total_investasi += investasi.balance
            total = total_simpanan_pokok + total_simpanan_wajib + total_pinjaman_bank + total_pinjaman_internal
            col = 0
            row+=1
            worksheet.row(row).height_mismatch = True
            worksheet.row(row).height = 256*2
            style = xlwt.easyxf("font:height 220; font: name Liberation Sans,color black;","#,##0;(#,##0);0")
            style_num = xlwt.easyxf("font:height 220; font: name Liberation Sans,color black;align: horiz right","#,##0.00;(#,##0.00);0")

            worksheet.write(row,col,baris, style=style)
            col+=1
            worksheet.write(row,col,member.nomor_induk, style=style)
            col+=1
            worksheet.write(row,col,member.name, style=style)
            col+=1
            worksheet.write(row,col,total_simpanan_pokok, style=style_num)
            col+=1
            worksheet.write(row,col,total_simpanan_wajib, style=style_num)
            col+=1
            worksheet.write(row,col,total_pinjaman_bank, style=style_num)
            col+=1
            worksheet.write(row,col,total_pinjaman_internal, style=style_num)
            col+=1
            worksheet.write(row,col,total, style=style_num)
            col+=1

        file_data = io.BytesIO()

        workbook.save(file_data)
        self.write({
        'attach_xls': base64.encodestring(file_data.getvalue()),
        'file_xls': judul+'.xls'
        })
        filedata = base64.encodestring(file_data.getvalue()),
        filename = judul+'.xls'

        return filedata,filename

######################### Integration Part
    def h2h_read(self,rsql):
        res = False
        myconz = psycopg2.connect(host=self.db_host, user=self.db_username, password=self.db_password, dbname=self.db_dbname)
        curz = myconz.cursor()
        curz.execute(rsql)
        result = curz.fetchall()
        if result is not None:
            res = result
        myconz.close()
        return res

    def h2h_write_send(self,table,wsql,tanggal,simpanan,pinjaman,mitra_id):
        res = False
        myconz = psycopg2.connect(host=self.db_host, user=self.db_username, password=self.db_password, dbname=self.db_dbname)
        curz = myconz.cursor()
        curz.execute(wsql,(tanggal,simpanan,pinjaman,mitra_id))
        myconz.commit()
        myconz.close()
        result = self.h2h_read("select id from " + table + " order by id desc limit 1")
        if result is not None:
            res = result[0]
        return res

    def h2h_write_send_line(self,table,wsql,send_id,member_id,employee_id,nama_anggota,nik_anggota,simpanan_pokok,simpanan_wajib,pinjaman_bank,pinjaman_internal,nomor_anggota):
        res = False
        myconz = psycopg2.connect(host=self.db_host, user=self.db_username, password=self.db_password, dbname=self.db_dbname)
        curz = myconz.cursor()
        if employee_id:
            curz.execute(wsql,(send_id,member_id,employee_id,nama_anggota,nik_anggota,simpanan_pokok,simpanan_wajib,pinjaman_bank,pinjaman_internal,nomor_anggota))
        else:
            curz.execute(wsql,(send_id,member_id,nama_anggota,nik_anggota,simpanan_pokok,simpanan_wajib,pinjaman_bank,pinjaman_internal,nomor_anggota))
           
        myconz.commit()
        myconz.close()
        result = self.h2h_read("select id from " + table + " order by id desc limit 1")
        if result is not None:
            res = result[0]
        return res

    def h2h_write_send_line_detil(self,table,wsql,send_line_id,product_id,product_name,amount,invoice_id,invoice_number,name):
        res = False
        myconz = psycopg2.connect(host=self.db_host, user=self.db_username, password=self.db_password, dbname=self.db_dbname)
        curz = myconz.cursor()
        curz.execute(wsql,(send_line_id,product_id,product_name,amount,invoice_id,invoice_number,name))
        myconz.commit()
        myconz.close()
        result = self.h2h_read("select id from " + table + " order by id desc limit 1")
        if result is not None:
            res = result[0]
        return res

    def h2h_get_employee_id(self,email):
        res = False
        myconz = psycopg2.connect(host=self.db_host, user=self.db_username, password=self.db_password, dbname=self.db_dbname)
        curz = myconz.cursor()
        curz.execute("select id from hr_employee where work_email=%s",(email,))
        result = curz.fetchone()
        if result is not None:
            res = result[0]
        myconz.close()
        return res
        
    def get_dest_member_id(self,nomor_anggota):
        res = False
        myconz = psycopg2.connect(host=self.db_host, user=self.db_username, password=self.db_password, dbname=self.db_dbname)
        curz = myconz.cursor()
        curz.execute("select id from simpin_member where nomor_anggota=%s",(nomor_anggota,))
        result = curz.fetchone()
        if result is not None:
            res = result[0]
        myconz.close()
        return res
        


    def h2h_get_employee_id_by_name(self,name):
        res = False
        myconz = psycopg2.connect(host=self.db_host, user=self.db_username, password=self.db_password, dbname=self.db_dbname)
        curz = myconz.cursor()
        curz.execute("select id from hr_employee where upper(name)=%s",(name.upper(),))
        result = curz.fetchone()
        if result is not None:
            res = result[0]
        myconz.close()
        return res

    def test_konek(self):
        myconz = psycopg2.connect(host=self.db_host, user=self.db_username, password=self.db_password, dbname=self.db_dbname)
        curz = myconz.cursor()
        curz.execute("SELECT version()")
        result = curz.fetchall()
        myconz.close()
        raise UserError(_('Connection Successfull \n %s')%(result,))
    
