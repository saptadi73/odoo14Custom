from odoo import models, fields, api

class pulang_sendiri(models.Model):
    _name = 'pulang.sendiri'

    patient_id = fields.Many2one('medical.patient', string="Nama")
    sex = fields.Selection([('m', 'Male'), ('f', 'Female')], string="Sex")
    age = fields.Char(string="Age", related="patient_id.age")
    phone = fields.Char(string="Phone")
    address_id = fields.Text(string="Address")
    tgl = fields.Datetime('Tanggal')
    identitas = fields.Selection([('ktp', 'KTP'),('sim','SIM')], string="Jenis Identitas")
    sdr = fields.Boolean('Sendiri')
    suami = fields.Boolean('Suami')
    istri = fields.Boolean('Istri')
    ayah = fields.Boolean('Ayah')
    ibu = fields.Boolean('Ibu')
    anak = fields.Boolean('Anak * Dari Pasien')
    sdr_kdg = fields.Boolean('Saudara Kandung')
    wali = fields.Boolean('Wali Yang Sah')
    name_id = fields.Many2one('res.partner', string="Yang Bernama")
    jk = fields.Char('Jenis Kelamin')
    umur = fields.Char('Age')
    almt = fields.Text('Alamat')
    hp = fields.Char(string="Phone")
    no_rm = fields.Char('No. RM')