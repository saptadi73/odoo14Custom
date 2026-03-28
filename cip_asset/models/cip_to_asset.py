from odoo import models, fields, api
from odoo.exceptions import UserError

class CipToAsset(models.Model):
    _name = "cip.to.asset"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "CIP To Asset"
    _rec_name = 'name'

    name = fields.Char(string='Nama')
    eartag_id = fields.Char('Eartag ID')
    sapi_id = fields.Many2one('sapi', string='Sapi', readonly=False)
    category_asset_id = fields.Many2one('account.asset.category', 'Category Asset')
    asset_id = fields.Many2one('account.asset.asset', 'Asset', readonly=True)
    date = fields.Date('Date')
    category_cip_id = fields.Many2one('type.cip', 'Category CIP')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('posted', 'Posted'),
        ('cancel', 'Cancel'),
    ], string='State', readonly=True, default='draft', required=True, tracking=True)
    journal_entry = fields.Many2one('account.move', 'Journal Entry')

    def func_posted(self):
        if self.state == 'draft':
            self.state = 'posted'

    def func_cancel(self):
        if self.state == 'posted':
            self.state = 'cancel'

    def func_set_draft(self):
        if self.state == 'cancel':
            self.state = 'draft'

    @api.onchange('eartag_id')
    def _onchange_eartag_id(self):
        if self.eartag_id:
            sapi = self.env['sapi'].search([('eartag_id', '=', self.eartag_id)], limit=1)
            self.sapi_id = sapi.id
            self.category_cip_id = sapi.category_cip_id.id

    # @api.onchange('eartag_id')
    # def onchange_eartag_id(self):
    #     if self.eartag_id:
    #         sapi = self.env['sapi'].search([('eartag_id', '=', self.eartag_id)], limit=1)
    #         if sapi:
    #             self.sapi_id = sapi.id
    #             # Tambahkan kondisi untuk mengisi category_cip_id berdasarkan data sapi
    #             if sapi.category_cip_id:
    #                 self.category_cip_id = sapi.category_cip_id.id
    #             else:
    #                 # Jika sapi tidak memiliki category_cip_id, Anda dapat menentukan nilai default atau mengosongkan bidang
    #                 self.category_cip_id = False
    #         else:
    #             # Reset sapi_id jika tidak ditemukan sapi dengan eartag_id tersebut
    #             self.sapi_id = False
    #             # Reset category_cip_id jika tidak ditemukan sapi
    #             self.category_cip_id = False

    def generate_to_asset(self):
        cip_records = self.search([])

        for cip_record in cip_records:
            category = self.env['account.asset.category'].browse(self.category_asset_id.id)
            asset_record = self.env['account.asset.asset'].create({
                'name': cip_record.name,
                'eartag_id': cip_record.eartag_id,
                'sapi_id': cip_record.sapi_id.id,
                'category_id': cip_record.category_asset_id.id,
                'value': cip_record.total_cip,
                'date': cip_record.date,
                'method': category.method,
                'method_number': category.method_number,
                'method_time': category.method_time,
                'method_period': category.method_period,
                'method_progress_factor': category.method_progress_factor,
                'method_end': category.method_end,
                'prorata': category.prorata,
                'account_analytic_id': category.account_analytic_id.id
                # Tambahkan field lain sesuai kebutuhan
            })

            # Simpan asset_record.id ke dalam cip_record untuk referensi
            cip_record.write({'asset_id': asset_record.id})

            # Perbarui nilai is_asset menjadi True pada rekaman sapi yang sesuai
            cip_record.sapi_id.write({'is_asset': True})

    def generate_journal_entry(self):
        for cip_to_asset in self:
            move_lines = []

            # Membuat line debit
            debit_line = {
                'name': 'Debit Entry',
                'account_id': cip_to_asset.category_asset_id.account_asset_id.id,
                'debit': cip_to_asset.total_cip,
                'credit': 0.0,
            }
            move_lines.append((0, 0, debit_line))

            # Membuat line kredit
            credit_line = {
                'name': 'Kredit Entry',
                'account_id': cip_to_asset.category_cip_id.account_id.id,
                'debit': 0.0,
                'credit': cip_to_asset.total_cip,
            }
            move_lines.append((0, 0, credit_line))

            # Membuat record di account.move
            journal_entry = self.env['account.move'].create({
                'journal_id': cip_to_asset.journal_id.id,
                'date': cip_to_asset.date,
                'ref': cip_to_asset.name,
                'line_ids': move_lines,
            })

            # Mengupdate asset_id di CipToAsset dengan ID dari journal entry yang baru dibuat
            cip_to_asset.write({'journal_entry': journal_entry.id, 'state': 'posted'})

        return True

