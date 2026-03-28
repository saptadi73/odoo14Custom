from odoo import models, fields, api, _

class service_conception(models.Model):
    _name = "service.conception"
    _description = "S/C (Service/ Conception)"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'id_sapi'

    id_sapi = fields.Many2one('sapi', 'Sapi')
    tps_id = fields.Many2one('tps.liter', 'TPS')
    tgl_sc = fields.Date('Tanggal')
    ib_ke = fields.Integer('IB Ke')
    id_status_reproduksi = fields.Many2one('master.status.reproduksi', 'Status Reproduksi')
    nilai_sc = fields.Integer('Nilai S/C')

    # @api.depends('ib_ke', 'stts_reprod_id')
    # def _compute_nilai_sc(self):
    #     for record in self:
    #         if record.stts_reprod_id.nama_status_reproduksi == 'Bunting':
    #             record.nilai_sc = record.ib_ke
    #         else:
    #             record.nilai_sc = 0

# class calving_interval(models.Model):
#     _name = "calving.interval"
#     _description = "CI ( Calving Interval)"
#     _inherit = ['mail.thread', 'mail.activity.mixin']
#     _rec_name = 'sapi_id'
#
#     sapi_id = fields.Many2one('sapi', 'Sapi')
#     tps_id = fields.Many2one('tps.liter', 'TPS')
#     tgl_ci = fields.Date('Tanggal')
#     stts_reprod_id = fields.Many2one('master.status.reproduksi', 'Status Reproduksi')
#     nilai_sc = fields.Integer('Nilai S/C')