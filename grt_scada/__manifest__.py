{
    'name': 'SCADA for Odoo - Manufacturing Integration',
    'version': '7.0.79',
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
        # Security - FIRST
        'security/security_groups.xml',
        # External views inheritance - EARLY
        # Temporary: disabled due view validation issue on current runtime (safe_eval opcode check)
        # 'views/scada_mrp_views.xml',
        'views/scada_product_views.xml',
        # Core SCADA views
        'views/scada_equipment_view.xml',
        'views/scada_sensor_reading_view.xml',
        'views/scada_api_log_view.xml',
        'views/scada_quality_control_view.xml',
        'views/scada_equipment_oee_view.xml',
        'views/scada_equipment_failure_view.xml',
        'views/scada_mo_bulk_wizard_view.xml',
        # Menus - AFTER all views (references actions from views)
        'views/menu.xml',
        # Data files
        'data/demo_data.xml',
        'data/ir_cron.xml',
        # Reports
        'reports/scada_quality_control_report.xml',
        'reports/scada_equipment_oee_report.xml',
        # Security access control - LAST
        'security/ir.model.access.csv',
        'security/ir.rule.xml',
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
