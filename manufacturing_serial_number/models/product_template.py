# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    use_manufacturing_serial = fields.Boolean(
        string='Use Manufacturing Serial',
        default=False,
        help='Enable automatic serial number generation for manufacturing'
    )
    
    serial_count = fields.Integer(
        string='Total Serials Generated',
        compute='_compute_serial_count'
    )

    @api.depends('product_variant_ids.serial_ids')
    def _compute_serial_count(self):
        for template in self:
            serials = self.env['manufacturing.serial'].search([
                ('product_id', 'in', template.product_variant_ids.ids)
            ])
            template.serial_count = len(serials)

    def action_view_serial_numbers(self):
        """View all serial numbers for this product"""
        self.ensure_one()
        return {
            'name': 'Serial Numbers',
            'type': 'ir.actions.act_window',
            'res_model': 'manufacturing.serial',
            'view_mode': 'tree,form',
            'domain': [('product_id', 'in', self.product_variant_ids.ids)],
            'context': {'default_product_id': self.product_variant_ids[0].id if self.product_variant_ids else False},
        }


class ProductProduct(models.Model):
    _inherit = 'product.product'

    serial_ids = fields.One2many(
        'manufacturing.serial',
        'product_id',
        string='Serial Numbers'
    )
