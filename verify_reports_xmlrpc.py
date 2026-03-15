#!/usr/bin/env python3
import xmlrpc.client

URL = "http://localhost:8070"
DB = "kanjabung_MRP"
USER = "admin"
PWD = "admin"

common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
uid = common.authenticate(DB, USER, PWD, {})
if not uid:
    raise SystemExit("AUTH_FAILED")

models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")

xmlids = [
    "grt_sales_business_category.action_sale_order_business_category_report",
    "grt_purchase_business_category.action_purchase_order_business_category_report",
    "grt_expense_business_category.action_hr_expense_business_category_report",
    "grt_inventory_business_category.action_stock_picking_business_category_report",
    "grt_crm_business_category.action_crm_pipeline_business_category_report",
    "grt_crm_business_category.action_crm_activity_history_report",
    "grt_sales_business_category.menu_sale_order_business_category_report",
    "grt_purchase_business_category.menu_purchase_order_business_category_report",
    "grt_expense_business_category.menu_hr_expense_business_category_report",
    "grt_inventory_business_category.menu_stock_picking_business_category_report",
    "grt_crm_business_category.menu_crm_pipeline_business_category_report",
]

print("=== XMLID CHECK ===")
for item in xmlids:
    module, name = item.split(".", 1)
    rec = models.execute_kw(
        DB,
        uid,
        PWD,
        "ir.model.data",
        "search_read",
        [[("module", "=", module), ("name", "=", name)]],
        {"fields": ["id", "model", "res_id"], "limit": 1},
    )
    print(("FOUND" if rec else "MISSING") + ": " + item)

print("\n=== ACTION CONTEXT CHECK ===")
imd = models.execute_kw(
    DB,
    uid,
    PWD,
    "ir.model.data",
    "search_read",
    [[("module", "=", "grt_crm_business_category"), ("name", "=", "action_crm_activity_history_report")]],
    {"fields": ["res_id"], "limit": 1},
)
if imd:
    action_id = imd[0]["res_id"]
    action = models.execute_kw(
        DB,
        uid,
        PWD,
        "ir.actions.act_window",
        "read",
        [[action_id]],
        {"fields": ["name", "context"]},
    )
    print("CRM Activity action:", action[0]["name"])
    print("CRM Activity context:", action[0].get("context"))

print("\n=== DATA SAMPLE COUNT ===")
checks = [
    ("sale.order", [("business_category_id", "!=", False)]),
    ("purchase.order", [("business_category_id", "!=", False)]),
    ("hr.expense", [("business_category_id", "!=", False)]),
    ("stock.picking", [("business_category_id", "!=", False)]),
    ("crm.lead", [("type", "=", "opportunity"), ("business_category_id", "!=", False)]),
    ("crm.activity.history", [("business_category_id", "!=", False)]),
]
for model, domain in checks:
    try:
        count = models.execute_kw(DB, uid, PWD, model, "search_count", [domain])
        print(f"{model}: {count}")
    except Exception as exc:
        print(f"{model}: ERROR {exc}")
