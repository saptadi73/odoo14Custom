# -*- coding: utf-8 -*-
{
    "name": "GRT Purchase Business Category",
    "summary": "Business category segregation and purchase teams for purchasing",
    "description": """
Adds business category handling to Purchase Orders with dedicated Purchase Teams,
record rules per business category, and automatic analytic account propagation
for purchasing transactions.
""",
    "author": "PT Gagak Rimang Teknologi",
    "website": "https://rimang.id",
    "category": "Purchases",
    "version": "14.0.1.0.0",
    "depends": [
        "purchase",
        "account",
        "grt_crm_business_category",
    ],
    "data": [
        "security/ir.model.access.csv",
        "security/ir.rule.csv",
        "views/crm_business_category_views.xml",
        "views/purchase_team_views.xml",
        "views/purchase_order_views.xml",
        "views/purchase_report_business_category_views.xml",
        "views/purchase_menu_views.xml",
    ],
    "installable": True,
    "application": False,
}
