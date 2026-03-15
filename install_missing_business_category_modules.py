#!/usr/bin/env python3
import xmlrpc.client

URL = "http://localhost:8070"
DB = "kanjabung_MRP"
USER = "admin"
PWD = "admin"

TARGETS = [
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
    {"fields": ["id", "name", "state"], "order": "name asc"},
)

if not mods:
    raise SystemExit("NO_TARGET_MODULES_FOUND")

for mod in mods:
    print("BEFORE | %s | %s" % (mod["name"], mod["state"]))

install_ids = [m["id"] for m in mods if m["state"] != "installed"]

if install_ids:
    print("Installing modules IDs:", install_ids)
    models.execute_kw(
        DB,
        uid,
        PWD,
        "ir.module.module",
        "button_immediate_install",
        [install_ids],
    )
    print("Install command completed")
else:
    print("No modules to install")

mods_after = models.execute_kw(
    DB,
    uid,
    PWD,
    "ir.module.module",
    "search_read",
    [[("name", "in", TARGETS)]],
    {"fields": ["name", "state", "installed_version"], "order": "name asc"},
)

for mod in mods_after:
    print("AFTER  | %s | %s | %s" % (mod["name"], mod["state"], mod.get("installed_version")))
