from odoo import SUPERUSER_ID, api


SEED_CATEGORIES = [
    ("crm_business_category_01", "Business Category 1", "BC01"),
    ("crm_business_category_02", "Business Category 2", "BC02"),
    ("crm_business_category_03", "Business Category 3", "BC03"),
    ("crm_business_category_04", "Business Category 4", "BC04"),
    ("crm_business_category_05", "Business Category 5", "BC05"),
    ("crm_business_category_06", "Business Category 6", "BC06"),
]


SHARED_XMLID_NAMES = [
    "view_crm_business_category_tree",
    "view_crm_business_category_form",
    "action_crm_business_category",
    "view_res_users_business_category_tree",
    "view_res_users_business_category_form",
    "action_res_users_business_category_access",
    "action_sync_team_business_category_access_server",
    "menu_crm_business_category",
    "menu_res_users_business_category_access",
]


def _get_xmlid_map(env, module, names):
    data = env["ir.model.data"].sudo().search(
        [("module", "=", module), ("name", "in", names)]
    )
    return {record.name: record for record in data}


def _ensure_xmlid(env, module, name, model, res_id, noupdate=True):
    xmlid = env["ir.model.data"].sudo().search(
        [("module", "=", module), ("name", "=", name)], limit=1
    )
    values = {
        "module": module,
        "name": name,
        "model": model,
        "res_id": res_id,
        "noupdate": noupdate,
    }
    if xmlid:
        xmlid.write(values)
    else:
        env["ir.model.data"].sudo().create(values)


def _cleanup_duplicate_record(env, xmlid_record, keep_res_id):
    if not xmlid_record or xmlid_record.res_id == keep_res_id:
        return

    model = env[xmlid_record.model].sudo()
    duplicate = model.browse(xmlid_record.res_id)
    if duplicate.exists():
        duplicate.unlink()


def _migrate_seed_categories(env):
    company = env.ref("base.main_company")
    category_model = env["crm.business.category"].sudo()
    base_xmlids = _get_xmlid_map(
        env, "grt_business_category_base", [name for name, _, _ in SEED_CATEGORIES]
    )
    old_xmlids = _get_xmlid_map(
        env, "grt_crm_business_category", [name for name, _, _ in SEED_CATEGORIES]
    )

    for xmlid_name, category_name, code in SEED_CATEGORIES:
        chosen = False
        old_xmlid = old_xmlids.get(xmlid_name)
        base_xmlid = base_xmlids.get(xmlid_name)

        if old_xmlid:
            chosen = category_model.browse(old_xmlid.res_id)
        elif base_xmlid:
            chosen = category_model.browse(base_xmlid.res_id)
        else:
            chosen = category_model.search(
                [("company_id", "=", company.id), "|", ("code", "=", code), ("name", "=", category_name)],
                limit=1,
            )

        if not chosen:
            chosen = category_model.create(
                {
                    "name": category_name,
                    "code": code,
                    "company_id": company.id,
                }
            )

        if not chosen.code:
            chosen.code = code

        _ensure_xmlid(
            env, "grt_business_category_base", xmlid_name, "crm.business.category", chosen.id
        )
        _ensure_xmlid(
            env, "grt_crm_business_category", xmlid_name, "crm.business.category", chosen.id
        )

        _cleanup_duplicate_record(env, base_xmlid, chosen.id)


def _pick_default_category(categories):
    active_categories = categories.filtered("active")
    coded = active_categories.filtered(lambda category: category.code == "BC01")
    return (coded[:1] or active_categories[:1] or categories[:1])


def _sync_seed_categories_to_all_companies(env):
    category_model = env["crm.business.category"].sudo()
    companies = env["res.company"].sudo().search([])
    stats = {"companies": len(companies), "created": 0, "existing": 0}

    for company in companies:
        for _, category_name, code in SEED_CATEGORIES:
            category = category_model.search(
                [
                    ("company_id", "=", company.id),
                    "|",
                    ("code", "=", code),
                    ("name", "=", category_name),
                ],
                limit=1,
            )
            if category:
                if not category.code:
                    category.code = code
                stats["existing"] += 1
                continue

            category_model.create(
                {
                    "name": category_name,
                    "code": code,
                    "company_id": company.id,
                }
            )
            stats["created"] += 1
    return stats


