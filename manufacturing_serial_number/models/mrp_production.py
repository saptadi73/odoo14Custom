# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    serial_ids = fields.One2many(
        'manufacturing.serial',
        'mrp_production_id',
        string='Serial Numbers',
        readonly=True
    )
    
    serial_count = fields.Integer(
        string='Serial Count',
        compute='_compute_serial_count'
    )
    
    auto_generate_serial = fields.Boolean(
        string='Auto Generate Serial',
        default=True,
        help='Automatically generate serial numbers when production is done'
    )

    @api.depends('serial_ids')
    def _compute_serial_count(self):
        for record in self:
            record.serial_count = len(record.serial_ids)

    def button_mark_done(self):
        """Override to generate serial numbers when marking as done"""
        res = super(MrpProduction, self).button_mark_done()
        
        for production in self:
            if production.auto_generate_serial and production.product_id:
                # Check if product needs serial tracking
                if production.product_id.tracking in ['serial', 'lot'] or \
                   production.product_id.use_manufacturing_serial:
                    production._generate_manufacturing_serials()
        
        return res

    def _generate_manufacturing_serials(self):
        """Generate serial numbers for finished products"""
        self.ensure_one()
        
        SerialObj = self.env['manufacturing.serial']
        
        # Calculate quantity to generate (based on product qty_done)
        qty_to_generate = int(self.product_qty)
        
        if qty_to_generate <= 0:
            return
        
        # Limit to reasonable number
        if qty_to_generate > 1000:
            raise UserError(_('Cannot generate more than 1000 serial numbers at once. Please reduce quantity.'))
        
        serial_list = []
        for i in range(qty_to_generate):
            serial_vals = {
                'product_id': self.product_id.id,
                'mrp_production_id': self.id,
                'production_date': fields.Datetime.now(),
                'state': 'produced',
                'company_id': self.company_id.id,
            }
            serial_list.append(serial_vals)
        
        # Batch create serials
        if serial_list:
            SerialObj.create(serial_list)
            
        return True

    def action_view_serial_numbers(self):
        """Open serial numbers view"""
        self.ensure_one()
        return {
            'name': _('Serial Numbers'),
            'type': 'ir.actions.act_window',
            'res_model': 'manufacturing.serial',
            'view_mode': 'tree,form',
            'domain': [('mrp_production_id', '=', self.id)],
            'context': {
                'default_mrp_production_id': self.id,
                'default_product_id': self.product_id.id,
            },
        }

    def action_generate_serials_manual(self):
        """Manual action to generate serials"""
        for production in self:
            if production.state in ['done', 'progress']:
                production._generate_manufacturing_serials()
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('Serial numbers generated successfully.'),
                'type': 'success',
                'sticky': False,
            }
        }
