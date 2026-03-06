from odoo import models


class AccountPayment(models.Model):
    _inherit = "account.payment"

    def action_post(self):
        result = super().action_post()
        receivable_lines = self.mapped("move_id.line_ids").filtered(lambda line: line.account_id.internal_type == "receivable")
        partials = receivable_lines.mapped("matched_debit_ids") | receivable_lines.mapped("matched_credit_ids")
        counterpart_lines = (partials.mapped("debit_move_id") | partials.mapped("credit_move_id")) - receivable_lines
        invoice_moves = counterpart_lines.mapped("move_id").filtered(
            lambda move: move.move_type == "out_invoice" and move.state == "posted" and move.payment_state == "paid"
        )
        orders = invoice_moves.mapped("invoice_line_ids.sale_line_ids.order_id")
        if orders:
            self.env["kpi.sales.trigger.rule"].sudo().process_paid_orders(orders)
        return result
