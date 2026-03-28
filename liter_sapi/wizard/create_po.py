# from odoo import models, fields, api, _
# from datetime import datetime
#
# class WizardCreatePo(models.TransientModel):
#     _name = 'wizard.create.po'
#     _description = 'Wizard Create PO'
#
#     @api.model
#     def default_get(self, fields):
#         res = super(WizardCreatePo, self).default_get(fields)
#         active_ids = self._context.get('active_ids')
#         if active_ids:
#             res['liter_sapi_ids'] = active_ids
#         return res
#
#     liter_sapi_ids = fields.Many2many('liter.sapi', string='Setoran Liter Sapi')
#
#     def create_po(self):
#         purchase_order_obj = self.env['purchase.order']
#         purchase_order_line_obj = self.env['purchase.order.line']
#
#         for liter in self.liter_sapi_ids:
#             product = self.env['product.product'].search([('product_tmpl_id', '=', liter.product_id.id)])
#
#             # Set is_po to True for relevant setoran_line_ids
#             liter.setoran_line_ids.write({'is_po': True})
#
#             # Set is_po to True for relevant setoran_line_date_ids
#             liter.setoran_line_date_ids.write({'is_po': True})
#
#             vals = {
#                 'partner_id': liter.peternak_id.partner_id.id,
#                 'date_order': datetime.now(),
#                 'state': 'draft',
#                 'setoran_id': liter.id
#             }
#
#             purchase_order = purchase_order_obj.create(vals)
#
#             po_line_vals = {
#                 'product_id': product.id,
#                 'product_qty': liter.qty_po,
#                 'name': product.name,
#                 'price_unit': liter.harga_satuan,
#                 'date_planned': datetime.now(),
#                 'product_uom': product.uom_po_id.id,
#                 'order_id': purchase_order.id,
#             }
#
#             purchase_order_line_obj.create(po_line_vals)
#
#         return {'type': 'ir.actions.act_window_close'}