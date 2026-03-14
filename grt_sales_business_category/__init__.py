from odoo import SUPERUSER_ID, api

from . import controllers
from . import models


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env["res.partner"]._backfill_missing_customer_qr_ref()
