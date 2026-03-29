from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    dairy_concentrate_ratio = fields.Float(
        string='Rasio Konsentrat',
        default=0.02,
        help='Kg konsentrat per 1 kg bobot badan sapi.',
    )
    dairy_grass_ratio = fields.Float(
        string='Rasio Rumput',
        default=0.10,
        help='Kg rumput per 1 kg bobot badan sapi.',
    )
    dairy_concentrate_product_id = fields.Many2one(
        'product.product',
        string='Produk Konsentrat',
        domain=[('type', 'in', ['product', 'consu'])],
    )
    dairy_grass_product_id = fields.Many2one(
        'product.product',
        string='Produk Rumput',
        domain=[('type', 'in', ['product', 'consu'])],
    )
    dairy_vitamin_product_id = fields.Many2one(
        'product.product',
        string='Produk Vitamin',
        domain=[('type', 'in', ['product', 'consu', 'service'])],
    )
    dairy_insemination_product_id = fields.Many2one(
        'product.product',
        string='Produk Inseminasi',
        domain=[('type', 'in', ['product', 'consu', 'service'])],
    )
    dairy_feed_source_location_id = fields.Many2one(
        'stock.location',
        string='Lokasi Sumber Pakan',
    )
    dairy_feed_consumption_location_id = fields.Many2one(
        'stock.location',
        string='Lokasi Konsumsi Pakan',
    )
    dairy_medical_source_location_id = fields.Many2one(
        'stock.location',
        string='Lokasi Gudang Medis',
    )
    dairy_medical_consumption_location_id = fields.Many2one(
        'stock.location',
        string='Lokasi Konsumsi Medis',
    )
    dairy_vitamin_source_location_id = fields.Many2one(
        'stock.location',
        string='Lokasi Sumber Vitamin',
        help='Field lama. Jika lokasi gudang medis belum diisi, modul akan fallback ke field ini.',
    )
    dairy_vitamin_consumption_location_id = fields.Many2one(
        'stock.location',
        string='Lokasi Konsumsi Vitamin',
        help='Field lama. Jika lokasi konsumsi medis belum diisi, modul akan fallback ke field ini.',
    )
    dairy_feed_journal_id = fields.Many2one(
        'account.journal',
        string='Jurnal Pakan',
        domain=[('type', '=', 'general')],
    )
    dairy_capitalization_journal_id = fields.Many2one(
        'account.journal',
        string='Jurnal Kapitalisasi Asset Biologis',
        domain=[('type', '=', 'general')],
    )
    dairy_treatment_journal_id = fields.Many2one(
        'account.journal',
        string='Jurnal Vitamin dan Inseminasi',
        domain=[('type', '=', 'general')],
    )
    dairy_feed_inventory_account_id = fields.Many2one(
        'account.account',
        string='Akun Kredit Persediaan Pakan',
        domain=[('deprecated', '=', False)],
    )
    dairy_feed_asset_account_id = fields.Many2one(
        'account.account',
        string='Akun Asset Biologis Belum Produksi',
        domain=[('deprecated', '=', False)],
    )
    dairy_feed_expense_account_id = fields.Many2one(
        'account.account',
        string='Akun Beban Pakan Produksi',
        domain=[('deprecated', '=', False)],
    )
    dairy_vitamin_credit_account_id = fields.Many2one(
        'account.account',
        string='Akun Kredit Vitamin',
        domain=[('deprecated', '=', False)],
        help='Untuk vitamin berbasis stok, isi dengan akun persediaan vitamin agar jurnal selaras dengan pengurangan stok.',
    )
    dairy_vitamin_expense_account_id = fields.Many2one(
        'account.account',
        string='Akun Beban Vitamin Produksi',
        domain=[('deprecated', '=', False)],
    )
    dairy_insemination_credit_account_id = fields.Many2one(
        'account.account',
        string='Akun Kredit Inseminasi',
        domain=[('deprecated', '=', False)],
    )
    dairy_insemination_expense_account_id = fields.Many2one(
        'account.account',
        string='Akun Beban Inseminasi Produksi',
        domain=[('deprecated', '=', False)],
    )
    dairy_asset_category_id = fields.Many2one(
        'account.asset.category',
        string='Kategori Asset Sapi Produksi',
        domain=[('type', '=', 'purchase')],
    )
    dairy_analytic_account_id = fields.Many2one(
        'account.analytic.account',
        string='Analytic Account Dairy',
    )

    dairy_meat_price_per_kg = fields.Monetary(
        string='Harga Daging per Kg',
        currency_field='currency_id',
        default=40000.0,
        help='Harga daging per kg saat ini untuk perhitungan nilai pasar berdasarkan BCS.',
    )

    dairy_impairment_journal_id = fields.Many2one(
        'account.journal',
        string='Jurnal CHKPN',
        domain=[('type', '=', 'general')],
    )
    dairy_impairment_expense_account_id = fields.Many2one(
        'account.account',
        string='Akun Beban CHKPN',
        domain=[('deprecated', '=', False)],
    )
    dairy_impairment_allowance_account_id = fields.Many2one(
        'account.account',
        string='Akun Cadangan CHKPN',
        domain=[('deprecated', '=', False)],
    )
    dairy_impairment_recovery_account_id = fields.Many2one(
        'account.account',
        string='Akun Pemulihan CHKPN',
        domain=[('deprecated', '=', False)],
    )


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    dairy_concentrate_ratio = fields.Float(related='company_id.dairy_concentrate_ratio', readonly=False)
    dairy_grass_ratio = fields.Float(related='company_id.dairy_grass_ratio', readonly=False)
    dairy_concentrate_product_id = fields.Many2one(related='company_id.dairy_concentrate_product_id', readonly=False)
    dairy_grass_product_id = fields.Many2one(related='company_id.dairy_grass_product_id', readonly=False)
    dairy_vitamin_product_id = fields.Many2one(related='company_id.dairy_vitamin_product_id', readonly=False)
    dairy_insemination_product_id = fields.Many2one(related='company_id.dairy_insemination_product_id', readonly=False)
    dairy_feed_source_location_id = fields.Many2one(related='company_id.dairy_feed_source_location_id', readonly=False)
    dairy_feed_consumption_location_id = fields.Many2one(related='company_id.dairy_feed_consumption_location_id', readonly=False)
    dairy_medical_source_location_id = fields.Many2one(related='company_id.dairy_medical_source_location_id', readonly=False)
    dairy_medical_consumption_location_id = fields.Many2one(related='company_id.dairy_medical_consumption_location_id', readonly=False)
    dairy_vitamin_source_location_id = fields.Many2one(related='company_id.dairy_vitamin_source_location_id', readonly=False)
    dairy_vitamin_consumption_location_id = fields.Many2one(related='company_id.dairy_vitamin_consumption_location_id', readonly=False)
    dairy_feed_journal_id = fields.Many2one(related='company_id.dairy_feed_journal_id', readonly=False)
    dairy_capitalization_journal_id = fields.Many2one(related='company_id.dairy_capitalization_journal_id', readonly=False)
    dairy_treatment_journal_id = fields.Many2one(related='company_id.dairy_treatment_journal_id', readonly=False)
    dairy_feed_inventory_account_id = fields.Many2one(related='company_id.dairy_feed_inventory_account_id', readonly=False)
    dairy_feed_asset_account_id = fields.Many2one(related='company_id.dairy_feed_asset_account_id', readonly=False)
    dairy_feed_expense_account_id = fields.Many2one(related='company_id.dairy_feed_expense_account_id', readonly=False)
    dairy_vitamin_credit_account_id = fields.Many2one(related='company_id.dairy_vitamin_credit_account_id', readonly=False)
    dairy_vitamin_expense_account_id = fields.Many2one(related='company_id.dairy_vitamin_expense_account_id', readonly=False)
    dairy_insemination_credit_account_id = fields.Many2one(related='company_id.dairy_insemination_credit_account_id', readonly=False)
    dairy_insemination_expense_account_id = fields.Many2one(related='company_id.dairy_insemination_expense_account_id', readonly=False)
    dairy_asset_category_id = fields.Many2one(related='company_id.dairy_asset_category_id', readonly=False)
    dairy_analytic_account_id = fields.Many2one(related='company_id.dairy_analytic_account_id', readonly=False)
    dairy_meat_price_per_kg = fields.Monetary(related='company_id.dairy_meat_price_per_kg', readonly=False)
    dairy_impairment_journal_id = fields.Many2one(related='company_id.dairy_impairment_journal_id', readonly=False)
    dairy_impairment_expense_account_id = fields.Many2one(related='company_id.dairy_impairment_expense_account_id', readonly=False)
    dairy_impairment_allowance_account_id = fields.Many2one(related='company_id.dairy_impairment_allowance_account_id', readonly=False)
    dairy_impairment_recovery_account_id = fields.Many2one(related='company_id.dairy_impairment_recovery_account_id', readonly=False)
