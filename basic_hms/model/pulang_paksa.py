from odoo import models, fields, api

class pulang_paksa(models.Model):
    _name = 'pulang.paksa'

    patient_id = fields.Many2one('medical.patient', string="Nama")
    sex = fields.Selection([('m', 'Male'), ('f', 'Female')], string="Sex")
    age = fields.Char(string="Age", related="patient_id.age")
    phone = fields.Char(string="Phone")
    address_id = fields.Text(string="Address")
    tgl = fields.Datetime('Tanggal')
    marital_status = fields.Selection([('s', 'Single'), ('m', 'Married'), ('w', 'Widowed'), ('d', 'Divorced'), ('x', 'Seperated')],string='Marital Status')
    bukti_ktp = fields.Char('Bukti Diri I KTP')
    ortu = fields.Boolean('Orang Tua')
    suami = fields.Boolean('Suami')
    istri = fields.Boolean('Istri')
    keluarga = fields.Boolean('Keluarga')
    anak = fields.Boolean('Anak * Dari Pasien')
    name_id = fields.Many2one('res.partner', string="Yang Bernama")
    jk = fields.Char('Jenis Kelamin')
    umur = fields.Char('Age')
    almt = fields.Text('Alamat')
    drwt_di = fields.Many2one('res.partner', string="Dirawat Di")


