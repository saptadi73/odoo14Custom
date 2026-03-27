{
    'name': 'Data Sapi',
    'version': '14.0.1.0',
    'license': 'LGPL-3',
    'category': 'Farm',
    "sequence": 1,
    'summary': 'Manage Sapi',
    'complexity': "easy",
    'author': 'AFajarR',
    'website': '',
    'depends': ['base', 'mail'],
    'data': [
            'security/ir.model.access.csv',
            'views/sapi_views.xml',
            'views/sapi_menu_view.xml',
            'views/sapi_portal_views.xml',
            'views/jenis_sapi_master_views.xml',
            'views/master_jenis_specimen_views.xml',
            'views/formulasi_sisi_views.xml',
            'views/pejantan_views.xml',
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