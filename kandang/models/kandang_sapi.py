from odoo import models, fields

class kandang_sapi_perah(models.Model):
    _name = "kandang.sapi.perah"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Kandang Sapi"
    _rec_name = 'nama_peternakan'

    image = fields.Binary('Image')
    nama_peternakan = fields.Char(string='Nama Peternakan/Kandang')
    jns_kdg = fields.Many2one('jenis.kandang', 'Jenis Kandang')
    almt = fields.Char('Alamat')
    kelurahan_id = fields.Many2one('wilayah.kelurahan', string='Kelurahan')
    kecamatan_id = fields.Many2one('wilayah.kecamatan', string='Kecamatan')
    kabkota_id = fields.Many2one('wilayah.kabkota', string='Kab / Kota')
    provinsi_id = fields.Many2one('wilayah.provinsi', string='Provinsi')
    state = fields.Selection([
        ('sendiri', 'Milik Sendiri'),
        ('terpisah', 'Terpisah'),
        ('Perusahaan', 'Perusahaan'),
    ], string='Status Kepemilikan')
    status_kepemilikan = fields.Selection([
        ('sendiri', 'Milik Sendiri'),
        ('terpisah', 'Terpisah'),
        ('Perusahaan', 'Perusahaan'),
    ], string='Status Kepemilikan')
    sapi_kandang_ids = fields.One2many('sapi', 'kandang_id', 'Sapi')
    wilayah_id = fields.Many2one('master.wilayah', 'Wilayah', required=True)


class jenis_kandang(models.Model):
    _name = "jenis.kandang"
    _rec_name = "kandang_name"
    _description = "Kandang Sapi"

    kandang_name = fields.Char('Nama', placeholder="Nama Fasilitas")
    luas_kandang = fields.Char('Luas Kandang')
    lantai = fields.Char('Jenis Lantai')
    atap = fields.Char('Jenis Atap')

class KandangInheritSapi(models.Model):
    _inherit = "sapi"

    kandang_id = fields.Many2one('kandang.sapi.perah', 'Kandang')