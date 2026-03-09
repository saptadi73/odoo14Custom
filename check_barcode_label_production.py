#!/usr/bin/env python3
"""
Diagnose barcode label printing problems for garazd_product_label in Odoo 14.

What this script checks:
1. Odoo connectivity and authentication
2. Module installation state and version
3. Critical report URL parameters used by PDF engine
4. Report action and template presence in database
5. Direct barcode endpoint availability via HTTP

Usage example:
python check_barcode_label_production.py --url http://127.0.0.1:8070 --db mydb --user admin --password admin
"""

import argparse
import sys
import urllib.error
import urllib.request
import xmlrpc.client


def _ok(msg):
    print(f"[OK] {msg}")


def _warn(msg):
    print(f"[WARN] {msg}")


def _err(msg):
    print(f"[ERROR] {msg}")


def _fetch_url(url, timeout=10):
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.status, resp.headers.get("Content-Type", "")


def main():
    parser = argparse.ArgumentParser(description="Check production barcode label readiness")
    parser.add_argument("--url", required=True, help="Odoo base URL, e.g. http://127.0.0.1:8070")
    parser.add_argument("--db", required=True, help="Database name")
    parser.add_argument("--user", required=True, help="Odoo username")
    parser.add_argument("--password", required=True, help="Odoo password")
    parser.add_argument(
        "--test-value",
        default="BATCH20260309",
        help="Sample barcode value for /report/barcode check",
    )
    args = parser.parse_args()

    base = args.url.rstrip("/")
    common = xmlrpc.client.ServerProxy(f"{base}/xmlrpc/2/common")
    models = xmlrpc.client.ServerProxy(f"{base}/xmlrpc/2/object")

    print("=" * 72)
    print("DIAGNOSIS: BARCODE LABEL PRODUCTION")
    print("=" * 72)

    try:
        version = common.version()
        _ok(f"Connected to Odoo: {version.get('server_version', 'unknown')}")
    except Exception as exc:
        _err(f"Cannot connect to Odoo XML-RPC at {base}: {exc}")
        return 2

    uid = common.authenticate(args.db, args.user, args.password, {})
    if not uid:
        _err("Authentication failed. Check --db/--user/--password.")
        return 2
    _ok(f"Authenticated as UID {uid}")

    module_ids = models.execute_kw(
        args.db,
        uid,
        args.password,
        "ir.module.module",
        "search",
        [[("name", "=", "garazd_product_label")]],
        {"limit": 1},
    )
    if not module_ids:
        _err("Module garazd_product_label not found in database.")
        return 2

    module_data = models.execute_kw(
        args.db,
        uid,
        args.password,
        "ir.module.module",
        "read",
        [module_ids],
        {"fields": ["name", "state", "installed_version", "latest_version"]},
    )[0]
    _ok(
        "Module state: {state}, installed_version: {iv}, latest_version: {lv}".format(
            state=module_data.get("state"),
            iv=module_data.get("installed_version") or "-",
            lv=module_data.get("latest_version") or "-",
        )
    )
    if module_data.get("state") != "installed":
        _warn("Module is not installed in production database.")

    params = ["report.url", "web.base.url", "web.base.url.freeze"]
    print("\nConfig parameters:")
    for key in params:
        value = models.execute_kw(
            args.db,
            uid,
            args.password,
            "ir.config_parameter",
            "get_param",
            [key],
        )
        if value:
            _ok(f"{key} = {value}")
        else:
            _warn(f"{key} is empty")

    report_names = [
        "garazd_product_label.report_product_label_57x35_template",
        "garazd_product_label.report_product_label_50x38_template",
        "garazd_product_label.report_product_label_a4_90x50_template",
        "garazd_product_label.report_product_label_thermal_4x6_template",
    ]
    print("\nReport actions:")
    for report_name in report_names:
        report_ids = models.execute_kw(
            args.db,
            uid,
            args.password,
            "ir.actions.report",
            "search",
            [[("report_name", "=", report_name)]],
            {"limit": 1},
        )
        if report_ids:
            _ok(f"Found report action: {report_name}")
        else:
            _warn(f"Missing report action: {report_name}")

    barcode_url = (
        f"{base}/report/barcode/?type=Code128&value={args.test_value}"
        "&width=600&height=100&humanreadable=0"
    )
    print("\nHTTP barcode test:")
    try:
        status, content_type = _fetch_url(barcode_url)
        if status == 200:
            _ok(f"Barcode endpoint returns 200 ({content_type})")
        else:
            _warn(f"Barcode endpoint returns status {status} ({content_type})")
    except urllib.error.HTTPError as exc:
        _err(f"Barcode endpoint HTTP error: {exc.code} {exc.reason}")
    except Exception as exc:
        _err(f"Barcode endpoint failed: {exc}")

    print("\nSuggested next actions if print still fails in production:")
    print("1. Upgrade module: Apps -> Custom Product Labels -> Upgrade")
    print("2. Ensure report.url points to local Odoo URL reachable by server")
    print("3. Test /report/barcode URL directly from production host")
    print("4. Reprint and inspect odoo log for wkhtmltopdf/report errors")

    return 0


if __name__ == "__main__":
    sys.exit(main())
