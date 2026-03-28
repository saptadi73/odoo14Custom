{
    'name': 'Master Peternak Sapi',
    'version': '14.0.1.0',
    'license': 'LGPL-3',
    'category': 'Farm',
    "sequence": 1,
    'summary': 'Manage Peternak',
    'complexity': "easy",
    'author': 'AFajarR',
    'website': '',
    'depends': ['base', 'mail', 'master_sapi', 'kandang'],
    'data': [
            'security/ir.model.access.csv',
            'report/menu_report_peternak.xml',
            'report/peternak_card_report.xml',
            'views/menu_peternak_sapi.xml',
            'views/peternak_sapi_views.xml',
            'views/peternak_relationship_views.xml',
            'views/peternak_group_views.xml',
            'views/jabatan_group_views.xml',
            'views/master_jenis_pelanggaran_views.xml',
            'views/pelanggaran_views.xml',
            'views/usaha_sapi_views.xml',
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
