from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ScadaMoBulkWizard(models.TransientModel):
    _name = 'scada.mo.bulk.wizard'
    _description = 'SCADA Bulk Manufacturing Order Wizard'

    product_id = fields.Many2one(
        'product.product',
        string='Finished Product',
        required=True,
    )
    product_qty = fields.Float(
        string='Total Quantity',
        required=True,
        default=1000.0,
    )
    date_planned_start = fields.Datetime(
        string='Production Date',
        required=True,
        default=fields.Datetime.now,
    )
    bom_id = fields.Many2one(
        'mrp.bom',
        string='BoM',
        required=True,
    )
    scada_equipment_id = fields.Many2one(
        'scada.equipment',
        string='SCADA Equipment',
    )
    max_qty_per_mo = fields.Float(
        string='Max Qty per MO',
        required=True,
        default=1000.0,
    )
    total_mo_count = fields.Integer(
        string='Generated MO Count',
        compute='_compute_total_mo_count',
    )

    @api.depends('product_qty', 'max_qty_per_mo')
    def _compute_total_mo_count(self):
        for wizard in self:
            if wizard.product_qty <= 0 or wizard.max_qty_per_mo <= 0:
                wizard.total_mo_count = 0
                continue
            full_count = int(wizard.product_qty // wizard.max_qty_per_mo)
            remainder = wizard.product_qty - (full_count * wizard.max_qty_per_mo)
            wizard.total_mo_count = full_count + (1 if remainder > 0 else 0)

    @api.onchange('product_id')
    def _onchange_product_id(self):
        for wizard in self:
            if not wizard.product_id:
                wizard.bom_id = False
                continue
            bom = wizard.env['mrp.bom']._bom_find(
                product=wizard.product_id,
                company_id=wizard.env.company.id,
                bom_type='normal',
            )
            wizard.bom_id = bom

    @api.onchange('bom_id')
    def _onchange_bom_id(self):
        for wizard in self:
            if not wizard.bom_id:
                continue
            bom_product = wizard.bom_id.product_id or wizard.bom_id.product_tmpl_id.product_variant_id
            wizard.product_id = bom_product
            wizard.scada_equipment_id = wizard.bom_id.scada_equipment_id

    def action_generate_mos(self):
        self.ensure_one()

        if self.product_qty <= 0:
            raise ValidationError(_('Total Quantity must be greater than zero.'))
        if self.max_qty_per_mo <= 0:
            raise ValidationError(_('Max Qty per MO must be greater than zero.'))
        if not self._bom_matches_product(self.bom_id, self.product_id):
            raise ValidationError(_('Selected BoM does not match the selected finished product.'))

        split_quantities = self._build_split_quantities(self.product_qty, self.max_qty_per_mo)
        if not split_quantities:
            raise ValidationError(_('No Manufacturing Orders can be generated from current values.'))

        equipment = self.scada_equipment_id or self.bom_id.scada_equipment_id
        uom = self.bom_id.product_uom_id or self.product_id.uom_id
        origin_ref = _('SCADA Bulk MO %s') % fields.Datetime.now()

        vals_list = []
        for qty in split_quantities:
            vals_list.append({
                'product_id': self.product_id.id,
                'product_qty': qty,
                'product_uom_id': uom.id,
                'bom_id': self.bom_id.id,
                'date_planned_start': self.date_planned_start,
                'origin': origin_ref,
                'scada_equipment_id': equipment.id if equipment else False,
            })

        mo_records = self.env['mrp.production'].create(vals_list)

        return {
            'type': 'ir.actions.act_window',
            'name': _('Generated Manufacturing Orders'),
            'res_model': 'mrp.production',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', mo_records.ids)],
            'target': 'current',
        }

    def _build_split_quantities(self, total_qty, chunk_size):
        full_count = int(total_qty // chunk_size)
        quantities = [chunk_size] * full_count
        remainder = total_qty - (full_count * chunk_size)
        if remainder > 0:
            quantities.append(remainder)
        return quantities

    def _bom_matches_product(self, bom, product):
        if not bom or not product:
            return False
        if bom.product_id:
            return bom.product_id.id == product.id
        if bom.product_tmpl_id:
            return bom.product_tmpl_id.id == product.product_tmpl_id.id
        return False
