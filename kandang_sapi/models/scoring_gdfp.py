# from odoo import models, fields, api
#
# class scoring_gdfp(models.Model):
#     _name = "scoring.gdfp"
#     _inherit = ['mail.thread', 'mail.activity.mixin']
#     _description = "Scoring GDFP"
#     _rec_name = 'peternak_name'
#
#     peternak_name = fields.Many2one('peternak.sapi', 'Nama Anggota')
#     id_peternak = fields.Char(related='peternak_name.id_peternak', string='ID Peternak')
#     mpak = fields.Integer(string='Management Pakan')
#     mkan = fields.Integer(string='Management Kandang')
#     mpem = fields.Integer(string='Management Pemerahan')
#     mbis = fields.Integer(string='Daya Saing Bisnis')
#     mpel = fields.Integer(string='Pengolahan Limbah')
#     mkes = fields.Integer(string='Kesehatan Hewan')
#     nilai_mpak = fields.Integer('Nilai', compute='hitung_nilai_mpak')
#     nilai_mkan = fields.Integer('Nilai', compute='hitung_nilai_mkan')
#     nilai_mpem = fields.Integer('Nilai', compute='hitung_nilai_mpem')
#     nilai_mbis = fields.Integer('Nilai', compute='hitung_nilai_mbis')
#     nilai_mpel = fields.Integer('Nilai', compute='hitung_nilai_mpel')
#     nilai_mkes = fields.Integer('Nilai', compute='hitung_nilai_mkes')
#     total = fields.Integer('Total', compute='hitung_total_score')
#
#     @api.depends('mpak')
#     def hitung_nilai_mpak(self):
#         for record in self:
#             record.nilai_mpak = record.mpak
#
#     @api.depends('mkan')
#     def hitung_nilai_mkan(self):
#         for record in self:
#             record.nilai_mkan = record.mkan
#
#     @api.depends('mpem')
#     def hitung_nilai_mpem(self):
#         for record in self:
#             record.nilai_mpem = record.mpem
#
#     @api.depends('mbis')
#     def hitung_nilai_mbis(self):
#         for record in self:
#             record.nilai_mbis = record.mbis
#
#     @api.depends('mpel')
#     def hitung_nilai_mpel(self):
#         for record in self:
#             record.nilai_mpel = record.mpel
#
#     @api.depends('mkes')
#     def hitung_nilai_mkes(self):
#         for record in self:
#             record.nilai_mkes = record.mkes
#
#     @api.depends('nilai_mpak', 'nilai_mkan', 'nilai_mpem', 'nilai_mbis', 'nilai_mpel', 'nilai_mkes')
#     def hitung_total_score(self):
#         for record in self:
#             record.total = record.nilai_mpak + record.nilai_mkan + record.nilai_mpem + record.nilai_mbis + record.nilai_mpel + record.nilai_mkes