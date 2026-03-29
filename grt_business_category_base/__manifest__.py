# -*- coding: utf-8 -*-
{
    "name": "GRT Business Category Base",
    "summary": "Shared business category master for cross-module references",
    "description": """
Central business category master module.
This module provides the shared business category model, user access context,
and reusable mixins so CRM, Sales, Purchase, Expense, and Inventory can all
reference the same category definitions.
""",
    "author": "PT Gagak Rimang Teknologi",
    "website": "https://rimang.id",
    "category": "Tools",
    "version": "14.0.1.2.0",
    "depends": ["base", "analytic"],
    "post_init_hook": "post_init_hook",
    "data": [
        "security/ir.model.access.csv",
        "security/ir.rule.csv",
        "views/crm_business_category_views.xml",
        "views/res_users_business_category_views.xml"
    ],
    "installable": True,
    "application": False
}
