from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _get_kpi_sales_customer_invoices(self):
        self.ensure_one()
        return self.invoice_ids.filtered(lambda inv: inv.move_type == "out_invoice" and inv.state == "posted")

    def _is_kpi_sales_fully_paid(self):
        self.ensure_one()
        invoices = self._get_kpi_sales_customer_invoices()
        return bool(invoices) and all(invoice.payment_state == "paid" for invoice in invoices)

    def _get_kpi_sales_payment_completion_date(self):
        self.ensure_one()
        invoices = self._get_kpi_sales_customer_invoices().filtered(lambda inv: inv.payment_state == "paid")
        payment_dates = []
        for invoice in invoices:
            payment_dates.extend(invoice._get_kpi_sales_payment_dates())
        payment_dates = [date_value for date_value in payment_dates if date_value]
        return max(payment_dates) if payment_dates else False

    def _get_kpi_sales_due_date(self):
        self.ensure_one()
        invoices = self._get_kpi_sales_customer_invoices()
        due_dates = [invoice.invoice_date_due or invoice.invoice_date for invoice in invoices if invoice.invoice_date_due or invoice.invoice_date]
        return max(due_dates) if due_dates else False

    def _get_kpi_sales_late_days(self, payment_date=False):
        self.ensure_one()
        payment_date = payment_date or self._get_kpi_sales_payment_completion_date()
        due_date = self._get_kpi_sales_due_date()
        if not payment_date or not due_date or payment_date <= due_date:
            return 0
        return (fields.Date.to_date(payment_date) - fields.Date.to_date(due_date)).days
