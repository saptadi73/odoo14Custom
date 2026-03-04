from odoo import fields, models


class CrmTeam(models.Model):
    _inherit = "crm.team"

    def _default_business_category_id(self):
        cr = self.env.cr
        cr.execute(
            """
            SELECT 1
            FROM information_schema.columns
            WHERE table_name = 'res_users' AND column_name = 'active_business_category_id'
            """
        )
        has_active = bool(cr.fetchone())
        cr.execute(
            """
            SELECT 1
            FROM information_schema.columns
            WHERE table_name = 'res_users' AND column_name = 'default_business_category_id'
            """
        )
        has_default = bool(cr.fetchone())

        if not has_active and not has_default:
            return False

        user = self.env.user
        if has_active and user.active_business_category_id:
            return user.active_business_category_id.id
        if has_default and user.default_business_category_id:
            return user.default_business_category_id.id
        return False

    business_category_id = fields.Many2one(
        "crm.business.category",
        string="Business Category",
        default=_default_business_category_id,
        required=True,
        ondelete="restrict",
    )
