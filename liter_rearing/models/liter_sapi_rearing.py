from odoo import models, fields, api
from datetime import datetime, timedelta
from collections import defaultdict
from odoo.exceptions import UserError


class liter_sapi_rearing(models.Model):
    _name = "liter.sapi.rearing"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Liter Sapi Rearing"
    _rec_name = 'tps_id'

    tps_id = fields.Many2one('tps.liter', string='TPS')
    picking_type_id = fields.Many2one('stock.picking.type', 'Operation Type')
    location_id = fields.Many2one('stock.location', 'Location')
    location_dest_id = fields.Many2one('stock.location', 'Destination Location')
    sapi_ids = fields.Many2many('sapi', string='Sapi')
    eartag_id = fields.Char('Eartag ID', compute='_compute_eartag_id')
    # purchase_count = fields.Integer(compute='compute_purchase_count')
    hasil_prod = fields.Float('Hasil Produksi')
    total_setoran_pagi = fields.Float('Total Setoran Pagi', compute='_compute_total_setoran')
    total_setoran_sore = fields.Float('Total Setoran Sore', compute='_compute_total_setoran')
    setoran = fields.Float('Total Setoran Susu')
    product_id_3 = fields.Many2one('product.product', 'Product', domain=[('is_rearing', '=', 'true')])
    tgl_setoran = fields.Datetime('Tanggal Setoran', default=fields.Datetime.now)
    tgl_awal = fields.Date('Tanggal Awal')
    tgl_akhir = fields.Date('Tanggal Akhir')
    periode_id = fields.Many2one('periode.setoran', 'Periode')
    pagi = fields.Boolean('Pagi', compute='_compute_shift')
    sore = fields.Boolean('Sore', compute='_compute_shift')
    tipe_setor = fields.Selection([
        ('1', 'Pagi'),
        ('2', 'Sore')
    ], 'Tipe Setor', required=False)
    picking_created = fields.Boolean('Picking Created', default=False)
    tipe_id = fields.Many2one('master.tipe.sapi', 'Tipe Sapi')
    uom_id = fields.Many2one('uom.uom', 'Uom',
                             default=lambda self: self.env['uom.uom'].search([('name', '=', 'Kg')], limit=1))
    tot_set_pag_sor = fields.Float('Setoarn Pagi Sore', compute='_compute_tot_set_pag_sor')
    name = fields.Char('Keterangan')
    harga_satuan = fields.Float('Harga Satuan', compute='_compute_harga_satuan')
    tot_nilai = fields.Float('Total Nilai', store=True)

    persediaan_nilai_ids = fields.One2many('persediaan.nilai.line', 'liter_sapi_rearing_id', string='Persediaan Nilai Ids')

    def default_get(self, fields):
        defaults = super(liter_sapi_rearing, self).default_get(fields)
        default_product = self.env['product.product'].search([('is_rearing', '=', True)], limit=1)
        if default_product:
            defaults['product_id_3'] = default_product.id

        return defaults

    @api.depends('setoran_line_rearing_ids')
    def _compute_total_setoran(self):
        for record in self:
            total_pagi = sum(line.setoran for line in record.setoran_line_rearing_ids if line.tipe_setor == '1')
            total_sore = sum(line.setoran for line in record.setoran_line_rearing_ids if line.tipe_setor == '2')
            record.total_setoran_pagi = total_pagi
            record.total_setoran_sore = total_sore

    @api.onchange('tipe_id')
    def onchange_tipe_id(self):
        if self.tipe_id:
            # Mengambil sapi yang memiliki tipe_id dan is_rearing = True
            sapi_records = self.env['sapi'].search([('tipe_id', '=', self.tipe_id.id), ('is_rearing', '=', True)])
            self.sapi_ids = [(6, 0, sapi_records.ids)]
        else:
            # Jika tipe_id tidak diisi, maka sapi_ids dikosongkan
            self.sapi_ids = [(5, 0, 0)]

    @api.depends('tot_nilai', 'tot_set_pag_sor')
    def _compute_harga_satuan(self):
        for record in self:
            if record.tot_set_pag_sor != 0:
                record.harga_satuan = record.tot_nilai / record.tot_set_pag_sor
            else:
                record.harga_satuan = 0.0

    def get_nilai_persediaan_transactions(self):
        """Function to fetch rearing transactions and populate PersediaanNilaiLine"""
        # Delete all PersediaanNilaiLine related to the current instance
        self.persediaan_nilai_ids.unlink()

        for persediaan in self:
            # Replace 'account.move.line' with the appropriate model
            account_move_lines = self.env['account.move.line'].search([
                ('account_id.code', '=', '101.0402.001'),
                ('date', '<=', persediaan.tgl_setoran),
                ('move_id.state', '=', 'posted'),
                # Add other criteria as needed
            ])

            # Use defaultdict to store aggregated values based on account_id
            aggregated_values = defaultdict(lambda: {'debit': 0.0, 'credit': 0.0, 'balance': 0.0, 'count': 0})

            for move_line in account_move_lines:
                account_id = move_line.account_id.id
                aggregated_values[account_id]['debit'] += move_line.debit
                aggregated_values[account_id]['credit'] += move_line.credit
                aggregated_values[account_id]['balance'] += move_line.balance
                aggregated_values[account_id]['count'] += 1

            # Access the related account.move and get its date
            move_date = move_line.move_id.date

            tot_nilai = sum(values['balance'] for values in aggregated_values.values())

            for account_id, values in aggregated_values.items():
                # Check if count is greater than 0 to avoid division by zero

                persediaan_nilai_data = {
                    'liter_sapi_rearing_id': persediaan.id,
                    'date': move_date,
                    'account_id': account_id,
                    'debit': values['debit'],
                    'credit': values['credit'],
                    'balance': values['balance'],
                }

                # Create a new PersediaanNilaiLine
                self.env['persediaan.nilai.line'].create(persediaan_nilai_data)

        # Change the status of PersediaanNilai to 'calculate' after fetching the data
        # self.write({'state': 'calculate'})

        # Check if tot_nilai is negative, if so, raise a warning
        if tot_nilai < 0:
            raise UserError("Total Nilai tidak boleh negatif!")

        persediaan.write({'tot_nilai': tot_nilai})

    # Add a button to the form view
    def button_get_nilai_persediaan_transactions(self):
        self.get_nilai_persediaan_transactions()
        return True

    @api.depends('total_setoran_pagi', 'total_setoran_sore')
    def _compute_tot_set_pag_sor(self):
        for record in self:
            record.tot_set_pag_sor = record.total_setoran_pagi + record.total_setoran_sore

    def _compute_shift(self):
        for record in self:
            if record.tgl_setoran:
                tgl_setoran_time = fields.Datetime.from_string(record.tgl_setoran).time()
                record.pagi = datetime.strptime("06:00:00", "%H:%M:%S").time() <= tgl_setoran_time <= datetime.strptime("12:00:00", "%H:%M:%S").time()
                record.sore = tgl_setoran_time >= datetime.strptime("12:00:01", "%H:%M:%S").time()

    @api.depends('sapi_ids')
    def _compute_eartag_id(self):
        for record in self:
            eartag_ids = [str(sapi.eartag_id) for sapi in record.sapi_ids if
                          sapi.eartag_id]  # konversi ke string dan hindari None atau False
            eartag_str = ', '.join(eartag_ids)
            record.eartag_id = eartag_str

    # @api.depends('total_setoran_pagi', 'total_setoran_sore')
    # def _compute_total_setoran(self):
    #     for record in self:
    #         total_setoran = record.total_setoran_pagi + record.total_setoran_sore
    #         record.setoran = total_setoran
    #
    # @api.depends('setoran_line_rearing_ids.setoran', 'setoran_line_rearing_ids.tipe_setor')
    # def _compute_total_setoran_pagi(self):
    #     for record in self:
    #         total_setoran_pagi = sum(
    #             line.setoran for line in record.setoran_line_rearing_ids if line.tipe_setor == '1'
    #         )
    #         record.total_setoran_pagi = total_setoran_pagi
    #
    # @api.depends('setoran_line_rearing_ids.setoran', 'setoran_line_rearing_ids.tipe_setor')
    # def _compute_total_setoran_sore(self):
    #     for record in self:
    #         total_setoran_sore = sum(
    #             line.setoran for line in record.setoran_line_rearing_ids if line.tipe_setor == '2'
    #         )
    #         record.total_setoran_sore = total_setoran_sore

    @api.onchange('tgl_setoran')
    def _onchange_tgl_setoran(self):
        if self.tgl_setoran:
            periode_setoran_obj = self.env['periode.setoran']
            periode_setoran = periode_setoran_obj.search([
                ('periode_setoran_awal', '<=', self.tgl_setoran),
                ('periode_setoran_akhir', '>=', self.tgl_setoran)
            ])
            if periode_setoran:
                self.periode_id = periode_setoran.id
            else:
                # Jika tidak ada periode yang sesuai, Anda dapat menangani kasus ini sesuai kebutuhan Anda.
                # Misalnya, memberikan default atau memberikan pesan kesalahan.
                self.periode_id = False

    @api.onchange('periode_id')
    def _onchange_periode_id(self):
        if self.periode_id:
            self.tgl_awal = self.periode_id.periode_setoran_awal
            self.tgl_akhir = self.periode_id.periode_setoran_akhir
        else:
            # Jika periode_id kosong, atur tgl_awal dan tgl_akhir menjadi False atau nilai default lainnya.
            self.tgl_awal = False
            self.tgl_akhir = False

    # def create_po(self):
    #     purchase_order_obj = self.env['purchase.order']
    #     purchase_order_line_obj = self.env['purchase.order.line']
    #     for liter in self:
    #         product = self.env['product.product'].search([('product_tmpl_id', '=', liter.product_id.id)])
    #         vals = {
    #             'partner_id': liter.peternak_id.partner_id.id,
    #             'date_order': datetime.now(),
    #             'state': 'draft',
    #             'setoran_id': self.id
    #         }
    #         purchase_order = purchase_order_obj.create(vals)
    #         po_line_vals = {
    #             'product_id': product.id,
    #             'product_qty': liter.setoran,
    #             'name': product.name,
    #             'price_unit': liter.harga_satuan,
    #             'date_planned': datetime.now(),
    #             'product_uom': product.uom_po_id.id,
    #             'order_id': purchase_order.id,
    #         }
    #
    #         purchase_order_line = purchase_order_line_obj.create(po_line_vals)

    def generate_setoran_lines(self):
        # Hapus setoran yang sudah ada untuk tipe_setor yang sama sebelum membuat atau memperbarui setoran baru
        existing_setoran_lines = self.env['setoran.line.rearing'].search([
            ('liter_sapi_rearing_id', '=', self.id),
            ('tipe_setor', '=', self.tipe_setor),
        ])

        # Hitung jumlah total rekaman dalam sapi_ids
        total_sapi_records = len(self.sapi_ids)

        # Distribusikan total setoran di antara sapi_ids dan buat atau perbarui setoran_line_rearing_ids
        for sapi in self.sapi_ids:
            setoran_line_values = {
                'liter_sapi_rearing_id': self.id,
                'uom_id': self.env['uom.uom'].search([('name', '=', 'Kg')], limit=1).id,
                'tgl_setor': fields.Datetime.now(),
                'tipe_setor': self.tipe_setor,
                'sapi_id': sapi.id,
                'eartag_id': sapi.eartag_id,
                'product_id_2': self.product_id_3.id,
            }

            if self.tipe_setor == '1':  # Pagi
                setoran_line_values['setoran'] = (1 / total_sapi_records) * self.hasil_prod
            elif self.tipe_setor == '2':  # Sore
                setoran_line_values['setoran'] = (1 / total_sapi_records) * self.hasil_prod

            # Cari baris setoran yang sudah ada untuk sapi ini
            existing_line = existing_setoran_lines.filtered(lambda line: line.sapi_id == sapi)

            if existing_line:  # Jika sudah ada, perbarui nilainya
                existing_line.write(setoran_line_values)
            else:  # Jika belum ada, buat baris baru
                self.env['setoran.line.rearing'].create(setoran_line_values)

        # Hapus setoran yang tidak terpakai
        unused_setoran_lines = existing_setoran_lines - self.env['setoran.line.rearing'].search([
            ('liter_sapi_rearing_id', '=', self.id),
            ('tipe_setor', '=', self.tipe_setor),
        ])
        unused_setoran_lines.unlink()


    setoran_line_rearing_ids = fields.One2many('setoran.line.rearing', 'liter_sapi_rearing_id', string='Setoran Line Rearing Ids')

    # def generate_stock_picking(self):
    #     for record in self:
    #         # Membuat stock picking
    #         picking_type = record.picking_type_id
    #         picking_data = {
    #             'picking_type_id': picking_type.id,
    #             'scheduled_date': record.tgl_setoran,
    #             'location_id': record.location_id.id,
    #             'location_dest_id': record.location_dest_id.id,
    #             # tambahkan field lain yang dibutuhkan untuk stock.picking
    #         }
    #         picking = self.env['stock.picking'].create(picking_data)
    #
    #         # Membuat move line
    #         for setoran_line in record.setoran_line_rearing_ids:
    #             move_data = {
    #                 'picking_id': picking.id,
    #                 'product_id': picking.product_id.id,
    #                 'product_uom_qty': picking.tot_set_pag_sor,
    #                 'product_uom': picking.uom_id.id,
    #                 'date': picking.tgl_setoran,
    #                 'partner_id': picking.partner_id.id,
    #                 # 'name': setoran_line.note,
    #                 'location_id': picking.location_id.id,
    #                 'location_dest_id': picking.location_dest_id.id,
    #                 'tipe_id': picking.tipe_id.id,
    #                 'sapi_ids': [(6, 0, picking.sapi_ids)],  # Menggunakan metode [(6, 0, ids)] untuk many2many
    #                 # Gantilah sesuai kebutuhan
    #                 # tambahkan field lain yang dibutuhkan untuk stock.move
    #             }
    #             move_line = self.env['stock.move'].create(move_data)
    #
    #             # Menghubungkan move line dengan liter_sapi_rearing_id
    #             setoran_line.write({'move_line_id': move_line.id})
    #
    #         # Menandai liter.sapi.rearing bahwa stock.picking sudah dibuat
    #         record.write({'picking_created': True})

    def generate_stock_picking(self):
        # Membuat stock.picking
        picking_vals = {
            'picking_type_id': self.picking_type_id.id,
            'location_id': self.location_id.id,
            'location_dest_id': self.location_dest_id.id,
            'scheduled_date': self.tgl_setoran,
        }
        picking = self.env['stock.picking'].create(picking_vals)

        # Membuat stock.move
        move_vals = {
            'product_id': self.product_id_3.id,
            'product_uom_qty': self.tot_set_pag_sor,
            'product_uom': self.uom_id.id,
            'picking_id': picking.id,
            'location_id': self.location_id.id,
            'location_dest_id': self.location_dest_id.id,
            'tipe_id': self.tipe_id.id,
            'date': self.tgl_setoran,
            'name': self.name,
            'price': self.harga_satuan,
        }
        move = self.env['stock.move'].create(move_vals)

        # Menghubungkan sapi_ids ke move
        move.write({'sapi_ids': [(6, 0, self.sapi_ids.ids)]})

        # Menyimpan eartag_id di move_ids_without_package
        move_ids_without_package = picking.move_ids_without_package
        move_ids_without_package.write({'eartag_id': self.eartag_id})

        # Tandai bahwa picking telah dibuat
        self.write({'picking_created': True})

        # Mengatur is_rearing menjadi True
        picking.write({'is_rearing': True})

        # Jika Anda memiliki lebih banyak field yang perlu dihubungkan atau diisi, Anda dapat menambahkannya di sini

        # return {
        #     'type': 'ir.actions.act_window.message',
        #     'title': 'Success',
        #     'message': 'Stock Picking berhasil dibuat.',
        # }


