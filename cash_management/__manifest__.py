# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name' : 'Cash Management',
    'version' : '1.0',
    'summary': 'Manage your Cash and Bank',
    'description': """
TODO

old description:
Invoicing & Payments by Accounting Voucher & Receipts
=====================================================
The specific and easy-to-use Invoicing system in Odoo allows you to keep track of your accounting, even when you are not an accountant. It provides an easy way to follow up on your vendors and customers.

You could use this simplified accounting in case you work with an (external) account to keep your books, and you still want to keep track of payments.

The Invoicing system includes receipts and vouchers (an easy way to keep track of sales and purchases). It also offers you an easy method of registering payments, without having to encode complete abstracts of account.

This module manages:

* Voucher Entry

    """,
    'name':'Cash Management',
    'category': 'Accounting',
    'sequence': 20,
    'depends' : ['account', 'base', 'basic_hms'],
    'demo' : [],
    'data' : [
        'security/account_voucher_security.xml',
        'security/ir.model.access.csv',
        # 'views/res_partner_views.xml',
        'views/account_journal_view.xml',
        'views/account_voucher_views.xml',
        'views/inherit_attribute_account_voucher.xml',
        'data/account_voucher_data.xml',
    ],
    'auto_install': False,
    'installable': True,
}
