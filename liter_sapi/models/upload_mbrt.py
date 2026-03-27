from odoo import models, fields, api

class UploadMbrt(models.Model):
    _name = "upload.mbrt"
    _description = "Upload MBRT"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    periode_id = fields.Many2one('periode.setoran', 'Periode')
    tps_id = fields.Many2one('tps.liter', string='TPS')
    upload_mbrt_ids = fields.One2many('upload.mbrt.line', 'upload_mbrt_id', 'Upload MBRT')

    def push_mbrt(self):
        for upload_mbrt_line in self.upload_mbrt_ids:
            # Ambil record liter.sapi yang sesuai dengan periode_id, tps_id, dan peternak_id dari baris upload_mbrt_line
            liter_sapi_record = self.env['liter.sapi'].search([
                ('periode_id', '=', self.periode_id.id),
                ('tps_id', '=', self.tps_id.id),
                ('peternak_id', '=', upload_mbrt_line.peternak_id.id),
            ], limit=1)

            # Jika ditemukan record liter.sapi, update mbrt_id dan is_mbrt sesuai dengan nilai dari baris upload_mbrt_line
            if liter_sapi_record:
                liter_sapi_record.write({
                    'mbrt_id': upload_mbrt_line.mbrt_id.id,
                })

                # Panggil metode onchange untuk grade_id
                liter_sapi_record._onchange_mbrt_id()

        return True

class UploadMbrtLine(models.Model):
    _name = "upload.mbrt.line"
    _description = "Upload MBRT Line"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    upload_mbrt_id = fields.Many2one('upload.mbrt', 'Upload MBRT ID')
    kode_peternak = fields.Char(string='Kode Peternak')
    peternak_id = fields.Many2one('peternak.sapi', 'Peternak')
    mbrt_id = fields.Many2one('tabel.mbrt', 'MBRT')
    is_mbrt = fields.Boolean('Is MBRT?')