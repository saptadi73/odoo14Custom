from odoo import api, fields, models
from datetime import datetime, timedelta, date

class SimPinPembiayaanForm(models.Model):
    _name = "simpin.syariah.pembiayaan.form"
    _description = "Pembiayaan Anggota Simpin Syariah Custom"
    _inherit = ['mail.thread', 'mail.activity.mixin']


    name = fields.Char(string='Nomor Pembiayaan')
    member_id = fields.Many2one('simpin_syariah.member', string='Nama Anggota', required=True,
                                domain=[('state', '=', 'check')])
    akad_kode = fields.Char(string='Akad Code', readonly=True, store=True)
    akad_id = fields.Many2one('master.akad_syariah', string='Jenis Akad')
    product_id = fields.Many2one('product.product', string='Produk', required=True, copy=False,
                                 track_visibility='onchange',
                                 domain=[('is_syariah', '=', True)])
    is_blokir = fields.Boolean('Blokir', default=False)
    balance = fields.Float(string='Balance', store=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submit', 'Submitted'),
        ('check', 'Check Document'),
        ('approve', 'Approved'),
    ], string='Status', default='draft', track_visibility='onchange', readonly=True)
    account_analytic_id = fields.Many2one('account.analytic.account', required=True, string='Analytic Account')
    peruntukan = fields.Many2one('master.general', string='Peruntukan', required=True,
                                 domain=[('type_umum', '=', 'peruntukan')], track_visibility='onchange')
    periode_angsuran = fields.Integer(string='Periode Angsuran', required=True, readonly=True, store=True,
                                      track_visibility='onchange', default=12)
    tanggal_akad = fields.Date(string='Tanggal Akad')
    total_pembiayaan = fields.Float(string='Nilai Pembiayaan', track_visibility='onchange', default=5000000,
                                       required=True)
    akad_tipe = fields.Selection([
        ('product', 'Barang'),
        ('service', 'Jasa')], string='Product Type', readonly=True, store=True)
    notes = fields.Text(string='Keterangan')

