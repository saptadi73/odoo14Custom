# -*- coding: utf-8 -*-
{
    "name": "Odoo KPI Customer Behavior Trigger",
    "summary": "Customer behavior event rules to send KPI values by assignment",
    "version": "14.0.1.0.0",
    "category": "Sales/Sales",
    "author": "Custom",
    "depends": ["sale_management", "hr", "odoo_kpi", "grt_sales_business_category"],
    "data": [
        "security/ir.model.access.csv",
        "views/kpi_customer_behavior_trigger_rule_views.xml",
    ],
    "installable": True,
    "application": False,
    "license": "LGPL-3",
}
