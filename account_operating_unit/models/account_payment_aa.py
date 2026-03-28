from odoo import api, fields, models


class account_payment_aa(models.Model):
    _inherit = "account.payment"

    # @api.depends("journal_id")
    # def _compute_operating_unit_id(self):
    #     for payment in self:
    #         if payment.journal_id:
    #             payment.operating_unit_id = payment.journal_id.operating_unit_id
    #
    # operating_unit_id = fields.Many2one(
    #     comodel_name="operating.unit",
    #     domain="[('user_ids', '=', uid)]",
    #     compute="_compute_operating_unit_id",
    #     store=True,
    # )

    def _prepare_move_line_default_aa_vals(self, write_off_line_vals=None):
        res = super()._prepare_move_line_default_aa_vals(write_off_line_vals)
        for line in res:
            line["analytic_account_id"] = self.analytic_account_id.id
        invoices = self.env["account.move"].browse(self._context.get("active_ids"))
        invoices_ou = invoices.analytic_account_id
        if invoices and len(invoices_ou) == 1 and invoices_ou != self.analytic_account_id:
            destination_account_id = self.destination_account_id.id
            for line in res:
                if line["account_id"] == destination_account_id:
                    line["analytic_account_id"] = invoices_ou.id
        return res