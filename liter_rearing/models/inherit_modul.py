from odoo import models, fields, api

class InheritProduk(models.Model):
    _inherit = "product.template"

    is_cip = fields.Boolean('CIP')
    is_rearing = fields.Boolean('Rearing')
    is_liter = fields.Boolean('Liter')

class InheritProdoctCip(models.Model):
    _inherit = 'product.template'

    category_id = fields.Many2one('type.cip', 'CIP Category')

class AccountMoveLineCip(models.Model):
    _inherit = "account.move.line"

    category_id = fields.Many2one('type.cip', 'CIP Category')
    is_rearing = fields.Boolean('Rearing', related='account_id.is_rearing')
    tipe_id = fields.Many2one('master.tipe.sapi', 'Tipe Sapi')
    sapi_id = fields.Many2one('sapi', 'Sapi')
    eartag_id = fields.Char('Eartag ID')


    @api.onchange('eartag_id')
    def _onchange_eartag_id(self):
        if self.eartag_id:
            sapi = self.env['sapi'].search([('eartag_id', '=', self.eartag_id)], limit=1)
            for line in self :
                line.sapi_id = sapi.id
                line.tipe_id = sapi.tipe_id.id
                line.category_id = sapi.category_cip_id.id


class AssetCip(models.Model):
    _inherit = "account.asset.asset"

    eartag_id = fields.Char('Eartag ID')
    sapi_id = fields.Many2one('sapi', 'Sapi')

class AccountCip(models.Model):
    _inherit = "account.account"

    is_rearing = fields.Boolean('Rearing')

class AccountJournalCip(models.Model):
    _inherit = "account.journal"

    is_rearing = fields.Boolean('Rearing')
    is_default_pedet = fields.Boolean('Default Pedet')
    is_default_dara = fields.Boolean('Default Dara')
    is_default_induk = fields.Boolean('Default Induk')
    default_account = fields.Many2one('account.account', 'Default Account')

class InheritTipeSapiCip(models.Model):
    _inherit = "type.cip"

    tipe_id = fields.Many2one('master.tipe.sapi', 'Tipe Sapi')

class InheritSapiCip(models.Model):
    _inherit = "cip"

    tipe_ids = fields.Many2many('master.tipe.sapi', string='Tipe ID')
    sapi_ids = fields.Many2many('sapi', string='Sapi', domain="[('tipe_id', 'in', tipe_ids)]")
    journal_id = fields.Many2one('account.journal', 'Journal Induk',
                                 default=lambda self: self._get_default_journal('is_default_induk'))
    journal_id_pedet = fields.Many2one('account.journal', 'Journal Pedet',
                                       default=lambda self: self._get_default_journal('is_default_pedet'))
    journal_id_dara = fields.Many2one('account.journal', 'Journal Dara',
                                      default=lambda self: self._get_default_journal('is_default_dara'))
    category_cip_ids = fields.Many2many('type.cip', string='Category CIP')

    def _get_default_journal(self, field_name):
        default_journal = self.env['account.journal'].search([(field_name, '=', True)], limit=1)
        return default_journal.id if default_journal else False

    @api.onchange('tipe_ids')
    def _onchange_tipe_ids(self):
        if self.tipe_ids:
            sapi_records = self.env['sapi'].search([('tipe_id', 'in', self.tipe_ids.ids), ('is_rearing', '=', True)])
            self.sapi_ids = [(6, 0, sapi_records.ids)]
        else:
            # Hapus semua sapi_ids jika tipe_ids dihapus
            self.sapi_ids = [(5, 0, 0)]

class InheritSapiCipLine(models.Model):
    _inherit = "cip.hpp.line"

    tipe_id = fields.Many2one('master.tipe.sapi', 'Tipe Sapi')

class InheritSapiHpp(models.Model):
    _inherit = "sapi"

    list_hpp_ids = fields.One2many('cip.hpp.line', 'sapi_id', 'List HPP')
    list_vb_ids = fields.One2many('account.move.line', 'sapi_id', 'List VB')
    is_asset = fields.Boolean('Asset', readonly=True)
    total_cip_sapi = fields.Float(string='Nilai Perolehan Sapi', compute='_compute_total_cip_sapi', store=True, digits=(1, 0))

    @api.depends('list_hpp_ids.amount', 'list_vb_ids.price_unit')
    def _compute_total_cip_sapi(self):
        for record in self:
            total_cip_sapi = 0.0
            for hpp_line in record.list_hpp_ids:
                total_cip_sapi += hpp_line.amount
            for vb_line in record.list_vb_ids:
                total_cip_sapi += vb_line.price_unit
            record.total_cip_sapi = total_cip_sapi

class InheritListCip(models.Model):
    _inherit = "cip.to.asset"

    list_hpp_ids = fields.One2many('cip.hpp.line', 'sapi_id', 'List HPP', related='sapi_id.list_hpp_ids')
    list_vb_ids = fields.One2many('account.move.line', 'sapi_id', 'List VB', related='sapi_id.list_vb_ids')
    total_cip = fields.Float(string='Total CIP', compute='_compute_total_cip', store=True, digits=(1, 0))
    journal_id = fields.Many2one('account.journal', 'Journal')


    @api.depends('list_hpp_ids.amount', 'list_vb_ids.price_unit')
    def _compute_total_cip(self):
        for record in self:
            total_cip = 0.0
            for hpp_line in record.list_hpp_ids:
                total_cip += hpp_line.amount
            for vb_line in record.list_vb_ids:
                total_cip += vb_line.price_unit
            record.total_cip = total_cip
