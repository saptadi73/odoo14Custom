{
    'name': 'SCADA for Odoo - Manufacturing Integration',
    'version': '6.0.52',
    'category': 'manufacturing',
    'license': 'LGPL-3',
    'author': 'PT. Gagak Rimang Teknologi',
    'website': 'https://rimang.id',
    'installable': True,
    'application': True, 
    'auto_install': False,
    'description': 'SCADA module for real-time manufacturing monitoring and control with Middleware API',
    'summary': 'SCADA module for Odoo Manufacturing with PLC Equipment integration and Middleware API',
    'depends': [
        'stock',
        'mrp',
        'web',
        'base',
    ],
    'external_dependencies': {
        'python': [
            'requests',
            'python-dateutil',
        ],
    },
    'data': [
        'security/security_groups.xml',
        'security/ir_model.xml',  # Define models explicitly before access rules
        # Views harus di-load SEBELUM ir.model.access.csv agar models terdaftar
        'views/scada_equipment_view.xml',
        'views/scada_mrp_views.xml',
        'views/scada_sensor_reading_view.xml',
        'views/scada_api_log_view.xml',
        'views/scada_quality_control_view.xml',
        'views/scada_equipment_oee_view.xml',
        'views/scada_equipment_failure_view.xml',
        # Security files setelah views
        'security/ir.model.access.csv',
        'security/ir.rule.xml',
        'views/menu.xml',
        'data/demo_data.xml',
        'data/ir_cron.xml',
        'reports/scada_quality_control_report.xml',
        'reports/scada_equipment_oee_report.xml',
    ],
    'demo': [
        'data/demo_data.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'grt_scada/static/src/css/scada_style.css',
        ],
    },
}
