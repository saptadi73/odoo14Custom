#!/usr/bin/env python3
import xmlrpc.client

URL = "http://localhost:8070"
DB = "kanjabung_MRP"
USER = "admin"
PWD = "admin"

common = xmlrpc.client.ServerProxy("%s/xmlrpc/2/common" % URL)
uid = common.authenticate(DB, USER, PWD, {})
if not uid:
    raise SystemExit("AUTH_FAILED")
models = xmlrpc.client.ServerProxy("%s/xmlrpc/2/object" % URL)

view_ids = models.execute_kw(
    DB, uid, PWD,
    "ir.ui.view", "search_read",
    [[("model", "=", "hr.expense")]],
    {"fields": ["id", "name", "key"], "limit": 200, "order": "id asc"},
)

print("hr.expense view candidates:")
for v in view_ids:
    print(v.get("id"), "|", v.get("key"), "|", v.get("name"))
