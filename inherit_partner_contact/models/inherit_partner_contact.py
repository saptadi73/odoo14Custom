from odoo import api, fields, models, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    nik = fields.Char(string='NIK')

class StockPickikngSapiInherit(models.Model):
    _inherit = 'stock.move'

    tipe_id = fields.Many2one('master.tipe.sapi', 'Tipe Sapi')

class StockPickikngInherit(models.Model):
    _inherit = 'stock.picking'

    tipe_id = fields.Many2one('master.tipe.sapi', 'Tipe Sapi')