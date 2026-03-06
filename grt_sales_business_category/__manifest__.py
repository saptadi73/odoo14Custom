# -*- coding: utf-8 -*-
{
    "name": "GRT Sales Business Category",
    "summary": "Business category and layered approval flow for sales orders",
    "description": """
Adds business category handling on Sales Orders using the same CRM teams/categories,
plus a two-step approval flow: Sales Team Leader then Accounting Manager.
""",
    "author": "PT Gagak Rimang Teknologi",
    "website": "https://rimang.id",
    "category": "Sales/Sales",
    "version": "14.0.1.0.0",
    "depends": [
        "sale_management",
        "sale_crm",
        "account",
        "grt_crm_business_category",
    ],
    "data": [
        "security/security.xml",
        "security/ir.rule.csv",
        "views/crm_team_views.xml",
        "views/sale_order_views.xml",
        "views/sale_team_menu_views.xml",
    ],
    "installable": True,
    "application": False,
}
