from odoo import models, fields, api

class discharge_hospitalized(models.Model):
    _name = 'discharge.hospitalized'

    patient_id = fields.Many2one('medical.patient', string="Nama")
    sex = fields.Selection([('m', 'Male'), ('f', 'Female')], string="Sex")
    age = fields.Char(string="Age", related="patient_id.age")
    phone = fields.Char(string="Phone")
    address_id = fields.Text(string="Address")
    marital_status = fields.Selection([('s', 'Single'), ('m', 'Married'), ('w', 'Widowed'), ('d', 'Divorced'), ('x', 'Seperated')],string='Marital Status')
    cara_pemb = fields.Selection([('cash', 'Tunai'), ('tf', 'Transfer')], string="Cara Pembayaran")
    norek_medik = fields.Char('No Rek Medik')
    pribadi_penjamin = fields.Boolean('Pribadi / Penjamin')
    tgl_msk = fields.Datetime('Tanggal Masuk')
    tgl_klr = fields.Datetime('Tanggal Keluar')
    diagnosis_msk = fields.Char('Diagnosis Masuk')
    diagnosis_klr = fields.Char('Diagnosis Keluar')
    oprsi = fields.Char('Operasi / Tindakan')
    anamnese = fields.Text('Anamnese dan Pemeriksaan Fisik')
    pmrksaan = fields.Text('Pemeriksaan Penunjang dan konsumsi')
    prkmbngn = fields.Text('Perkembangan selama perawatan')
    terapi_drwt = fields.Char('Terapi Selama dirawat')
    terapi_plg = fields.Char('Terapi Pulang')
    prognosa = fields.Char('Prognosa')
    sembuh = fields.Boolean('Sembuh')
    membaik = fields.Boolean('Membaik')
    blm_sembuh = fields.Boolean('Belum Sembuh')
    meninggal_krg = fields.Boolean('Meninggal < 48 jam')
    meninggal_lbh = fields.Boolean('Meninggal > 48 jam')
    mp = fields.Boolean('RS. Mulia Pajajaran')
    lain = fields.Boolean('RS. Lain')
    pskms = fields.Boolean('Puskesmas')
    tgl_kontrol = fields.Datetime('Tanggal Kontrol')

    @api.onchange('patient_id')
    def onchange_patient_id(self):
        if self.patient_id:
            if self.patient_id.sex:
                self.sex = self.patient_id.sex
        else:
            self.sex = ''