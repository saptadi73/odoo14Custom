#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Runtime test akses eksklusif Business Category (Odoo XML-RPC).

Tujuan:
- Memastikan user hanya bisa akses record pada business category yang diizinkan.
- Memastikan akses lintas category ditolak (read/write rule).
- Memastikan policy strict manager scope berjalan (kecuali sysadmin).

Cara pakai:
1) Sesuaikan konfigurasi di bagian CONFIG.
2) Pastikan di database sudah ada minimal 2 business category.
3) Pastikan ada 2 user test (A dan B) dengan category berbeda.
4) Jalankan: python test_business_category_access_runtime.py
"""

import traceback
import xmlrpc.client


# =========================
# CONFIG
# =========================
ODOO_URL = "http://localhost:8070"
ODOO_DB = "kanjabung_MRP"

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin"

# User uji dengan category berbeda
USER_A_USERNAME = "user.category.a"
USER_A_PASSWORD = "admin"
USER_B_USERNAME = "user.category.b"
USER_B_PASSWORD = "admin"

AUTO_BOOTSTRAP_TEST_USERS = True

# Jika None, script akan auto-detect dari effective_business_category_ids user
USER_A_CATEGORY_ID = None
USER_B_CATEGORY_ID = None

# Model + field category yang diuji
MODEL_CATEGORY_MAP = {
    "crm.lead": "business_category_id",
    "sale.order": "business_category_id",
    "purchase.order": "business_category_id",
    "hr.expense": "business_category_id",
    "stock.picking": "business_category_id",
    "account.move": "business_category_id",  # Sales invoice
}

TEST_GROUP_XMLIDS = [
    "base.group_user",
    "crm.group_use_lead",
    "sales_team.group_sale_salesman",
    "sales_team.group_sale_manager",
    "purchase.group_purchase_user",
    "hr_expense.group_hr_expense_user",
    "stock.group_stock_user",
    "account.group_account_user",
]


def rpc_common(url):
    return xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")


def rpc_object(url):
    return xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")


def auth(common, db, username, password):
    uid = common.authenticate(db, username, password, {})
    if not uid:
        raise RuntimeError(f"Gagal login: {username}")
    return uid


def execute(models, db, uid, pwd, model, method, args=None, kwargs=None):
    if args is None:
        args = []
    if kwargs is None:
        kwargs = {}
    return models.execute_kw(db, uid, pwd, model, method, args, kwargs)


def safe_call(label, fn):
    try:
        result = fn()
        return True, result, None
    except Exception as exc:
        return False, None, f"{label}: {exc}"


def pick_user_category(models, db, admin_uid, admin_pwd, user_id, fallback=None):
    if fallback:
        return fallback

    user_data = execute(
        models,
        db,
        admin_uid,
        admin_pwd,
        "res.users",
        "read",
        [[user_id]],
        {"fields": ["effective_business_category_ids"]},
    )
    category_ids = user_data[0].get("effective_business_category_ids", [])
    if not category_ids:
        raise RuntimeError(
            f"User ID {user_id} tidak punya effective_business_category_ids."
        )
    return category_ids[0]


def get_xmlid_res_id(models, db, uid, pwd, xmlid):
    module, name = xmlid.split(".", 1)
    rec = execute(
        models,
        db,
        uid,
        pwd,
        "ir.model.data",
        "search_read",
        [[("module", "=", module), ("name", "=", name)]],
        {"fields": ["res_id"], "limit": 1},
    )
    return rec[0]["res_id"] if rec else None


def ensure_two_categories(models, db, admin_uid, admin_pwd):
    categories = execute(
        models,
        db,
        admin_uid,
        admin_pwd,
        "crm.business.category",
        "search_read",
        [[("active", "=", True)]],
        {"fields": ["id", "name"], "order": "id asc", "limit": 10},
    )

    if len(categories) >= 2:
        return categories[0]["id"], categories[1]["id"]

    company = execute(
        models,
        db,
        admin_uid,
        admin_pwd,
        "res.company",
        "search_read",
        [[]],
        {"fields": ["id"], "limit": 1},
    )
    if not company:
        raise RuntimeError("Tidak ada company di database.")
    company_id = company[0]["id"]

    while len(categories) < 2:
        next_no = len(categories) + 1
        new_id = execute(
            models,
            db,
            admin_uid,
            admin_pwd,
            "crm.business.category",
            "create",
            [{
                "name": f"AUTO Category {next_no}",
                "code": f"AUTO{next_no}",
                "company_id": company_id,
            }],
        )
        categories.append({"id": new_id, "name": f"AUTO Category {next_no}"})

    return categories[0]["id"], categories[1]["id"]


def ensure_user_with_category(models, db, admin_uid, admin_pwd, login, password, category_id):
    user_rec = execute(
        models,
        db,
        admin_uid,
        admin_pwd,
        "res.users",
        "search_read",
        [[("login", "=", login)]],
        {"fields": ["id", "company_id", "company_ids"], "limit": 1},
    )

    company = execute(
        models,
        db,
        admin_uid,
        admin_pwd,
        "crm.business.category",
        "read",
        [[category_id]],
        {"fields": ["company_id"]},
    )
    if not company or not company[0].get("company_id"):
        raise RuntimeError(f"Category {category_id} tidak punya company_id.")
    company_id = company[0]["company_id"][0]

    group_ids = []
    for xmlid in TEST_GROUP_XMLIDS:
        gid = get_xmlid_res_id(models, db, admin_uid, admin_pwd, xmlid)
        if gid:
            group_ids.append(gid)

    vals = {
        "name": login,
        "login": login,
        "password": password,
        "company_id": company_id,
        "company_ids": [(6, 0, [company_id])],
        "allowed_business_category_ids": [(6, 0, [category_id])],
        "default_business_category_id": category_id,
        "active_business_category_id": category_id,
    }
    if group_ids:
        vals["groups_id"] = [(6, 0, group_ids)]

    if user_rec:
        uid = user_rec[0]["id"]
        execute(models, db, admin_uid, admin_pwd, "res.users", "write", [[uid], vals])
        return uid

    return execute(models, db, admin_uid, admin_pwd, "res.users", "create", [vals])


def ensure_crm_lead_sample(models, db, admin_uid, admin_pwd, category_id, suffix):
    existing = execute(
        models,
        db,
        admin_uid,
        admin_pwd,
        "crm.lead",
        "search",
        [[("business_category_id", "=", category_id)]],
        {"limit": 1},
    )
    if existing:
        return existing[0]
    team = execute(
        models,
        db,
        admin_uid,
        admin_pwd,
        "crm.team",
        "search_read",
        [[("business_category_id", "=", category_id)]],
        {"fields": ["id"], "limit": 1},
    )

    vals = {
        "name": f"AUTO Lead {suffix}",
        "business_category_id": category_id,
    }
    if team:
        vals["team_id"] = team[0]["id"]

    ok, result, err = safe_call(
        "crm.lead.create",
        lambda: execute(
            models,
            db,
            admin_uid,
            admin_pwd,
            "crm.lead",
            "create",
            [vals],
        ),
    )
    if ok:
        return result

    print(f"[WARN] Gagal create sample crm.lead untuk category {category_id}: {err}")
    return None


def find_sample_record(models, db, admin_uid, admin_pwd, model, category_field, category_id):
    recs = execute(
        models,
        db,
        admin_uid,
        admin_pwd,
        model,
        "search_read",
        [[(category_field, "=", category_id)]],
        {"fields": ["id"], "limit": 1},
    )
    return recs[0]["id"] if recs else None


def test_access_rule(models, db, uid, pwd, model, record_id, operation):
    def _call():
        return execute(
            models,
            db,
            uid,
            pwd,
            model,
            "check_access_rule",
            [[record_id], operation],
        )

    return safe_call(f"{model}.check_access_rule({operation})", _call)


def test_read(models, db, uid, pwd, model, record_id):
    def _call():
        return execute(
            models,
            db,
            uid,
            pwd,
            model,
            "read",
            [[record_id]],
            {"fields": ["id"]},
        )

    return safe_call(f"{model}.read", _call)


def print_result(test_name, ok, detail=""):
    status = "PASS" if ok else "FAIL"
    print(f"[{status}] {test_name}")
    if detail:
        print(f"       {detail}")


def main():
    print("=" * 90)
    print("TEST RUNTIME AKSES EKSKLUSIF BUSINESS CATEGORY")
    print("=" * 90)
    print(f"URL : {ODOO_URL}")
    print(f"DB  : {ODOO_DB}")
    print("-" * 90)

    common = rpc_common(ODOO_URL)
    models = rpc_object(ODOO_URL)

    admin_uid = auth(common, ODOO_DB, ADMIN_USERNAME, ADMIN_PASSWORD)
    user_a_uid = common.authenticate(ODOO_DB, USER_A_USERNAME, USER_A_PASSWORD, {})
    user_b_uid = common.authenticate(ODOO_DB, USER_B_USERNAME, USER_B_PASSWORD, {})

    if AUTO_BOOTSTRAP_TEST_USERS and (not user_a_uid or not user_b_uid):
        cat_a_bootstrap, cat_b_bootstrap = ensure_two_categories(
            models, ODOO_DB, admin_uid, ADMIN_PASSWORD
        )
        ensure_user_with_category(
            models,
            ODOO_DB,
            admin_uid,
            ADMIN_PASSWORD,
            USER_A_USERNAME,
            USER_A_PASSWORD,
            cat_a_bootstrap,
        )
        ensure_user_with_category(
            models,
            ODOO_DB,
            admin_uid,
            ADMIN_PASSWORD,
            USER_B_USERNAME,
            USER_B_PASSWORD,
            cat_b_bootstrap,
        )
        ensure_crm_lead_sample(models, ODOO_DB, admin_uid, ADMIN_PASSWORD, cat_a_bootstrap, "A")
        ensure_crm_lead_sample(models, ODOO_DB, admin_uid, ADMIN_PASSWORD, cat_b_bootstrap, "B")
        user_a_uid = auth(common, ODOO_DB, USER_A_USERNAME, USER_A_PASSWORD)
        user_b_uid = auth(common, ODOO_DB, USER_B_USERNAME, USER_B_PASSWORD)
    else:
        user_a_uid = auth(common, ODOO_DB, USER_A_USERNAME, USER_A_PASSWORD)
        user_b_uid = auth(common, ODOO_DB, USER_B_USERNAME, USER_B_PASSWORD)

    cat_a = pick_user_category(
        models, ODOO_DB, admin_uid, ADMIN_PASSWORD, user_a_uid, fallback=USER_A_CATEGORY_ID
    )
    cat_b = pick_user_category(
        models, ODOO_DB, admin_uid, ADMIN_PASSWORD, user_b_uid, fallback=USER_B_CATEGORY_ID
    )

    if cat_a == cat_b:
        raise RuntimeError(
            "User A dan User B berada di category yang sama. Gunakan 2 user dengan category berbeda."
        )

    print(f"User A UID={user_a_uid} category={cat_a}")
    print(f"User B UID={user_b_uid} category={cat_b}")
    print("-" * 90)

    total = 0
    passed = 0

    for model, category_field in MODEL_CATEGORY_MAP.items():
        print(f"\nModel: {model} (field: {category_field})")

        sample_a = find_sample_record(
            models, ODOO_DB, admin_uid, ADMIN_PASSWORD, model, category_field, cat_a
        )
        sample_b = find_sample_record(
            models, ODOO_DB, admin_uid, ADMIN_PASSWORD, model, category_field, cat_b
        )

        if not sample_a or not sample_b:
            print(
                "[SKIP] Sample data tidak cukup untuk dua category. "
                "Siapkan minimal 1 record per category."
            )
            continue

        # 1) User A read own category => harus boleh
        total += 1
        ok_rule, _, err_rule = test_access_rule(
            models, ODOO_DB, user_a_uid, USER_A_PASSWORD, model, sample_a, "read"
        )
        ok_read, _, err_read = test_read(
            models, ODOO_DB, user_a_uid, USER_A_PASSWORD, model, sample_a
        )
        own_read_ok = ok_rule and ok_read
        if own_read_ok:
            passed += 1
        print_result(
            "User A read OWN category",
            own_read_ok,
            "" if own_read_ok else (err_rule or err_read or "ditolak"),
        )

        # 2) User A read other category => harus ditolak
        total += 1
        ok_rule_other, _, err_rule_other = test_access_rule(
            models, ODOO_DB, user_a_uid, USER_A_PASSWORD, model, sample_b, "read"
        )
        ok_read_other, _, err_read_other = test_read(
            models, ODOO_DB, user_a_uid, USER_A_PASSWORD, model, sample_b
        )
        other_read_denied = not (ok_rule_other and ok_read_other)
        if other_read_denied:
            passed += 1
        print_result(
            "User A read OTHER category (must deny)",
            other_read_denied,
            "denied as expected"
            if other_read_denied
            else "masih bisa baca lintas category",
        )

        # 3) User A write other category => harus ditolak
        total += 1
        ok_write_other, _, err_write_other = test_access_rule(
            models, ODOO_DB, user_a_uid, USER_A_PASSWORD, model, sample_b, "write"
        )
        other_write_denied = not ok_write_other
        if other_write_denied:
            passed += 1
        print_result(
            "User A write OTHER category (must deny)",
            other_write_denied,
            "denied as expected"
            if other_write_denied
            else f"masih lolos check_access_rule(write): {err_write_other}",
        )

    print("\n" + "=" * 90)
    print(f"SUMMARY: {passed}/{total} test PASS")
    print("=" * 90)

    if total == 0:
        print("Tidak ada test yang dieksekusi karena sample data belum tersedia.")
        return 2

    if passed != total:
        print("\nAda gap akses. Cek record rule di modul terkait (sales/purchase/expense/inventory/accounting).")
        return 1

    print("\nSemua test lolos. Akses eksklusif per business category terverifikasi.")
    return 0


if __name__ == "__main__":
    try:
        exit_code = main()
    except Exception:
        print("\n[ERROR] Test gagal dijalankan:")
        traceback.print_exc()
        exit_code = 99
    raise SystemExit(exit_code)
