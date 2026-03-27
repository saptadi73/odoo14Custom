from odoo import models, fields, api

class StockPickikngInheritHms(models.Model):
    _inherit = 'stock.picking'

    tipe_id = fields.Many2one('master.tipe.sapi', 'Tipe Sapi')
    sapi_ids = fields.Many2many('sapi', string='Sapi')
    eartag_id = fields.Char('Eartag ID', compute='_compute_pakan_eartag_id')
    product_pakan_id = fields.Many2one(
        'product.product', 'Product', readonly=False)
    qty = fields.Float('Qty')
    price = fields.Float('Total Price', compute='_compute_tot_price')
    standard_price = fields.Float('Cost', related='product_pakan_id.standard_price')
    jum_sapi = fields.Integer('Jumlah Sapi', compute='_compute_total_sapi', store=True)

    @api.depends('qty', 'standard_price')
    def _compute_tot_price(self):
        for cip in self:
            if cip.standard_price != 0:
                cip.price = cip.standard_price * cip.qty
            else:
                cip.price = 0.0

    @api.depends('sapi_ids')
    def _compute_total_sapi(self):
        for cip in self:
            cip.jum_sapi = len(cip.sapi_ids)

    @api.onchange('tipe_id')
    def _onchange_pakan_tipe_id(self):
        # Clear existing sapi_ids
        self.sapi_ids = [(5, 0, 0)]

        # Fill sapi_ids based on tipe_id
        if self.tipe_id:
            # Add your logic here to fetch sapi_ids based on the selected tipe_id
            # For example:
            sapi_ids = self.env['sapi'].search([('tipe_id', '=', self.tipe_id.id), ('is_rearing', '=', True)])

            # Set the sapi_ids field with the fetched sapi_ids
            self.sapi_ids = [(6, 0, sapi_ids.ids)]

    @api.depends('sapi_ids')
    def _compute_pakan_eartag_id(self):
        for record in self:
            eartag_ids = [str(sapi.eartag_id) for sapi in record.sapi_ids if
                          sapi.eartag_id]  # konversi ke string dan hindari None atau False
            eartag_str = ', '.join(eartag_ids)
            record.eartag_id = eartag_str

class StockPickikngSapiInheritHms(models.Model):
    _inherit = 'stock.move'

    tipe_id = fields.Many2one('master.tipe.sapi', 'Tipe Sapi')
    sapi_ids = fields.Many2many('sapi', string='Sapi')
    eartag_id = fields.Char('Eartag ID', compute='_compute_eartag_id')
    price = fields.Float('Price')
    tot_price = fields.Float('Total', compute='_compute_tot_price')
    product_id = fields.Many2one(
        'product.product', 'Product',
        check_company=True,
        domain="[('type', 'in', ['product', 'consu']), '|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        index=True, required=True,
        states={'done': [('readonly', True)]})
    product_uom_qty = fields.Float(
        'Demand',
        digits='Product Unit of Measure',
        default=0.0, required=True, states={'done': [('readonly', True)]},
        help="This is the quantity of products from an inventory "
             "point of view. For moves in the state 'done', this is the "
             "quantity of products that were actually moved. For other "
             "moves, this is the quantity of product that is planned to "
             "be moved. Lowering this quantity does not generate a "
             "backorder. Changing this quantity on assigned moves affects "
             "the product reservation, and should be done with care.")
    inventory_qty = fields.Float('On Hand Qty', compute='_compute_inventory_qty', store=True)
    is_pakan = fields.Boolean('Is Pakan?')

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.price = self.product_id.standard_price

    @api.depends('price', 'product_uom_qty')
    def _compute_tot_price(self):
        for move in self:
            move.tot_price = move.price * move.product_uom_qty

    @api.depends('product_id', 'product_id.stock_quant_ids')
    def _compute_inventory_qty(self):
        for move in self:
            if move.product_id:
                quants = move.product_id.stock_quant_ids.filtered(lambda quant: quant.location_id.usage == 'internal')
                move.inventory_qty = sum(quants.mapped('quantity'))
            else:
                move.inventory_qty = 0.0

    @api.onchange('tipe_id')
    def _onchange_tipe_id(self):
        # Clear existing sapi_ids
        self.sapi_ids = [(5, 0, 0)]

        # Fill sapi_ids based on tipe_id
        if self.tipe_id:
            # Add your logic here to fetch sapi_ids based on the selected tipe_id
            # For example:
            sapi_ids = self.env['sapi'].search([('tipe_id', '=', self.tipe_id.id), ('is_rearing', '=', True)])

            # Set the sapi_ids field with the fetched sapi_ids
            self.sapi_ids = [(6, 0, sapi_ids.ids)]

    @api.depends('sapi_ids')
    def _compute_eartag_id(self):
        for record in self:
            eartag_ids = [str(sapi.eartag_id) for sapi in record.sapi_ids if
                          sapi.eartag_id]  # konversi ke string dan hindari None atau False
            eartag_str = ', '.join(eartag_ids)
            record.eartag_id = eartag_str
