# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Simpan Pinjam Syariah',
    'Author': 'Achmad T. Zaini, Ifoel',
    'email' : '',
    'version': '1.0',
    'category': 'Simpin Syariah',
    'summary': 'Simpan Pinjam Syariah',
    'description': """
        Dasar Pengaturan Perbankan Syariah
 Fatwa-Fatwa Dewan Syariah Nasional - Majelis Ulama Indonesia (DSN – MUI)
2 Undang-Undang Nomor 21 Tahun 2008 tanggal 17 Juli 2008 tentang Perbankan Syariah.
3 Peraturan Bank Indonesia mengenai Perbankan Syariah.
4 Surat Edaran Bank Indonesia mengenai Perbankan Syariah.
    """,
    'depends': [
        "base",
        "account",
        "sale",
        "stock",
        "product",
        "asa_wilayah",
        "mail",
        "portal",
        ],
    'data': [
        'security/simpin_syariah_security.xml',
        'security/ir.model.access.csv',
        'views/syariah_menu_views.xml',
        'views/syariah_member_views.xml',
        'views/training_views.xml',
        'views/product_template_view.xml',
        'views/syariah_config_views.xml',
        'views/syariah_simpanan_views.xml',
        'views/syariah_investasi_views.xml',
        'views/syariah_pembiayaan_views.xml',
        'views/syariah_pembiayaan_korporasi_views.xml',
        'views/syariah_pinjaman_views.xml',
        'views/setoran_tarikan_views.xml',
        'views/mitra_syariah_views.xml',
        'views/mitra_bank_views.xml',
        'views/master_wilayah_views.xml',
        'views/kinerja_anggota_views.xml',
	'views/form_pinjaman_views.xml',
        'views/form_simpanan_views.xml',
        #'data/syariah_data.xml',
        'data/simpanan_data.xml',
        'data/pinjaman_data.xml',
        'data/mail_template_data.xml',
        #'report/report_simulasi_angsuran.xml',
        'report/report_profile_member.xml',
        'report/jadwal_angsuran.xml',
        'report/jadwal_angsuran_bank.xml',
        'report/report_daftar_definitif_pembiayaan.xml',
        'views/pembiayaan_portal_templates.xml',
        'data/cron_create_invoice.xml',
    ],
    'license': 'AGPL-3',
    'installable': True,
    'application': True,
    'auto_install': False
}
