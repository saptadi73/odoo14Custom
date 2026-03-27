# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Employee Additional Kanjabung',
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'category': 'Generic Modules/Human Resources',
    'author': 'FHMA, '
              'Odoo Community Association (OCA)',
    'depends': ['hr'],
    'data': [
        'views/hr_employee_views.xml',
#        'views/payroll_journal_views.xml',
#        'views/ptkp_views.xml',
#        'views/account_move_views.xml',
#        'views/pph21_rate_views.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
}
