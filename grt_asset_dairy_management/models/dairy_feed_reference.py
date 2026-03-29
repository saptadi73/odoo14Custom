from odoo import api, fields, models


class DairyFeedReference(models.Model):
    _name = 'dairy.feed.reference'
    _description = 'Referensi Pakan Sapi Perah'
    _order = 'sequence, age_month_from, weight_from, id'
    _rec_name = 'name'

    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    name = fields.Char(string='Kode', required=True)
    age_month_from = fields.Float(string='Umur Dari (Bulan)', required=True)
    age_month_to = fields.Float(string='Umur Sampai (Bulan)', required=True)
    weight_from = fields.Float(string='BB Dari (Kg)', required=True)
    weight_to = fields.Float(string='BB Sampai (Kg)', required=True)
    daily_gain = fields.Float(string='PBH (Kg/Ek/Hr)')
    gain_to_age = fields.Float(string='PBH s/d Umur')
    concentrate_monthly_qty = fields.Float(string='Konsentrat Bulanan (Kg)')
    grass_monthly_qty = fields.Float(string='Rumput Bulanan (Kg)')
    concentrate_daily_qty = fields.Float(string='Konsentrat Harian (Kg)', required=True)
    grass_daily_qty = fields.Float(string='Rumput Harian (Kg)', required=True)
    note = fields.Char(string='Catatan')

    _sql_constraints = [
        ('name_unique', 'unique(name)', 'Kode referensi pakan harus unik.'),
    ]

    @api.model
    def find_match(self, age_months, weight):
        if age_months is None or weight is None:
            return self.browse()
        domain = [
            ('active', '=', True),
            ('age_month_from', '<=', age_months),
            ('age_month_to', '>=', age_months),
            ('weight_from', '<=', weight),
            ('weight_to', '>=', weight),
        ]
        record = self.search(domain, order='sequence, id', limit=1)
        if record:
            return record
        # fallback bertahap bila hanya umur atau hanya berat yang cocok
        domain = [
            ('active', '=', True),
            ('age_month_from', '<=', age_months),
            ('age_month_to', '>=', age_months),
        ]
        record = self.search(domain, order='sequence, id', limit=1)
        if record:
            return record
        domain = [
            ('active', '=', True),
            ('weight_from', '<=', weight),
            ('weight_to', '>=', weight),
        ]
        return self.search(domain, order='sequence, id', limit=1)
