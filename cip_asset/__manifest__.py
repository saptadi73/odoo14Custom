{
    'name': 'CIP Asset',
    'version': '14.0.1.0',
    'license': 'LGPL-3',
    'category': 'Asset',
    "sequence": 1,
    'summary': 'Manage Asset',
    'complexity': "easy",
    'author': 'AFajarR',
    'website': '',
    'depends': ['mail', 'liter_sapi'],
    'data': [
            'security/ir.model.access.csv',
            'views/menu_views.xml',
            "views/cip_views.xml",
            "views/cip_to_asset_views.xml",
            "views/type_cip_views.xml",
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