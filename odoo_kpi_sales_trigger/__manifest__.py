# -*- coding: utf-8 -*-
{
    "name": "Odoo KPI Sales Trigger",
    "summary": "Sales event rules to send KPI values by assignment",
    "version": "14.0.1.0.2",
    "category": "Sales/Sales",
    "author": "Custom",
    "depends": ["sale_management", "account", "hr", "odoo_kpi", "grt_sales_business_category"],
    "data": [
        "security/ir.model.access.csv",
        "views/kpi_sales_trigger_rule_views.xml",
    ],
    "installable": True,
    "application": False,
    "license": "LGPL-3",
}
