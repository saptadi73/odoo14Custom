# -*- coding: utf-8 -*-
{
    "name": "Odoo KPI System",
    "summary": "Dynamic KPI management for employee, department, and team",
    "version": "14.0.1.0.0",
    "category": "Human Resources",
    "author": "Custom",
    "depends": ["base", "mail", "hr", "crm"],
    "data": [
        "security/kpi_security.xml",
        "security/ir.model.access.csv",
        "views/kpi_department_views.xml",
        "views/kpi_definition_views.xml",
        "views/kpi_target_views.xml",
        "views/kpi_period_views.xml",
        "views/kpi_assignment_views.xml",
        "views/kpi_value_views.xml",
        "views/kpi_score_views.xml",
        "views/kpi_team_views.xml",
        "views/kpi_evidence_views.xml",
        "views/kpi_menu.xml",
        "data/kpi_cron.xml",
    ],
    "installable": True,
    "application": True,
    "license": "LGPL-3",
}

