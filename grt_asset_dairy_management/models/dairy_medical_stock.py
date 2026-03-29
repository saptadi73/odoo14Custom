from odoo import _, api, fields, models
from odoo.exceptions import UserError


class DairyMedicalStockTransfer(models.Model):
    _name = 'dairy.medical.stock.transfer'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Distribusi Stok Medis ke Tas Petugas'
    _order = 'date desc, id desc'
    _rec_name = 'name'

    name = fields.Char(string='Nomor', copy=False, readonly=True, default='New')
    date = fields.Date(string='Tanggal', required=True, default=fields.Date.context_today, tracking=True)
    person_in_charge = fields.Char(string='Petugas')
    bag_location_id = fields.Many2one('stock.location', string='Lokasi Tas Petugas', required=True, domain=[('usage', '=', 'internal')])
    source_location_id = fields.Many2one('stock.location', string='Lokasi Gudang Medis', required=True, domain=[('usage', '=', 'internal')])
    line_ids = fields.One2many('dairy.medical.stock.transfer.line', 'transfer_id', string='Detail Produk')
    stock_move_ids = fields.Many2many('stock.move', string='Stock Moves', readonly=True, copy=False)
    reverse_stock_move_ids = fields.Many2many('stock.move', 'dairy_medical_transfer_reverse_stock_rel', 'transfer_id', 'move_id', string='Reverse Stock Moves', readonly=True, copy=False)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company, required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('posted', 'Posted'),
        ('cancel', 'Cancel'),
    ], string='Status', default='draft', tracking=True)
    note = fields.Text(string='Catatan')

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('dairy.medical.stock.transfer') or 'New'
        if not vals.get('source_location_id'):
            company = self.env.company
            vals['source_location_id'] = (company.dairy_medical_source_location_id or company.dairy_vitamin_source_location_id).id or False
        return super(DairyMedicalStockTransfer, self).create(vals)

    def action_open_bag_location_wizard(self):
        self.ensure_one()
        return {
            'name': _('Buat Lokasi Tas Petugas'),
            'type': 'ir.actions.act_window',
            'res_model': 'dairy.bag.location.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'active_model': self._name,
                'active_id': self.id,
            },
        }

    def _get_default_medical_source_location(self):
        self.ensure_one()
        return self.company_id.dairy_medical_source_location_id or self.company_id.dairy_vitamin_source_location_id

    def action_post(self):
        StockMove = self.env['stock.move']
        for record in self:
            if not record.line_ids:
                raise UserError(_('Detail distribusi stok medis belum diisi.'))
            if not record.source_location_id:
                raise UserError(_('Lokasi gudang medis wajib diisi.'))
            if not record.bag_location_id:
                raise UserError(_('Lokasi tas petugas wajib diisi.'))
            created_moves = StockMove
            for line in record.line_ids:
                line._validate_before_post()
                move = StockMove.create(line._prepare_stock_move_vals())
                move._action_confirm()
                move._action_done()
                created_moves |= move
            record.write({
                'stock_move_ids': [(6, 0, created_moves.ids)],
                'state': 'posted',
            })

    def _create_reverse_stock_moves(self):
        self.ensure_one()
        StockMove = self.env['stock.move']
        created_moves = StockMove
        for move in self.stock_move_ids.filtered(lambda m: m.state == 'done'):
            reverse_move = StockMove.create({
                'name': '%s REV' % (move.name or self.name),
                'company_id': move.company_id.id,
                'date': fields.Datetime.now(),
                'product_id': move.product_id.id,
                'product_uom': move.product_uom.id,
                'product_uom_qty': move.product_uom_qty,
                'location_id': move.location_dest_id.id,
                'location_dest_id': move.location_id.id,
                'reference': '%s/REV' % self.name,
                'origin': self.name,
            })
            reverse_move._action_confirm()
            reverse_move._action_done()
            created_moves |= reverse_move
        return created_moves

    def action_cancel(self):
        for record in self:
            if record.state != 'posted':
                record.state = 'cancel'
                continue
            reverse_moves = record._create_reverse_stock_moves()
            record.write({
                'reverse_stock_move_ids': [(6, 0, reverse_moves.ids)],
                'state': 'cancel',
            })

    def action_reset_to_draft(self):
        for record in self:
            if record.state == 'cancel':
                record.state = 'draft'


