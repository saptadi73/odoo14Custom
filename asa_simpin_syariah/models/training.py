from odoo import models, fields, api

class training(models.Model):
    _name = "training"
    _description = "Training Anggota"
    _rec_name = 'program_name'

    program_name = fields.Char(string='Training Program', required=True)
    date_from = fields.Datetime(string="Date From")
    date_to = fields.Datetime(string="Date To")
    responsible = fields.Many2one('res.users', 'Responsible')
    training_line_ids = fields.One2many('training.line', 'training_line_id', string='Training Line Ids')

class training_line(models.Model):
    _name = "training.line"
    _description = "Training Anggota Line"
    _rec_name = 'anggota_id'

    anggota_id = fields.Many2one('simpin_syariah.member', 'Anggota')
    kode_anggota = fields.Char('Kode Anggota', related='anggota_id.kode_anggota')
    jabatan_id = fields.Char('Jabatan', compute='_compute_jabatan_id')
    ceklis = fields.Boolean('Ceklis')
    training_line_id = fields.Many2one('training', 'Training Line Id')

    @api.depends('anggota_id')
    def _compute_jabatan_id(self):
        for record in self:
            record.jabatan_id = record.anggota_id.jabatan_id.jabatan if record.anggota_id and record.anggota_id.jabatan_id else False
