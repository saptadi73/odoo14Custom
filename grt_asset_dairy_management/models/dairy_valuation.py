from odoo import fields, models


class DairyValuationHistory(models.Model):
    _name = 'dairy.valuation.history'
    _description = 'Riwayat Valuasi Sapi Dairy'
    _order = 'valuation_date desc, id desc'

    sapi_id = fields.Many2one('sapi', string='Sapi', required=True, ondelete='cascade')
    valuation_date = fields.Date(string='Tanggal Valuasi', required=True, default=fields.Date.context_today)
    company_id = fields.Many2one('res.company', related='sapi_id.company_id', store=True, readonly=True)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', readonly=True)
    meat_price_per_kg = fields.Monetary(string='Harga Daging/Kg', currency_field='currency_id')
    bcs_reference_id = fields.Many2one('dairy.bcs.reference', string='BCS')
    market_weight = fields.Float(string='Bobot Pasar Acuan (Kg)')
    market_value = fields.Monetary(string='Nilai Pasar', currency_field='currency_id')
    book_value = fields.Monetary(string='Nilai Buku', currency_field='currency_id')
    chkpn_target_value = fields.Monetary(string='CHKPN Seharusnya', currency_field='currency_id')
    recognized_before = fields.Monetary(string='CHKPN Sebelum', currency_field='currency_id')
    delta_value = fields.Monetary(string='Delta CHKPN', currency_field='currency_id')
    recognized_after = fields.Monetary(string='CHKPN Setelah', currency_field='currency_id')
    journal_move_id = fields.Many2one('account.move', string='Jurnal')
    note = fields.Char(string='Catatan')
