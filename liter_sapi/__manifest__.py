{
    'name': 'Liter Sapi',
    'version': '14.0.1.0',
    'license': 'LGPL-3',
    'category': 'Farm',
    "sequence": 1,
    'summary': 'Manage Liter Sapi',
    'complexity': "easy",
    'author': 'AFajarR',
    'website': '',
    'depends': ['mail', 'purchase', 'product', 'peternak_sapi'],
    'data': [
            'security/ir.model.access.csv',
            'views/liter_sapi_views.xml',
            'views/data_anggota_liter_views.xml',
            'views/tps_liter_views.xml',
            'views/menu_liter_sapi.xml',
            'views/tabel_def_bj.xml',
	        'views/periode_setoran_views.xml',
            'views/setoran_line.xml',
            'views/stock_picking_inherit_views.xml',
            'views/tabel_grade_views.xml',
            'views/tabel_mbrt_views.xml',
            'views/tabel_tpckan_views.xml',
            'views/tabel_tpc_views.xml',
            'views/tabel_insentif_prod_views.xml',
            'views/tabel_fat_views.xml',
            'views/tabel_bj_fat_views.xml',
            'views/tabel_ts_views.xml',
            'views/tabel_range_mbrt_views.xml',
            'views/selisih_harga_views.xml',
            # 'views/upload_harga_real_views.xml',
            'views/upload_mbrt_views.xml',
            'views/upload_hasil_lab_views.xml',
            'views/upload_centang_mbrt.xml',
            'wizard/mass_create_po_view.xml',
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