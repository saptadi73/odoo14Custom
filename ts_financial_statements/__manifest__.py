# -*- coding: utf-8 -*-
{
    'name': "Vertical Financial Statements by Company or Analytical Account",
    'version': '14.0.1.0',
    'category': 'Accounting/Accounting',
    'summary': """Financial Statement Reports""",

    'description': """
        Long description of module's purpose
    """,

    'author': 'TeamUp4Solutions, TaxDotCom',
    'website': "http://www.taxdotcom.com",
    'maintainer': 'Sohail Ahmad',
    # any module necessary for this one to work correctly
    'depends': ['base','account','asa_company_konsol'],
    'data': [
        'wizard/ts_financial_reports_wizard.xml',
        'security/ir.model.access.csv',
        'reports/report.xml',
        'views/views.xml',
        'views/ts_reports_config_view.xml',
    ],
    
    'installable': True,
    'auto_install': False,
    'price': 70.00,
    'currency': 'EUR',
    'images': ['static/description/banner.gif'],
    'license': 'OPL-1',
}
