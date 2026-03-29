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
    _migrate_shared_xmlids(env)
    _cleanup_obsolete_crm_security(env)
