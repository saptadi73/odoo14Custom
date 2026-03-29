# -*- coding: utf-8 -*-
{
    "name": "GRT Expense Business Category",
    "summary": "Business category segregation and expense teams for expenses",
    "description": """
Adds business category handling to Expenses with dedicated Expense Teams,
record rules per business category, and automatic analytic account propagation
for expense transactions and accounting entries.
""",
    "author": "PT Gagak Rimang Teknologi",
    "website": "https://rimang.id",
    "category": "Human Resources/Expenses",
    "version": "14.0.1.1.0",
    "depends": [
        "hr_expense",
        "account",
        "grt_business_category_base",
    ],
    "data": [
        "security/ir.model.access.csv",
        "security/ir.rule.csv",
        "views/expense_team_views.xml",
        "views/hr_expense_views.xml",
        "views/expense_report_business_category_views.xml",
        "views/expense_menu_views.xml",
    ],
    "installable": True,
    "application": False,
}
