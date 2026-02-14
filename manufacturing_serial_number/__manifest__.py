# -*- coding: utf-8 -*-
{
    'name': 'Manufacturing Serial Number',
    'version': '14.0.1.0.0',
    'category': 'Manufacturing',
    'summary': 'Automatic Serial Number Generation for Manufacturing Products',
    'description': """
        Manufacturing Serial Number
        ============================
        
        Modul ini menyediakan fitur untuk:
        * Generate otomatis serial number unik untuk setiap produk manufacturing
        * Tracking serial number per Manufacturing Order
        * Laporan dan history serial number
        * Integrasi penuh dengan Manufacturing Order (MRP)
        
        Cocok untuk community edition yang membutuhkan tracking serial number
        tanpa harus menggunakan fitur berbayar.
    """,
    'author': 'Custom Development',
    'website': '',
    'depends': ['mrp', 'stock', 'product'],
    'data': [
        'security/ir.model.access.csv',
        'views/manufacturing_serial_views.xml',
        'views/mrp_production_views.xml',
        'views/product_template_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
