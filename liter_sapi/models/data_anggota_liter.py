from odoo import models, fields, api

class data_anggota_liter(models.Model):
    _name = "data.anggota.liter"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Data Anggota Liter"
    _rec_name = 'peternak_id'

    # peternak_name = fields.Many2one('peternak.sapi', string='Nama Anggota')
    peternak_id = fields.Many2one('peternak.sapi', string='Nama Anggota')
    kode_peternak = fields.Char(related='peternak_id.kode_peternak', string='ID Anggota')
    status_anggota = fields.Selection(related='peternak_id.state', string='Status Anggota')
    gmbr = fields.Binary(related='peternak_id.gmbr', string='Image')
    # wilayah_id = fields.Many2one('master.wilayah', related='peternak_id.wilayah_id', string='Wilayah')
    jum_induk_laktasi = fields.Integer('Jumlah Induk Laktasi', related='peternak_id.jumlah_sapi_laktasi')
    jum_induk_kering = fields.Integer('Jumlah Induk Kering', related='peternak_id.jumlah_sapi_kering')
    jum_sapi_dara = fields.Integer('Jumlah Sapi Dara', related='peternak_id.jumlah_sapi_dara')
    active = fields.Boolean(default=True)
    jenis_pelanggaran_liter_ids = fields.One2many('pelanggaran.peternak', 'peternak_id', 'Jenis Pelanggaran')

    liter_count = fields.Integer(compute='compute_liter_count')

    def get_liter_count(self):
        action = self.env.ref('liter_sapi.'
                              'act_liter_sapi_view').read()[0]
        action['domain'] = [('peternak_id', 'in', self.ids)]
        return action

    def compute_liter_count(self):
        for record in self:
            record.liter_count = self.env['liter.sapi'].search_count(
                [('peternak_id', 'in', self.ids)])

    # pelanggaran_count = fields.Integer(compute='compute_pelanggaran_count')
    #
    # def get_pelanggaran_count(self):
    #     action = self.env.ref('peternak_sapi.'
    #                           'act_pelanggaran_view').read()[0]
    #     action['domain'] = [('peternak_id', 'in', self.ids)]
    #     return action
    #
    # def compute_pelanggaran_count(self):
    #     for record in self:
    #         record.pelanggaran_count = self.env['pelanggaran.peternak'].search_count(
    #             [('peternak_id', 'in', self.ids)])

#     liter_pelanggaran_line = fields.One2many('liter.pelanggaran.line', 'liter_pelanggaran_id', string='Liter Pelanggaran Lines')
#
# class LiterPelanggaranLine(models.Model):
#     _name = 'liter.pelanggaran.line'
#     _description = 'Liter Pelanggaran Line'
#
#     peternak_sapi = fields.Many2one('peternak.sapi', string='Nama Anggota')
#     id_peternak_sapi = fields.Char(related='peternak_sapi.id_peternak', string='ID Anggota')
#     pelanggaran_id = fields.Many2one('jenis.pelanggaran', 'Pelanggaran')
#     keterangan_id = fields.Text('Keterangan')
#     liter_pelanggaran_id = fields.Many2one('data.anggota', string='Liter Pelanggaran')
