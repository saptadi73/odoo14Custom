{
    'name': 'Kandang Sapi',
    'version': '14.0.1.0',
    'license': 'LGPL-3',
    'category': 'Farm',
    "sequence": 1,
    'summary': 'Manage Sapi',
    'complexity': "easy",
    'author': 'AFajarR',
    'website': '',
    'depends': ['base', 'mail','master_sapi'],
    'data': [
            'views/kandang_sapi_views.xml',
            'views/master_jenis_kandang_views.xml',
            'views/menu_kandang.xml',
            'security/ir.model.access.csv',
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