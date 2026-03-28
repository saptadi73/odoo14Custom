from odoo import models, fields, api

class data_anggota(models.Model):
    _name = "data.anggota"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Data Anggota"
    _rec_name = 'anggota_id'

    anggota_id = fields.Many2one('simpin_syariah.member', 'Nama Anggota')
    kode_anggota = fields.Char(related='anggota_id.kode_anggota', string='Kode Anggota')
    # status_anggota = fields.Selection(related='peternak_id.state', string='Status Anggota')
    gmbr = fields.Binary(related='anggota_id.gmbr', string='Image')
    wilayah_id = fields.Many2one('master.wilayah', related='anggota_id.wilayah_id', string='Wilayah')
    thp = fields.Char('THP')
    prod_susu = fields.Char('Produksi Susu')
    jum_induk_laktasi = fields.Integer('Jumlah Induk Laktasi', related='anggota_id.jumlah_sapi_laktasi')
    jum_induk_kering = fields.Integer('Jumlah Induk Kering', related='anggota_id.jumlah_sapi_kering')
    jum_sapi_dara = fields.Integer('Jumlah Sapi Dara', related='anggota_id.jumlah_sapi_dara')
    fat = fields.Char('Fat')
    bj = fields.Char('BJ')
    grade = fields.Char('Grade')
    active = fields.Boolean(default=True)

    gdfp_count = fields.Integer(compute='compute_gdfp_count')

    def get_gdfp_count(self):
        action = self.env.ref('kandang_sapi.'
                              'act_gdfp_view').read()[0]
        action['domain'] = [('anggota_id', 'in', self.ids)]
        return action

    def compute_gdfp_count(self):
        for record in self:
            record.gdfp_count = self.env['entry.gdfp'].search_count(
                [('anggota_id', 'in', self.ids)])

    # @api.depends('anggota_id')
    # def _compute_jum_laktasi_kering_dara_(self):
    #     for record in self:
    #         if record.anggota_id:
    #             record.jum_induk_laktasi = record.anggota_id.jumlah_sapi_laktasi
    #             record.jum_induk_kering = record.anggota_id.jumlah_sapi_kering
    #             record.jum_sapi_dara = record.anggota_id.jumlah_sapi_dara
    #         else:
    #             record.jum_induk_laktasi = 0
    #             record.jum_induk_kering = 0
    #             record.jum_sapi_dara = 0

    # @api.onchange('anggota_id')
    # def _onchange_anggota_id(self):
    #     if not self.anggota_id:
    #         self.jum_induk_laktasi = 0
    #         self.jum_induk_kering = 0
    #         self.jum_sapi_dara = 0
    #     else:
    #         anggota_id = self.env['simpin_syariah.member'].search([('anggota_id', '=', self.anggota_id.name)], limit=1)
    #         if anggota_id:
    #             self.jum_induk_laktasi = anggota_id.jumlah_sapi_kering
    #             self.jum_induk_kering = anggota_id.jumlah_sapi_laktasi
    #             self.jum_sapi_dara = anggota_id.jumlah_sapi_dara
    #         else:
    #             self.jum_induk_laktasi = 0
    #             self.jum_induk_kering = 0
    #             self.jum_sapi_dara = 0

    # jenis_pelanggaran_ids = fields.One2many('pelanggaran.peternak', 'anggota_id', 'Jenis Pelanggaran')


    #
    # pelanggaran_gdfp_count = fields.Integer(compute='compute_pelanggaran_gdfp_count')
    #
    # def get_pelanggaran_gdfp_count(self):
    #     action = self.env.ref('peternak_sapi.'
    #                           'act_pelanggaran_view').read()[0]
    #     action['domain'] = [('peternak_id', 'in', self.ids)]
    #     return action
    #
    # def compute_pelanggaran_gdfp_count(self):
    #     for record in self:
    #         record.pelanggaran_gdfp_count = self.env['pelanggaran.peternak'].search_count(
    #             [('peternak_id', 'in', self.ids)])

#     gdfp_pelanggaran_line = fields.One2many('gdfp.pelanggaran.line', 'gdfp_pelanggaran_id', string='GDFP Pelanggaran Lines')
#
# class GDFPPelanggaranLine(models.Model):
#     _name = 'gdfp.pelanggaran.line'
#     _description = 'GDFP Pelanggaran Line'
#
#     peternak_name = fields.Many2one('peternak.sapi', string='Nama Anggota')
#     id_peternak = fields.Char(related='peternak_name.id_peternak', string='ID Anggota')
#     pelanggaran = fields.Many2one('jenis.pelanggaran', 'Pelanggaran')
#     keterangan = fields.Text('Keterangan')
#     gdfp_pelanggaran_id = fields.Many2one('data.anggota', string='GDFP Pelanggaran')