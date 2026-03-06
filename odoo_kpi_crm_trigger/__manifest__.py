# -*- coding: utf-8 -*-
{
    "name": "Odoo KPI CRM Trigger",
    "summary": "CRM event rules to send KPI values by assignment",
    "version": "14.0.1.0.0",
    "category": "Sales/CRM",
    "author": "Custom",
    "depends": ["crm", "mail", "hr", "odoo_kpi", "grt_crm_business_category"],
    "data": [
        "security/ir.model.access.csv",
        "views/kpi_crm_trigger_rule_views.xml",
    ],
    "installable": True,
    "application": False,
    "license": "LGPL-3",
}
