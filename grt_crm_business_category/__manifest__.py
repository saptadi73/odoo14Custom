# -*- coding: utf-8 -*-
{
    "name": "GRT CRM Business Category",
    "summary": "Business category selection before pipeline in CRM",
    "description": """
Adds Business Category in CRM and binds pipeline/team choices by category.
This enables different staging flow per business category through team pipelines.
""",
    "author": "PT Gagak Rimang Teknologi",
    "website": "https://rimang.id",
    "category": "Sales/CRM",
    "version": "14.0.2.10.1",
    "depends": ["crm"],
    "data": [
        "security/ir.model.access.csv",
        "security/ir.rule.csv",
        "data/crm_business_category_data.xml",
        "views/assets.xml",
        "views/crm_activity_history_views.xml",
        "views/crm_business_category_views.xml",
        "views/crm_lead_views.xml",
        "views/crm_menu_views.xml",
        "views/crm_stage_views.xml",
        "views/crm_team_views.xml",
        "views/crm_team_business_category_views.xml",
        "views/mail_activity_views.xml",
        "views/res_users_business_category_views.xml",
    ],
    "installable": True,
    "application": False,
}
