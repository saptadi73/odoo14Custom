from odoo import models, fields, api

class UploadCentangMbrt(models.Model):
    _name = "upload.centang.mbrt"
    _description = "Upload Centang MBRT"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    periode_id = fields.Many2one('periode.setoran', 'Periode')
    tps_id = fields.Many2one('tps.liter', string='TPS')
    upload_centang_ids = fields.One2many('upload.centang.line', 'upload_centang_id', 'Upload Centang MBRT')

    def push_hasil_centang(self):
        for upload_centang_line in self.upload_centang_ids:
            # Ambil record liter.sapi yang sesuai dengan periode_id, tps_id, dan peternak_id
            liter_sapi_record = self.env['liter.sapi'].search([
                ('periode_id', '=', self.periode_id.id),
                ('tps_id', '=', self.tps_id.id),
                ('peternak_id', '=', upload_centang_line.peternak_id.id)
            ], limit=1)

            # Jika ditemukan record liter.sapi, iterasi setoran_line_ids untuk mencari tgl_setor yang sesuai
            if liter_sapi_record:
                setoran_line_record = self.env['setoran.line'].search([
                    ('liter_sapi_id', '=', liter_sapi_record.id),
                    ('tgl_setor', '=', upload_centang_line.tgl_setor),
                ], limit=1)

                # Jika ditemukan record setoran.line, update is_mbrt sesuai dengan nilai dari baris upload_centang_line
                if setoran_line_record:
                    setoran_line_record.write({
                        'is_mbrt': upload_centang_line.is_mbrt,
                    })

                    # Recompute the jumlah_mbrt field for the liter_sapi_record
                    liter_sapi_record._compute_jumlah_mbrt()

        return True

class UploadCentangLine(models.Model):
    _name = "upload.centang.line"
    _description = "Upload Centang Line"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    upload_centang_id = fields.Many2one('upload.centang.mbrt', 'Upload Lab ID')
    kode_peternak = fields.Char(string='Kode Peternak')
    peternak_id = fields.Many2one('peternak.sapi', 'Peternak')
    tgl_setor = fields.Date('Tanggal Setor')
    is_mbrt = fields.Boolean('Is MBRT?')