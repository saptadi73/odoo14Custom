from odoo import models, fields, api

class UploadHasilLab(models.Model):
    _name = "upload.hasil.lab"
    _description = "Upload Hasil Lab"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    periode_id = fields.Many2one('periode.setoran', 'Periode')
    tps_id = fields.Many2one('tps.liter', string='TPS')
    upload_lab_ids = fields.One2many('upload.lab.line', 'upload_lab_id', 'Upload Hasil Lab')

    def push_hasil_lab(self):
        for upload_lab_line in self.upload_lab_ids:
            # Ambil record liter.sapi yang sesuai dengan periode_id, tps_id, dan peternak_id dari baris upload_mbrt_line
            liter_sapi_record = self.env['liter.sapi'].search([
                ('periode_id', '=', self.periode_id.id),
                ('tps_id', '=', self.tps_id.id),
                ('peternak_id', '=', upload_lab_line.peternak_id.id),
            ], limit=1)

            # Jika ditemukan record liter.sapi, update mbrt_id dan is_mbrt sesuai dengan nilai dari baris upload_mbrt_line
            if liter_sapi_record:
                liter_sapi_record.write({
                    'fat_id': upload_lab_line.fat_id.id,
                    'snf': upload_lab_line.snf,
                    'pro': upload_lab_line.pro,
                    'salts': upload_lab_line.salts,
                    'freez_point': upload_lab_line.freeze,
                    'tpc_kan': upload_lab_line.tpc_kan,

                })

        return True

    # def push_hasil_lab(self):
    #     # Ambil semua record liter.sapi yang sesuai dengan periode_id dan tps_id
    #     liter_sapi_records = self.env['liter.sapi'].search([
    #         ('periode_id', '=', self.periode_id.id),
    #         ('tps_id', '=', self.tps_id.id),
    #     ])
    #
    #     # Buat dictionary untuk mapping peternak_id dengan hasil lab
    #     upload_lab_dict = {
    #         upload_lab_line.peternak_id.id: upload_lab_line
    #         for upload_lab_line in self.upload_lab_ids
    #     }
    #
    #     # Iterate through each liter.sapi record and update fields based on the lab results
    #     for liter_sapi_record in liter_sapi_records:
    #         upload_lab_line = upload_lab_dict.get(liter_sapi_record.peternak_id.id)
    #         if upload_lab_line:
    #             liter_sapi_record.write({
    #                 'bj_id': upload_lab_line.bj_id.id,
    #                 'fat_id': upload_lab_line.fat_id.id,
    #                 'ts': upload_lab_line.ts,
    #             })
    #
    #     return True

class UploadLabLine(models.Model):
    _name = "upload.lab.line"
    _description = "Upload Lab Line"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    upload_lab_id = fields.Many2one('upload.hasil.lab', 'Upload Lab ID')
    kode_peternak = fields.Char(string='Kode Peternak')
    peternak_id = fields.Many2one('peternak.sapi', 'Peternak')
    tipe_mitra = fields.Selection([
        ('1', 'Mitra 1'),
        ('2', 'Mitra 2'),
    ], string='Tipe Mitra')
    fat_id = fields.Many2one('tabel.fat', 'FAT')
    bj_id = fields.Many2one('tabel.bj.fat', 'BJ')
    ts = fields.Float('TS')
    mbrt_id = fields.Many2one('tabel.mbrt', 'MBRT')
    grade_id = fields.Many2one('tabel.grade', 'Grade')
    nilai_grade = fields.Float('Nilai Grade')
    tpc_kan = fields.Char('TPC Kan')
    snf = fields.Float('SNF')
    pro = fields.Float('Pro')
    salts = fields.Float('Salts')
    freeze = fields.Float('Freezing Point')
    lac = fields.Float('Lac')
    add_water = fields.Float('Add Water')
    harga_real = fields.Float('Harga Real')