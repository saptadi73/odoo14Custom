from odoo import models, fields, api

class UploadHargaReal(models.Model):
    _name = "upload.harga.real"
    _description = "Upload Harga Real"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    periode_id = fields.Many2one('periode.setoran', 'Periode')
    tps_id = fields.Many2one('tps.liter', string='TPS')
    upload_harga_ids = fields.One2many('upload.harga.real.line', 'upload_harga_id', 'Upload Hasil Lab')

    def push_harga_real(self):
        # Ambil semua record liter.sapi yang sesuai dengan periode_id dan tps_id
        liter_sapi_records = self.env['liter.sapi'].search([
            ('periode_id', '=', self.periode_id.id),
            ('tps_id', '=', self.tps_id.id),
        ])

        # Iterasi setiap record liter.sapi dan update harga_real sesuai dengan peternak_id di upload_harga_ids
        for liter_sapi_record in liter_sapi_records:
            for upload_harga_line in self.upload_harga_ids:
                if upload_harga_line.peternak_id == liter_sapi_record.peternak_id:
                    liter_sapi_record.write({'harga_real': upload_harga_line.harga_real})

        return True

class UploadHargaRealLine(models.Model):
    _name = "upload.harga.real.line"
    _description = "Upload Harga Real Line"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    upload_harga_id = fields.Many2one('upload.harga.real', 'Upload Harga ID')
    kode_peternak = fields.Char(string='Kode Peternak')
    peternak_id = fields.Many2one('peternak.sapi', 'Peternak')
    tipe_mitra = fields.Selection([
        ('1', 'Mitra 1'),
        ('2', 'Mitra 2'),
    ], string='Tipe Mitra')
    fat = fields.Float('FAT')
    bj = fields.Float('BJ')
    ts = fields.Float('TS')
    mbrt_id = fields.Many2one('tabel.mbrt', 'MBRT')
    grade_id = fields.Many2one('tabel.grade', 'Grade')
    nilai_grade = fields.Float('Nilai Grade')
    tpc_kan = fields.Float('TPC Kan')
    snf = fields.Float('SNF')
    pro = fields.Float('Pro')
    salts = fields.Float('Salts')
    freeze = fields.Float('Freezing Point')
    lac = fields.Float('Lac')
    add_water = fields.Float('Add Water')
    harga_real = fields.Float('Harga Real')