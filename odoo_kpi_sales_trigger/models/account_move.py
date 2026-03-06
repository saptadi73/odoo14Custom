from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    def _get_kpi_sales_payment_dates(self):
        self.ensure_one()
        receivable_lines = self.line_ids.filtered(lambda line: line.account_id.internal_type == "receivable")
        partials = receivable_lines.mapped("matched_debit_ids") | receivable_lines.mapped("matched_credit_ids")
        counterpart_lines = (partials.mapped("debit_move_id") | partials.mapped("credit_move_id")) - receivable_lines
        return [move.date for move in counterpart_lines.mapped("move_id") if move.date]

    def write(self, vals):
        previous_payment_state = {}
        if "payment_state" in vals:
            previous_payment_state = {move.id: move.payment_state for move in self}

        result = super().write(vals)

        if "payment_state" in vals:
            paid_moves = self.filtered(
                lambda move: move.move_type == "out_invoice"
                and previous_payment_state.get(move.id) != "paid"
                and move.payment_state == "paid"
            )
            orders = paid_moves.mapped("invoice_line_ids.sale_line_ids.order_id")
            if orders:
                self.env["kpi.sales.trigger.rule"].sudo().process_paid_orders(orders)
        return result
