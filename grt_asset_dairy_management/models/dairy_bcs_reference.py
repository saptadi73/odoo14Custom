from odoo import fields, models


class DairyBcsReference(models.Model):
    _name = 'dairy.bcs.reference'
    _description = 'Referensi BCS Sapi Perah'
    _order = 'score, id'
    _rec_name = 'display_name_custom'

    active = fields.Boolean(default=True)
    score = fields.Float(string='BCS', required=True)
    weight_min = fields.Float(string='Berat Minimum (Kg)', required=True)
    weight_max = fields.Float(string='Berat Maksimum (Kg)', required=True)
    weight_average = fields.Float(string='Berat Rata-rata (Kg)', required=True)
    market_value_reference = fields.Monetary(string='Nilai Pasar Referensi', currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    note = fields.Char(string='Catatan')
    display_name_custom = fields.Char(string='Display Name', compute='_compute_display_name', store=False)

    _sql_constraints = [
        ('score_unique', 'unique(score)', 'Nilai BCS harus unik.'),
    ]

    def _compute_display_name(self):
        for record in self:
            record.display_name_custom = 'BCS %s' % (record.score,)