class DairyMedicalStockTransferLine(models.Model):
    _name = 'dairy.medical.stock.transfer.line'
    _description = 'Detail Distribusi Stok Medis'

    transfer_id = fields.Many2one('dairy.medical.stock.transfer', string='Distribusi', required=True, ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Produk', required=True, domain=[('type', 'in', ['product', 'consu'])])
    qty = fields.Float(string='Qty', required=True, default=1.0)
    product_uom_id = fields.Many2one('uom.uom', string='Satuan', related='product_id.uom_id', readonly=True)
    note = fields.Char(string='Catatan')

    def _validate_before_post(self):
        self.ensure_one()
        if not self.product_id:
            raise UserError(_('Produk pada distribusi stok medis wajib diisi.'))
        if self.qty <= 0:
            raise UserError(_('Qty distribusi stok medis harus lebih besar dari 0.'))
        if self.product_id.type not in ('product', 'consu'):
            raise UserError(_('Produk distribusi stok medis harus bertipe stok atau consumable.'))

    def _prepare_stock_move_vals(self):
        self.ensure_one()
        transfer = self.transfer_id
        return {
            'name': '%s - %s' % (transfer.name, self.product_id.display_name),
            'company_id': transfer.company_id.id,
            'date': transfer.date,
            'product_id': self.product_id.id,
            'product_uom': self.product_uom_id.id,
            'product_uom_qty': self.qty,
            'location_id': transfer.source_location_id.id,
            'location_dest_id': transfer.bag_location_id.id,
            'reference': transfer.name,
            'origin': transfer.name,
        }


class DairyBagStockReport(models.Model):
    _name = 'dairy.bag.stock.report'
    _description = 'Saldo Stok Tas Petugas'
    _auto = False
    _order = 'bag_location_name, product_name'

    bag_location_id = fields.Many2one('stock.location', string='Lokasi Tas', readonly=True)
    bag_location_name = fields.Char(string='Lokasi Tas', readonly=True)
    person_in_charge = fields.Char(string='Petugas', readonly=True)
    product_id = fields.Many2one('product.product', string='Produk', readonly=True)
    product_name = fields.Char(string='Produk', readonly=True)
    product_uom_id = fields.Many2one('uom.uom', string='Satuan', readonly=True)
    qty_on_hand = fields.Float(string='Saldo', readonly=True)
    company_id = fields.Many2one('res.company', string='Company', readonly=True)

    def init(self):
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW dairy_bag_stock_report AS (
                WITH bag_locations AS (
                    SELECT DISTINCT bag_location_id AS location_id, company_id, person_in_charge
                    FROM dairy_medical_stock_transfer
                    WHERE bag_location_id IS NOT NULL
                    UNION
                    SELECT DISTINCT bag_location_id AS location_id, company_id, person_in_charge
                    FROM dairy_treatment_record
                    WHERE bag_location_id IS NOT NULL
                )
                SELECT
                    row_number() OVER () AS id,
                    bl.location_id AS bag_location_id,
                    sl.complete_name AS bag_location_name,
                    COALESCE(bl.person_in_charge, sl.name) AS person_in_charge,
                    sq.product_id,
                    pt.name AS product_name,
                    pt.uom_id AS product_uom_id,
                    SUM(sq.quantity) AS qty_on_hand,
                    bl.company_id
                FROM bag_locations bl
                JOIN stock_location sl ON sl.id = bl.location_id
                JOIN stock_quant sq ON sq.location_id = bl.location_id
                JOIN product_product pp ON pp.id = sq.product_id
                JOIN product_template pt ON pt.id = pp.product_tmpl_id
                GROUP BY bl.location_id, sl.complete_name, COALESCE(bl.person_in_charge, sl.name), sq.product_id, pt.name, pt.uom_id, bl.company_id
                HAVING SUM(sq.quantity) <> 0
            )
        """)


class DairyBagMovementReport(models.Model):
    _name = 'dairy.bag.movement.report'
    _description = 'Mutasi Stok Tas Petugas'
    _auto = False
    _order = 'date desc, id desc'

    date = fields.Datetime(string='Tanggal', readonly=True)
    bag_location_id = fields.Many2one('stock.location', string='Lokasi Tas', readonly=True)
    bag_location_name = fields.Char(string='Lokasi Tas', readonly=True)
    person_in_charge = fields.Char(string='Petugas', readonly=True)
    product_id = fields.Many2one('product.product', string='Produk', readonly=True)
    product_name = fields.Char(string='Produk', readonly=True)
    product_uom_id = fields.Many2one('uom.uom', string='Satuan', readonly=True)
    qty_in = fields.Float(string='Masuk', readonly=True)
    qty_out = fields.Float(string='Keluar', readonly=True)
    qty_signed = fields.Float(string='Mutasi Netto', readonly=True)
    source_location_id = fields.Many2one('stock.location', string='Dari', readonly=True)
    dest_location_id = fields.Many2one('stock.location', string='Ke', readonly=True)
    reference = fields.Char(string='Referensi', readonly=True)
    origin = fields.Char(string='Origin', readonly=True)
    company_id = fields.Many2one('res.company', string='Company', readonly=True)

    def init(self):
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW dairy_bag_movement_report AS (
                WITH bag_locations AS (
                    SELECT DISTINCT bag_location_id AS location_id, company_id, person_in_charge
                    FROM dairy_medical_stock_transfer
                    WHERE bag_location_id IS NOT NULL
                    UNION
                    SELECT DISTINCT bag_location_id AS location_id, company_id, person_in_charge
                    FROM dairy_treatment_record
                    WHERE bag_location_id IS NOT NULL
                ),
                inbound AS (
                    SELECT
                        sm.id,
                        sm.date,
                        bl.location_id AS bag_location_id,
                        sl.complete_name AS bag_location_name,
                        COALESCE(bl.person_in_charge, sl.name) AS person_in_charge,
                        sm.product_id,
                        pt.name AS product_name,
                        pt.uom_id AS product_uom_id,
                        sm.product_uom_qty AS qty_in,
                        0.0 AS qty_out,
                        sm.product_uom_qty AS qty_signed,
                        sm.location_id AS source_location_id,
                        sm.location_dest_id AS dest_location_id,
                        sm.reference,
                        sm.origin,
                        sm.company_id
                    FROM stock_move sm
                    JOIN bag_locations bl ON bl.location_id = sm.location_dest_id
                    JOIN stock_location sl ON sl.id = bl.location_id
                    JOIN product_product pp ON pp.id = sm.product_id
                    JOIN product_template pt ON pt.id = pp.product_tmpl_id
                    WHERE sm.state = 'done'
                ),
                outbound AS (
                    SELECT
                        sm.id + 1000000000,
                        sm.date,
                        bl.location_id AS bag_location_id,
                        sl.complete_name AS bag_location_name,
                        COALESCE(bl.person_in_charge, sl.name) AS person_in_charge,
                        sm.product_id,
                        pt.name AS product_name,
                        pt.uom_id AS product_uom_id,
                        0.0 AS qty_in,
                        sm.product_uom_qty AS qty_out,
                        -sm.product_uom_qty AS qty_signed,
                        sm.location_id AS source_location_id,
                        sm.location_dest_id AS dest_location_id,
                        sm.reference,
                        sm.origin,
                        sm.company_id
                    FROM stock_move sm
                    JOIN bag_locations bl ON bl.location_id = sm.location_id
                    JOIN stock_location sl ON sl.id = bl.location_id
                    JOIN product_product pp ON pp.id = sm.product_id
                    JOIN product_template pt ON pt.id = pp.product_tmpl_id
                    WHERE sm.state = 'done'
                )
                SELECT * FROM inbound
                UNION ALL
                SELECT * FROM outbound
            )
        """)
