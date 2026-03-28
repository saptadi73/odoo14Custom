from odoo import models, fields, api, _
from odoo import exceptions


class form_kunjungan(models.Model):
    _name = "form.kunjungan"
    _description = "Form Kunjungan"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'code'

    code = fields.Char(string="Number")
    petugas_id = fields.Many2one('medical.physician', 'Petugas')
    # jenis_kunjungan_id = fields.Many2one('master.jenis.kunjungan', 'Jenis Kunjungan')
    jenis_kunjungan_ids = fields.Many2many('master.jenis.kunjungan')
    solusi_kunjungan_ids = fields.Many2many('master.solusi.kunjungan')
    peternak_id = fields.Many2one('peternak.sapi', 'Nama Anggota')
    kode_peternak = fields.Char(related='peternak_id.kode_peternak', string='ID Peternak')
    tanggal_kunjungan = fields.Datetime('Tanggal Kunjungan')
    note = fields.Text('Catatan')

    @api.model
    def create(self, vals):
        if vals.get("code", "") == "":
            vals["code"] = self.env["ir.sequence"].next_by_code("form.kunjungan")
        result = super(form_kunjungan, self).create(vals)
        return result
