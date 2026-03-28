from odoo import api, fields, models, _


class AssetDepreciationConfirmationWizard(models.TransientModel):
    _inherit = "asset.depreciation.confirmation.wizard"
    _description = "asset.depreciation.confirmation.wizard"

    category_id = fields.Many2one('account.asset.category', string='Category')

    def asset_compute(self):
        res = super(AssetDepreciationConfirmationWizard, self).asset_compute()
        domain_filter = []
        if self.category_id:
            domain_filter.append(('category_id', '=', self.category_id.id))
        res['domain'] = str(domain_filter)
        return res
