{
    'name': 'Kandang Sapi',
    'version': '14.0.1.0',
    'license': 'LGPL-3',
    'category': 'Farm',
    "sequence": 1,
    'summary': 'Manage Kandang Sapi',
    'complexity': "easy",
    'author': 'AFajarR',
    'website': '',
    'depends': ['base', 'mail', 'asa_simpin_syariah', 'peternak_sapi', 'liter_sapi', 'basic_hms', 'master_sapi'],
    'data': [
            'security/ir.model.access.csv',
            'data/sequence.xml',
            'views/menu_kandang.xml',
            # 'views/fasilitas_kandang_views.xml',
            'views/data_anggota_views.xml',
            'views/master_jenis_kunjungan_views.xml',
            # 'views/scoring_gdfp_views.xml',
            # 'views/gdfp_views.xml',
            'views/master_jenis_pakan_tambah_views.xml',
            'views/form_kunjungan_views.xml',
            'views/form_kunjungan_gdfp_views.xml',
            'views/master_tabel_hijauan.xml',
            'views/master_tabel_konsentrat.xml',
            'views/master_tabel_pakan_tambah.xml',
            'views/master_solusi_kunjungan_views.xml',

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
