from odoo import models


class AccountPaymentRegister(models.TransientModel):
    _inherit = "account.payment.register"

    def _create_payment_vals_from_wizard(self):
        vals = super()._create_payment_vals_from_wizard()
        moves = self.line_ids.mapped("move_id")
        categories = moves.mapped("business_category_id")
        analytics = moves.mapped("analytic_account_id")
        if len(categories) == 1:
            vals["business_category_id"] = categories.id
        if len(analytics) == 1:
            vals["analytic_account_id"] = analytics.id
        return vals
