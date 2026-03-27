# -*- coding: utf-8 -*-
{
    'name': 'Sales Profit and Loss Report',
    'version': '14.0.0.1',
    'summary': 'Sale order wise profit report',
    'category': 'Sale',
    'author': 'Odoo Decoder',
    'company': 'Odoo Decoder',
    'website': 'https://odoodecoder.odoo.com/',
    'depends': [
        'sale_management',
        'report_xlsx',
        'sale_margin'
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/profit_report_sale.xml',
        'views/report.xml',
        'wizard/profit_report_wizard_view.xml',
    ],
    'license': 'AGPL-3',
    'images': ['static/description/banner.gif'],
    'installable': True,
    'auto_install': False,
    'application': False,
    'live_test_url': 'https://youtu.be/w0hugb1OVJ8',
}
