from odoo import models, fields, api
import math

class SelisihHarga(models.Model):
    _name = "selisih.harga"
    _description = "Selisih Harga"
    _rec_name = 'periode_id'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    periode_id = fields.Many2one('periode.setoran', 'Periode')
    tps_id = fields.Many2one('tps.liter', string='TPS')
    account_debit_id = fields.Many2one('account.account', 'Debit Account')
    account_credit_id = fields.Many2one('account.account', 'Credit Account')
    journal_id = fields.Many2one('account.journal', 'Journal')
    tot_selisih_harga = fields.Float('Total Selisih Harga', compute='_compute_tot_selisih_harga', readonly=False)
    selisih_harga_ids = fields.One2many('selisih.harga.line', 'selisih_harga_id', 'Selisih Harga IDS')
    journal_entry_id = fields.Many2one('account.move', 'Journal Entry')
    date = fields.Date('Accounting Date')

    def generate_journal_entry(self):
        for record in self:
            move_lines = []
            # Membuat baris debit
            debit_line = {
                'name': 'Debit Entry',
                'account_id': record.account_debit_id.id,
                'debit': record.tot_selisih_harga,
                'credit': 0.0,
            }
            move_lines.append((0, 0, debit_line))

            # Membuat line kredit
            credit_line = {
                'name': 'Kredit Entry',
                'account_id': record.account_credit_id.id,
                'debit': 0.0,
                'credit': record.tot_selisih_harga,
            }
            move_lines.append((0, 0, credit_line))

            # Membuat entri jurnal
            journal_entry = self.env['account.move'].create({
                'journal_id': record.journal_id.id,
                'ref': f"Selisih Harga - {record.periode_id.periode_setoran}",
                'date': record.date,
                'line_ids': move_lines,
            })

            # Menghubungkan entri jurnal dengan rekaman SelisihHarga
            record.write({'journal_entry_id': journal_entry.id})

    @api.depends('selisih_harga_ids.total_selisih')
    def _compute_tot_selisih_harga(self):
        for record in self:
            total_selisih = sum(record.selisih_harga_ids.mapped('total_selisih'))
            # Membulatkan total_selisih_harga
            record.tot_selisih_harga = round(total_selisih, 0)

    def get_selisih_harga(self):
        for record in self:
            # Hapus data lama di selisih_harga_ids
            record.selisih_harga_ids.unlink()

            # Ambil data dari liter_sapi berdasarkan periode_id dan tps_id
            liter_sapi_records = self.env['liter.sapi'].search([
                ('periode_id', '=', record.periode_id.id),
                ('tps_id', '=', record.tps_id.id),
            ])

            # Map data ke SelisihHargaLine
            selisih_harga_lines = []
            for liter_sapi_record in liter_sapi_records:
                selisih_harga_line = {
                    'selisih_harga_id': record.id,
                    'kode_peternak': liter_sapi_record.kode_peternak,
                    'peternak_id': liter_sapi_record.peternak_id.id,
                    'setoran': liter_sapi_record.setoran,
                    'harga_satuan': liter_sapi_record.harga_satuan,
                    'total_harga_estimasi': liter_sapi_record.total_harga_estimasi,
                    'harga_real': liter_sapi_record.harga_real,
                    'total_harga_real': liter_sapi_record.total_harga_real,
                }
                selisih_harga_lines.append((0, 0, selisih_harga_line))

            # Tambahkan data baru ke selisih_harga_ids
            record.write({'selisih_harga_ids': selisih_harga_lines})

class SelisihHargaLine(models.Model):
    _name = "selisih.harga.line"
    _description = "Tabel Selisih Harga"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    selisih_harga_id = fields.Many2one('selisih.harga', 'Selisih ID')
    kode_peternak = fields.Char(string='ID Peternak')
    peternak_id = fields.Many2one('peternak.sapi', 'Peternak')
    setoran = fields.Float('Total Setoran Susu (KG)')
    harga_satuan = fields.Float('Harga Rata-Rata')
    total_harga_estimasi = fields.Float('Total')
    harga_real = fields.Float('Harga Real')
    total_harga_real = fields.Float('Total')
    total_selisih = fields.Float('Selisih', compute='_compute_total_selisih')

    @api.depends('total_harga_real', 'total_harga_estimasi')
    def _compute_total_selisih(self):
        for record in self:
            if record.total_harga_real != 0:
                record.total_selisih = record.total_harga_real - record.total_harga_estimasi
            else:
                record.total_selisih = 0