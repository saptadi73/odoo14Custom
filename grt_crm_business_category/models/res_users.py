from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ResUsers(models.Model):
    _inherit = "res.users"

    allowed_business_category_ids = fields.Many2many(
        "crm.business.category",
        "res_users_crm_business_category_rel",
        "user_id",
        "business_category_id",
        string="Allowed Business Categories",
        help="Users can only access CRM data in these business categories.",
    )

    default_business_category_id = fields.Many2one(
        "crm.business.category",
        string="Default Business Category",
        domain="[('id', 'in', allowed_business_category_ids)]",
        help="Default category for new records.",
    )

    active_business_category_id = fields.Many2one(
        "crm.business.category",
        string="Active Business Category",
        domain="[('id', 'in', allowed_business_category_ids)]",
        help="Current user context category, similar to active company.",
    )

    @api.onchange("allowed_business_category_ids")
    def _onchange_allowed_business_category_ids(self):
        for user in self:
            if user.default_business_category_id not in user.allowed_business_category_ids:
                user.default_business_category_id = False
            if user.active_business_category_id not in user.allowed_business_category_ids:
                user.active_business_category_id = False
            if user.allowed_business_category_ids and not user.default_business_category_id:
                user.default_business_category_id = user.allowed_business_category_ids[0]
            if user.allowed_business_category_ids and not user.active_business_category_id:
                user.active_business_category_id = user.default_business_category_id

    @api.constrains(
        "allowed_business_category_ids",
        "default_business_category_id",
        "active_business_category_id",
    )
    def _check_business_category_consistency(self):
        for user in self:
            if user.default_business_category_id and user.default_business_category_id not in user.allowed_business_category_ids:
                raise ValidationError(
                    _("Default Business Category must be included in Allowed Business Categories.")
                )
            if user.active_business_category_id and user.active_business_category_id not in user.allowed_business_category_ids:
                raise ValidationError(
                    _("Active Business Category must be included in Allowed Business Categories.")
                )
