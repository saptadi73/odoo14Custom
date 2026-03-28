# -*- coding: utf-8 -*-
{
    "name": "slip_kjb_all",
    "version": "2.01",
    "author": "OSK (Si Fahmi)",
    "license": "LGPL-3",
    "category": "Payroll",
    "website": "",
    "depends": ["hr_payroll_community","hr","hr_attendance"],
    "data": [
             'security/ir.model.access.csv',
             'data/security.xml',
             'views/payslip_view.xml',
             'views/employee_view.xml',
             'views/attandance_view.xml',

             
             ],
    'installable': True,
    'auto_install': False,
}