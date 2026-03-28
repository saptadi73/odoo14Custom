# -*- coding: utf-8 -*-

{
    "name": "Payroll Knjabung",
    "version": "1.01",
    "author": "Ifoel Arbeis - 08156814955",
    "license": "",
    "category": "HR",
    "website": "",
    "depends": ["hr_payroll_community","hr","account", 'liter_sapi'],
    "data": [   
                'security/ir.model.access.csv',
            	'views/payslip_view.xml',
                'views/payment_view.xml'
                # 'views/setoran_susu_view.xml'
             ],
    'installable': True,
    'auto_install': False,
}
