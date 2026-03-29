from odoo import models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def reconcile(self):
        invoice_moves = self.mapped("move_id").filtered(
            lambda move: move.move_type == "out_invoice" and move.state == "posted"
        )
        result = super().reconcile()
        paid_orders = invoice_moves.filtered(lambda move: move.payment_state == "paid").mapped(
            "invoice_line_ids.sale_line_ids.order_id"
        )
        if paid_orders:
            self.env["kpi.sales.trigger.rule"].sudo().process_paid_orders(paid_orders)
        return result
