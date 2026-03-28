# -*- coding: utf-8 -*-
{
    "name": "GRT MRP Overhead Costing",
    "summary": "Monthly overhead absorption, expense reconciliation, and variance for manufacturing",
    "description": """
Adds monthly manufacturing overhead periods to:
- store electricity and labor overhead
- calculate overhead tariff per kg / hour / MO
- allocate applied overhead to manufacturing orders
- reconcile applied overhead against actual expense postings
- compute variance
- generate journal adjustment entries
""",
    "author": "PT Gagak Rimang Teknologi",
    "website": "https://rimang.id",
    "category": "Manufacturing",
    "version": "14.0.1.0.0",
    "depends": [
        "mail",
        "mrp",
        "account",
        "stock_account",
        "hr_expense",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/sequence.xml",
        "views/mrp_overhead_type_views.xml",
        "views/mrp_overhead_period_views.xml",
        "views/mrp_production_views.xml",
        "views/product_bom_overhead_factor_views.xml",
        "views/hr_expense_views.xml",
        "views/mrp_overhead_menu_views.xml",
        "views/mrp_overhead_documentation_views.xml",
    ],
    "installable": True,
    "application": False,
    "license": "LGPL-3",
}
