from odoo import api, fields, models, _

class ResCompany(models.Model):
    _inherit = "res.company"

    gain_account_id = fields.Many2one('account.account', domain="[('deprecated', '=', False), ('company_id', '=', id)]", help="Account used to write the journal item in case of gain while selling an asset")
    loss_account_id = fields.Many2one('account.account', domain="[('deprecated', '=', False), ('company_id', '=', id)]", help="Account used to write the journal item in case of loss while selling an asset")
    asset_income_account_id = fields.Many2one('account.account',string="Asset Income Account", domain="[('deprecated', '=', False), ('company_id', '=', id)]", help="Account used to write the journal item in case of loss while selling an asset")


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.onchange('is_asset')
    def _onchange_set_asset_income_account(self):
        for rec in self:
            if rec.is_asset == True:
                rec.property_account_income_id = self.env.company.asset_income_account_id.id
            # else:
