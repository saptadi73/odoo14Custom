# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import random
import string


class ManufacturingSerial(models.Model):
    _name = 'manufacturing.serial'
    _description = 'Manufacturing Serial Number'
    _order = 'serial_number desc'
    _rec_name = 'serial_number'

    serial_number = fields.Char(
        string='Serial Number',
        required=True,
        copy=False,
        readonly=True,
        index=True,
        default='New'
    )
    
    product_id = fields.Many2one(
        'product.product',
        string='Product',
        required=True,
        ondelete='restrict'
    )
    
    mrp_production_id = fields.Many2one(
        'mrp.production',
        string='Manufacturing Order',
        ondelete='cascade'
    )
    
    production_date = fields.Datetime(
        string='Production Date',
        default=fields.Datetime.now,
        required=True
    )
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('produced', 'Produced'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled')
    ], string='State', default='draft', required=True)
    
    notes = fields.Text(string='Notes')
    
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company
    )
    
    lot_id = fields.Many2one(
        'stock.production.lot',
        string='Lot/Serial Number (Stock)',
        help='Link to stock lot if available'
    )
    
    _sql_constraints = [
        ('serial_number_unique', 'unique(serial_number, company_id)', 
         'Serial number must be unique per company!')
    ]

    @api.model
    def create(self, vals):
        if vals.get('serial_number', 'New') == 'New':
            vals['serial_number'] = self._generate_serial_number(vals.get('product_id'))
        return super(ManufacturingSerial, self).create(vals)

    def _generate_serial_number(self, product_id=None):
        """Generate unique serial number"""
        prefix = 'MFG'
        
        if product_id:
            product = self.env['product.product'].browse(product_id)
            if product.default_code:
                prefix = product.default_code[:6].upper()
        
        # Generate sequential number
        sequence = self.env['ir.sequence'].next_by_code('manufacturing.serial') or '0001'
        
        # Add random suffix for extra uniqueness
        random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        
        serial_number = f"{prefix}-{sequence}-{random_suffix}"
        
        # Check if exists, regenerate if needed
        if self.search([('serial_number', '=', serial_number)], limit=1):
            return self._generate_serial_number(product_id)
        
        return serial_number

    def action_set_produced(self):
        self.write({'state': 'produced'})

    def action_set_delivered(self):
        self.write({'state': 'delivered'})

    def action_cancel(self):
        self.write({'state': 'cancelled'})

    def name_get(self):
        result = []
        for record in self:
            name = f"{record.serial_number}"
            if record.product_id:
                name = f"{record.serial_number} - {record.product_id.name}"
            result.append((record.id, name))
        return result
