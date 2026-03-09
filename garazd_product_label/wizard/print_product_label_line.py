# Copyright © 2018 Garazd Creation (<https://garazd.biz>)
# @author: Yurii Razumovskyi (<support@garazd.biz>)
# @author: Iryna Razumovska (<support@garazd.biz>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.html).

from urllib.parse import quote

from odoo import api, fields, models
from reportlab.graphics.barcode import createBarcodeDrawing


class PrintProductLabelLine(models.TransientModel):
    _name = "print.product.label.line"
    _description = 'Line with a Product Label Data'
    _order = 'sequence'

    sequence = fields.Integer(default=900)
    selected = fields.Boolean(string='Print', default=True)
    wizard_id = fields.Many2one(comodel_name='print.product.label')  # Not make required
    product_id = fields.Many2one(comodel_name='product.product', required=True)
    lot_id = fields.Many2one(
        comodel_name='stock.production.lot',
        string='Lot/Serial Number',
    )
    barcode = fields.Char(compute='_compute_barcode')
    qty_initial = fields.Integer(string='Initial Qty', default=1)
    qty = fields.Integer(string='Label Qty', default=1)
    company_id = fields.Many2one(
        comodel_name='res.company',
        compute='_compute_company_id',
    )

    @api.depends('wizard_id.company_id')
    def _compute_company_id(self):
        for label in self:
            label.company_id = \
                label.wizard_id.company_id and label.wizard_id.company_id.id \
                or self.env.user.company_id.id

    @api.depends('product_id', 'lot_id')
    def _compute_barcode(self):
        for label in self:
            label.barcode = label.lot_id.name or label.product_id.barcode

    def _get_barcode_type(self):
        self.ensure_one()
        barcode = (self.barcode or '').strip()
        if self.lot_id:
            return 'Code128'
        if barcode.isdigit() and len(barcode) == 13:
            return 'EAN13'
        if barcode.isdigit() and len(barcode) == 8:
            return 'EAN8'
        return 'Code128'

    def get_barcode_url(self, width=600, height=100):
        self.ensure_one()
        if not self.barcode:
            return False
        barcode_value = quote(self.barcode, safe='')
        humanreadable = 1 if self.wizard_id.humanreadable else 0
        # Default Odoo barcode route with trailing slash is broadly compatible.
        return '/report/barcode/?type=%s&value=%s&width=%s&height=%s&humanreadable=%s' % (
            self._get_barcode_type(),
            barcode_value,
            width,
            height,
            humanreadable,
        )

    def get_barcode_url_alt(self, width=600, height=100):
        self.ensure_one()
        if not self.barcode:
            return False
        barcode_value = quote(self.barcode, safe='')
        humanreadable = 1 if self.wizard_id.humanreadable else 0
        # Fallback variant without trailing slash for strict proxies.
        return '/report/barcode?type=%s&value=%s&width=%s&height=%s&humanreadable=%s' % (
            self._get_barcode_type(),
            barcode_value,
            width,
            height,
            humanreadable,
        )



    def action_plus_qty(self):
        self.ensure_one()
        if not self.qty:
            self.update({'selected': True})
        self.update({'qty': self.qty + 1})

    def action_minus_qty(self):
        self.ensure_one()
        if self.qty > 0:
            self.update({'qty': self.qty - 1})
            if not self.qty:
                self.update({'selected': False})
