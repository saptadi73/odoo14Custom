# -*- coding: utf-8 -*-

from odoo import models, fields


class ScadaQualityControl(models.Model):
    _name = 'scada.quality.control'
    _description = 'SCADA Quality Control'
    _order = 'tanggal_uji desc, id desc'
    _rec_name = 'kode'

    product_id = fields.Many2one(
        'product.product',
        string='Product',
        required=True,
        ondelete='restrict'
    )
    product_name = fields.Char(
        string='Product Name',
        related='product_id.name',
        store=True,
        readonly=True
    )
    kode = fields.Char(string='Kode', required=True, index=True)

    quantity = fields.Float(
        string='Quantity',
        digits='Product Unit of Measure',
        required=True
    )
    uom_id = fields.Many2one(
        'uom.uom',
        string='Unit of Measure',
        related='product_id.uom_id',
        store=True,
        readonly=True
    )

    qc_type = fields.Selection([
        ('raw', 'Raw Material'),
        ('finished', 'Finished Goods')
    ], string='QC Type', required=True, default='finished')

    lot_id = fields.Many2one(
        'stock.production.lot',
        string='Lot/Serial Number'
    )

    warna = fields.Boolean(string='Warna', default=False)
    aroma = fields.Boolean(string='Aroma', default=False)
    tekstur = fields.Boolean(string='Tekstur', default=False)
    pest = fields.Boolean(string='Pest', default=False)
    kemasan = fields.Boolean(string='Kemasan', default=False)
    jahitan = fields.Boolean(string='Jahitan', default=False)
    label = fields.Boolean(string='Label', default=False)

    density = fields.Float(string='Density', digits=(16, 3))
    ka_output = fields.Float(string='KA Output', digits=(16, 3))
    ka_output_max = fields.Float(string='KA Output Max', digits=(16, 3))

    suhu_ruang = fields.Float(string='Suhu Ruang')
    suhu_produk = fields.Float(string='Suhu Produk')

    umur_barang = fields.Float(string='Umur Barang')
    umur_simpan = fields.Float(string='Umur Simpan')

    ka_supply = fields.Float(string='KA Supply', digits=(16, 3))
    ka_supply_max = fields.Float(string='KA Supply Max', digits=(16, 3))

    kadar_air = fields.Float(string='Kadar Air', digits=(16, 3))
    ka_process_max = fields.Float(string='KA Process Max', digits=(16, 3))

    tanggal_uji = fields.Date(
        string='Tanggal Uji',
        default=fields.Date.context_today,
        required=True
    )

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company
    )
