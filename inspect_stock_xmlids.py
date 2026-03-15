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
    [[("module", "=", "stock"), ("model", "=", "ir.ui.view")]],
    {"fields": ["name", "res_id"], "limit": 1200},
)

for row in imd:
    name = row.get("name")
    if "move" in name or "picking" in name or "filter" in name:
        print("stock.%s -> %s" % (name, row.get("res_id")))
