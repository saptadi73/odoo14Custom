# -*- coding: utf-8 -*-
import datetime
import logging
from odoo import api, models, _
_logger = logging.getLogger(__name__)

class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'

    def check_report_vals(self, orderlines):
        product_dict = {}
        for lines in orderlines:
            for ln in lines:
                for new in lines[ln]:
                    if new.order_id.state in ['sale', 'done']:
                        cost_price = new.purchase_price * new.product_uom_qty if new.purchase_price else new.product_id.standard_price * new.product_uom_qty
                        amount_wo_tax = new.price_subtotal
                        if new.price_unit not in product_dict:
                            product_dict.update({
                                new.price_unit:
                                    {
                                        'category': new.product_id.categ_id,
                                        'qty': new.product_uom_qty,
                                        'uom': new.product_id.uom_id,
                                        'unit_price': new.price_unit,
                                        'taxes': new.price_tax if new.price_tax else 0.0,
                                        'amt_wo_tax': float("{:.2f}".format(amount_wo_tax)),
                                        'cost_price': cost_price,
                                        'gross_pnl': float("{:.2f}".format(amount_wo_tax - cost_price)),
                                    }
                                })
                        else:
                            product_dict[new.price_unit].update({
                                'qty': product_dict[new.price_unit]['qty'] + new.product_uom_qty,
                                'amt_wo_tax': float("{:.2f}".format(product_dict[new.price_unit]['amt_wo_tax'] + amount_wo_tax)),
                                'taxes': product_dict[new.price_unit]['taxes'] + new.price_tax,
                                'cost_price': product_dict[new.price_unit]['cost_price'] + cost_price,
                                'gross_pnl': float("{:.2f}".format(product_dict[new.price_unit]['gross_pnl'] + (amount_wo_tax - cost_price))),
                            })
        return product_dict


class ReportRender(models.AbstractModel):
    _name = 'report.sales_profit_loss_report.report_sales_profit_report'
    _description = 'Product profit Report Render'

    @api.model
    def _get_report_values(self, docids, data=None):
        # only for pdf report
        model_data = data['form']
        return self.generate_report_values(model_data)

    @api.model
    def generate_report_values(self, data):
        from_date = data['from_date']
        to_date = data['to_date']
        company = data['company']
        sale_orders = self.env['sale.order'].search([('date_order', '>=', from_date), ('date_order', '<=', to_date), ('state', 'not in', ['draft', 'cancel', 'sent']), ('company_id', '=', company[0])])
        test_dict = {}
        for order in sale_orders:
            for lines in order.order_line:
                if lines.product_id not in test_dict:
                    test_dict.update({lines.product_id:[{lines.price_unit:[lines]}]})
                else:
                    for price in test_dict[lines.product_id]:
                        if lines.price_unit not in price:
                            price.update({lines.price_unit:[lines]})
                        else:
                            price[lines.price_unit].append(lines)
        return {
            'data': data,
            'product_dict': test_dict,
            'report_date': datetime.datetime.now().strftime("%Y-%m-%d"),
        }
