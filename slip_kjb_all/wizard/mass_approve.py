from odoo import models, api, _
from odoo.exceptions import UserError


class MassAprrove(models.TransientModel):
    _name = "mass.approve"
    _description = "Mass Approve"

    @api.multi
    def mass_approve(self):
        context = dict(self._context or {})
        payslip = self.env['hr.payslip'].browse(context.get('active_ids'))
        mass_approve = self.env['hr.payslip']
        for pay in payslip:
            if pay.state == 'done':
                mass_approve += pay
        if not mass_approve:
            raise UserError(_("Cannot Finish a payslip state not Done....!!!"))
        mass_approve.finish()
        return {'type': 'ir.actions.act_window_close'}