# class purchase(models.Model):
#     _inherit = "purchase.order"
#
#     setoran_id = fields.Many2one('liter.sapi', 'Setoran')
#     bj = fields.Integer('BJ')
#     # bj_pagi = fields.Integer('BJ Pagi')
#     # bj_sore = fields.Integer('BJ Sore')
#     grade = fields.Char('Grade')


class SetoranLineRearing(models.Model):
    _name = 'setoran.line.rearing'
    _description = 'Setoran Line Rearing'

    liter_sapi_rearing_id = fields.Many2one('liter.sapi.rearing', 'Liter Sapi Rearing Id')
    setoran = fields.Float('Setoran')
    uom_id = fields.Many2one('uom.uom', 'Uom', default=lambda self: self.env['uom.uom'].search([('name', '=', 'Kg')], limit=1))
    tps_id = fields.Many2one('tps.liter', string='TPS', related='liter_sapi_rearing_id.tps_id', store=True)
    tgl_setor = fields.Datetime('Tanggal Setor')
    tipe_setor = fields.Selection([
        ('1', 'Pagi'),
        ('2', 'Sore')
    ], 'Tipe Setor', required=False)
    sapi_id = fields.Many2one('sapi', 'Sapi')
    eartag_id = fields.Char('Eartag ID')
    product_id = fields.Many2one('product.template', 'Product')
    product_id_2 = fields.Many2one('product.product', 'Product')
    move_line_id = fields.Many2one('stock.move', 'Move Line')

class PersediaanNilaiLine(models.Model):
    _name = 'persediaan.nilai.line'
    _description = 'Persediaan Nilai Line'

    liter_sapi_rearing_id = fields.Many2one('liter.sapi.rearing', 'Liter Sapi Rearing Id')
    date = fields.Date('Date')
    account_id = fields.Many2one('account.account', 'Account')
    debit = fields.Float('Debit')
    credit = fields.Float('Credit')
    balance = fields.Float('Balance')