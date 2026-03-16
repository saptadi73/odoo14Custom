#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Smoke test for module grt_partner_offset_reconcile (non-destructive).

Checks:
1) Authentication
2) Module existence + installed state
3) Wizard models registered
4) XMLIDs (action + menu) loaded

Usage:
  python smoke_test_partner_offset.py
  python smoke_test_partner_offset.py --url http://localhost:8070 --db kanjabung_MRP --user admin --password admin
"""

import argparse
import sys
import xmlrpc.client


def parse_args():
    parser = argparse.ArgumentParser(description="Smoke test for partner offset reconciliation module")
    parser.add_argument("--url", default="http://localhost:8070", help="Odoo base URL")
    parser.add_argument("--db", default="kanjabung_MRP", help="Odoo database name")
    parser.add_argument("--user", default="admin", help="Odoo username")
    parser.add_argument("--password", default="admin", help="Odoo password")
    parser.add_argument(
        "--module",
        default="grt_partner_offset_reconcile",
        help="Technical module name",
    )
    return parser.parse_args()


def fail(message):
    print(f"❌ {message}")
    return 1


def ok(message):
    print(f"✅ {message}")


def main():
    args = parse_args()

    common = xmlrpc.client.ServerProxy(f"{args.url}/xmlrpc/2/common")
    uid = common.authenticate(args.db, args.user, args.password, {})
    if not uid:
        return fail("Authentication failed")
    ok(f"Authenticated as {args.user} (uid={uid})")

    models = xmlrpc.client.ServerProxy(f"{args.url}/xmlrpc/2/object")

    module_data = models.execute_kw(
        args.db,
        uid,
        args.password,
        "ir.module.module",
        "search_read",
        [[("name", "=", args.module)]],
        {"fields": ["name", "state", "installed_version"], "limit": 1},
    )
    if not module_data:
        return fail(f"Module {args.module} not found")

    module = module_data[0]
    ok(f"Module found: {module['name']} (state={module['state']}, version={module.get('installed_version')})")
    if module.get("state") != "installed":
        return fail("Module exists but is not installed")

    model_names = ["grt.partner.offset.wizard", "grt.partner.offset.wizard.line"]
    model_records = models.execute_kw(
        args.db,
        uid,
        args.password,
        "ir.model",
        "search_read",
        [[("model", "in", model_names)]],
        {"fields": ["model"], "limit": 10},
    )
    found_models = {record["model"] for record in model_records}
    missing_models = [name for name in model_names if name not in found_models]
    if missing_models:
        return fail(f"Missing wizard models: {', '.join(missing_models)}")
    ok("Wizard models are registered")

    required_xmlids = ["action_partner_offset_wizard", "menu_partner_offset_wizard"]
    xmlid_data = models.execute_kw(
        args.db,
        uid,
        args.password,
        "ir.model.data",
        "search_read",
        [[("module", "=", args.module), ("name", "in", required_xmlids)]],
        {"fields": ["module", "name", "model", "res_id"], "limit": 10},
    )
    found_xmlids = {record["name"] for record in xmlid_data}
    missing_xmlids = [name for name in required_xmlids if name not in found_xmlids]
    if missing_xmlids:
        return fail(f"Missing XMLIDs: {', '.join(missing_xmlids)}")
    ok("Action and menu XMLIDs are loaded")

    print("\n🎉 Smoke test passed. Module is ready to use.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(f"❌ Unexpected error: {exc}")
        sys.exit(1)
