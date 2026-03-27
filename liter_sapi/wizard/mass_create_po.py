from odoo import api, models, _
from odoo.exceptions import UserError


class CreatePOWizard(models.TransientModel):
    _name = 'create.po.wiz'


    def mass_create_po(self):
        if self._context.get('active_model') == 'liter.sapi':
            domain = [('id', 'in', self._context.get('active_ids', []))]
        else:
            raise UserError(_("Missing 'active_model' in context."))

        product = self.env['liter.sapi'].search(domain).filtered('product_id')
        for p in product :
            if p.qty_po != 0 :
                print ("===============liter============", p.peternak_id.id)
                p.create_po()
        return {'type': 'ir.actions.act_window_close'}

    
