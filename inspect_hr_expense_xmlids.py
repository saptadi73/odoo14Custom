#!/usr/bin/env python3
import xmlrpc.client

URL = "http://localhost:8070"
DB = "kanjabung_MRP"
USER = "admin"
PWD = "admin"

common = xmlrpc.client.ServerProxy("%s/xmlrpc/2/common" % URL)
uid = common.authenticate(DB, USER, PWD, {})
models = xmlrpc.client.ServerProxy("%s/xmlrpc/2/object" % URL)

imd = models.execute_kw(
    DB, uid, PWD,
    "ir.model.data", "search_read",
    [[("module", "=", "hr_expense"), ("model", "=", "ir.ui.view")]],
    {"fields": ["name", "res_id"], "limit": 500, "order": "name asc"},
)

print("hr_expense view xmlids:")
for row in imd:
    print("hr_expense.%s -> %s" % (row.get("name"), row.get("res_id")))
