from odoo import api, fields, models


class DairyMeatPriceHistory(models.Model):
    _name = 'dairy.meat.price.history'
    _description = 'Riwayat Harga Daging Dairy'
    _order = 'date desc, id desc'
    _rec_name = 'date'

    date = fields.Date(required=True, default=fields.Date.context_today)
    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', readonly=True)
    price_per_kg = fields.Monetary(string='Harga Daging per Kg', required=True, currency_field='currency_id')
    note = fields.Char(string='Catatan')

    @api.model
    def create(self, vals):
        record = super(DairyMeatPriceHistory, self).create(vals)
        if record.company_id:
            record.company_id.dairy_meat_price_per_kg = record.price_per_kg
        return record
