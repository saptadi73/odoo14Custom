from odoo import SUPERUSER_ID, api

from . import controllers
from . import models


def _cleanup_legacy_sales_team_menu(env):
    menu = env.ref("grt_sales_business_category.menu_sale_team_from_sales", raise_if_not_found=False)
    action = env.ref("grt_sales_business_category.action_sales_team_from_sales", raise_if_not_found=False)

    if menu:
        menu.unlink()
    if action and action.exists():
        action.unlink()


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _cleanup_legacy_sales_team_menu(env)
    env["res.partner"]._backfill_missing_customer_qr_ref()
