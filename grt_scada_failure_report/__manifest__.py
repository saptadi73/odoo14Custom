{
    'name': 'SCADA Failure Reporting',
    'version': '14.0.1.0.0',
    'category': 'manufacturing',
    'license': 'LGPL-3',
    'author': 'Custom',
    'installable': True,
    'application': False,
    'depends': [
        'base',
        'web',
        'grt_scada',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/scada_failure_report_views.xml',
        'views/scada_failure_report_menu.xml',
    ],
}
