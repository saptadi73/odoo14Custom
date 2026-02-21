# -*- coding: utf-8 -*-
{
    "name": "GRT CRM Business Category",
    "summary": "Business category selection before pipeline in CRM",
    "description": """
Adds Business Category in CRM and binds pipeline/team choices by category.
This enables different staging flow per business category through team pipelines.
""",
    "author": "GRT",
    "website": "https://www.rimang.id",
    "category": "Sales/CRM",
    "version": "14.0.1.0.0",
    "depends": ["crm"],
    "data": [
        "security/ir.model.access.csv",
        "views/crm_business_category_views.xml",
        "views/crm_team_views.xml",
        "views/crm_lead_views.xml",
    ],
    "installable": True,
    "application": False,
}

