# -*- coding: utf-8 -*-
# Copyright 2017 Elico Corp (www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Payslip Lines BI report",
    "version": "14.0.1.0.0",
    "summary": "Analyze your payroll with the Payslip Lines BI report",
    "category": "Generic Modules/Human Resources",
    "website": "https://www.elico-corp.com/",
    "author": "Elico Corp, "
              "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "depends": [
        "hr_payroll_community",
    ],
    'data': [
        'views/hr_payroll_report_menu.xml',
        'views/hr_payslip_line_view.xml',
    ],
}
