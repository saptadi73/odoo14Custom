from datetime import date, datetime, time
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _, SUPERUSER_ID
from odoo.exceptions import UserError, ValidationError

class SetoranSusu(models.Model):
    _inherit = 'liter.sapi'


    def create_po(self):
        purchase_order_obj = self.env['purchase.order']
        purchase_order_line_obj = self.env['purchase.order.line']
        for liter in self:
            vals = {
                        'partner_id' : liter.peternak_id.partner_id.id,
                        'date_order' : datetime.now(),
                        'state' : 'draft'                             
                    }
            purchase_order = purchase_order_obj.create(vals)
            po_line_vals = {
                'product_id' : liter.product_id.id,
                'product_qty': liter.setoran,
                'name' : liter.product_id.name,
                'price_unit' : liter.harga_satuan,
                'date_planned' : datetime.now(),
                'product_uom' : liter.product_id.uom_po_id.id,
                'order_id' : purchase_order.id,
            }
            
            purchase_order_line = purchase_order_line_obj.create(po_line_vals)
