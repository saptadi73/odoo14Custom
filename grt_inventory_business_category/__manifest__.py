# -*- coding: utf-8 -*-
{
    "name": "GRT Inventory Business Category",
    "summary": "Business category segregation and inventory teams for stock operations",
    "description": """
Adds business category handling to Inventory with dedicated Inventory Teams,
warehouse segregation, record rules per business category, and analytic account
propagation for stock valuation journal entries.
""",
    "author": "PT Gagak Rimang Teknologi",
    "website": "https://rimang.id",
    "category": "Inventory",
    "version": "14.0.1.1.1",
    "depends": [
        "stock_account",
        "sale_stock",
        "purchase_stock",
        "grt_business_category_base",
        "grt_sales_business_category",
        "grt_purchase_business_category",
    ],
    "data": [
        "security/ir.model.access.csv",
        "security/ir.rule.csv",
        "views/stock_team_views.xml",
        "views/stock_warehouse_views.xml",
        "views/stock_picking_views.xml",
        "views/product_views.xml",
        "views/inventory_report_business_category_views.xml",
        "views/stock_menu_views.xml",
    ],
    "installable": True,
    "application": False,
}
