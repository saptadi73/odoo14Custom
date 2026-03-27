{
    'name': 'Liter Rearing',
    'version': '14.0.1.0',
    'license': 'LGPL-3',
    'category': 'Farm',
    "sequence": 1,
    'summary': 'Manage Liter Sapi Rearing',
    'complexity': "easy",
    'author': 'AFajarR',
    'website': '',
    'depends': ['mail', 'liter_sapi', 'master_sapi', 'base_accounting_kit'],
    'data': [
            'security/ir.model.access.csv',
            'views/liter_sapi_rearing_views.xml',
            'views/menu_rearing.xml',
            'views/inherit_modul_views.xml',
            ],
    'demo': [

            ],
    'css': [

        ],
    'qweb': [

            ],
    'images': [

            ],
    'installable': True,
    'auto_install': False,
    'application': True,
}