def _cleanup_safe_legacy_business_category_data(env):
    cr = env.cr
    company_model = env["res.company"].sudo()
    category_model = env["crm.business.category"].sudo()
    stats = {
        "crm_team_updated": 0,
        "crm_team_unresolved": 0,
        "stock_warehouse_updated": 0,
        "stock_warehouse_unresolved": 0,
        "product_template_updated": 0,
        "product_template_unresolved": 0,
    }

    categories_by_company = {}
    for company in company_model.search([]):
        categories_by_company[company.id] = _pick_default_category(
            category_model.search([("company_id", "=", company.id)], order="active desc, code, id")
        )

    for company in company_model.search([]):
        default_category = categories_by_company.get(company.id)
        if not default_category:
            continue

        cr.execute(
            """
            UPDATE crm_team
               SET business_category_id = %s
             WHERE business_category_id IS NULL
               AND company_id = %s
            """,
            [default_category.id, company.id],
        )
        stats["crm_team_updated"] += cr.rowcount

        cr.execute(
            """
            UPDATE stock_warehouse
               SET business_category_id = %s
             WHERE business_category_id IS NULL
               AND company_id = %s
            """,
            [default_category.id, company.id],
        )
        stats["stock_warehouse_updated"] += cr.rowcount

        cr.execute(
            """
            UPDATE product_template
               SET business_category_id = %s
             WHERE business_category_id IS NULL
               AND company_id = %s
            """,
            [default_category.id, company.id],
        )
        stats["product_template_updated"] += cr.rowcount

    cr.execute("SELECT COUNT(*) FROM crm_team WHERE business_category_id IS NULL")
    stats["crm_team_unresolved"] = cr.fetchone()[0]

    cr.execute("SELECT COUNT(*) FROM stock_warehouse WHERE business_category_id IS NULL")
    stats["stock_warehouse_unresolved"] = cr.fetchone()[0]

    cr.execute(
        """
        SELECT COUNT(*)
          FROM product_template
         WHERE business_category_id IS NULL
           AND active IS TRUE
        """
    )
    stats["product_template_unresolved"] = cr.fetchone()[0]
    return stats


def _migrate_shared_xmlids(env):
    base_xmlids = _get_xmlid_map(env, "grt_business_category_base", SHARED_XMLID_NAMES)
    old_xmlids = _get_xmlid_map(env, "grt_crm_business_category", SHARED_XMLID_NAMES)

    for xmlid_name in SHARED_XMLID_NAMES:
        old_xmlid = old_xmlids.get(xmlid_name)
        base_xmlid = base_xmlids.get(xmlid_name)

        canonical = old_xmlid or base_xmlid
        if not canonical:
            continue

        _ensure_xmlid(
            env,
            "grt_business_category_base",
            xmlid_name,
            canonical.model,
            canonical.res_id,
            noupdate=canonical.noupdate,
        )
        _ensure_xmlid(
            env,
            "grt_crm_business_category",
            xmlid_name,
            canonical.model,
            canonical.res_id,
            noupdate=canonical.noupdate,
        )

        if old_xmlid and base_xmlid and old_xmlid.res_id != base_xmlid.res_id:
            _cleanup_duplicate_record(env, base_xmlid, old_xmlid.res_id)


def _cleanup_obsolete_crm_security(env):
    obsolete_names = [
        "access_crm_business_category_user",
        "access_crm_business_category_manager",
        "crm_business_category_rule_user",
        "crm_business_category_rule_manager",
    ]
    obsolete = env["ir.model.data"].sudo().search(
        [("module", "=", "grt_crm_business_category"), ("name", "in", obsolete_names)]
    )
    for record in obsolete:
        target = env[record.model].sudo().browse(record.res_id)
        if target.exists():
            target.unlink()
    obsolete.unlink()


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _migrate_seed_categories(env)
    _sync_seed_categories_to_all_companies(env)
    _migrate_shared_xmlids(env)
    _cleanup_obsolete_crm_security(env)
    _cleanup_safe_legacy_business_category_data(env)
