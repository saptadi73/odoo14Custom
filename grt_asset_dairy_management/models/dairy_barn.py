from odoo import api, fields, models


class KandangSapiPerah(models.Model):
    _inherit = 'kandang.sapi.perah'

    code = fields.Char(string='Kode Kandang', copy=False, readonly=True, default='New')
    lokasi = fields.Char(string='Lokasi Detail')
    luas = fields.Float(string='Luas (m2)')
    kapasitas = fields.Integer(string='Kapasitas Ekor')
    latitude = fields.Float(string='Latitude', digits=(16, 6))
    longitude = fields.Float(string='Longitude', digits=(16, 6))
    notes = fields.Text(string='Catatan')
    active = fields.Boolean(default=True)
    dairy_cow_count = fields.Integer(
        string='Jumlah Sapi',
        compute='_compute_dairy_cow_count',
    )

    @api.depends('sapi_kandang_ids')
    def _compute_dairy_cow_count(self):
        for record in self:
            record.dairy_cow_count = len(record.sapi_kandang_ids)

    @api.model
    def create(self, vals):
        if vals.get('code', 'New') == 'New':
            vals['code'] = self.env['ir.sequence'].next_by_code('kandang.sapi.perah.code') or 'New'
        return super(KandangSapiPerah, self).create(vals)
