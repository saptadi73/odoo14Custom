#!/usr/bin/env python3
import xmlrpc.client

URL = "http://localhost:8070"
DB = "kanjabung_MRP"
USER = "admin"
PWD = "admin"

TARGETS = [
    "grt_crm_business_category",
    "grt_sales_business_category",
    "grt_purchase_business_category",
    "grt_expense_business_category",
    "grt_inventory_business_category",
]

common = xmlrpc.client.ServerProxy("%s/xmlrpc/2/common" % URL)
uid = common.authenticate(DB, USER, PWD, {})
if not uid:
    raise SystemExit("AUTH_FAILED")

models = xmlrpc.client.ServerProxy("%s/xmlrpc/2/object" % URL)
mods = models.execute_kw(
    DB,
    uid,
    PWD,
    "ir.module.module",
    "search_read",
    [[("name", "in", TARGETS)]],
    {"fields": ["name", "state", "installed_version"], "order": "name asc"},
)

for m in mods:
    print("%s | %s | %s" % (m.get("name"), m.get("state"), m.get("installed_version")))
