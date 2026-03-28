from odoo import api, fields, models, _

class SimpananAnggota(models.Model):
    _name = "form.simpanan"
    _description = "Simpanan Anggota Simpin Syariah"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'ref'

    @api.model
    def _default_currency(self):
        return self.env.user.company_id.currency_id.id

    # nomor_rekening = fields.Char(string='Nomor Rekening', default=lambda self: self.env['ir.sequence'].next_by_code('form.simpanan.sequence'))
    name = fields.Char('Name')
    ref = fields.Char('No Simpanan', default='/', copy=False)
    member_id = fields.Many2one('simpin_syariah.member', string='Nama Anggota', required=False,
                                domain=[('state', '=', 'done')])
    product_id = fields.Many2one('product.product', string='Produk', required=False,
                                 domain=[('is_syariah', '=', True)])
    currency_id = fields.Many2one('res.currency', string="Currency", readonly=True, default=_default_currency)
    balance = fields.Monetary(string='Balance', compute='_compute_balance', store=True, currency_field='currency_id')
    account_analytic_id = fields.Many2one('account.analytic.account', required=False, string='Analytic Account')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submit', 'Submitted'),
        ('check', 'Check Document'),
        ('approve', 'Approved'),
        ('active', 'Active'),
        ('close', 'Closed'),
        ('block', 'Blocked'),
    ], string='Status', default='draft', readonly=True, tracking=True)
    partner_id = fields.Many2one('res.partner', string='Customer')
    max_debit = fields.Float('Maksimal Debit', compute='_compute_amount_maxdebit', store=True)
    resource_name = fields.Char(string='Resource Name')

    @api.depends('simpanan_line_ids.debit')
    def _compute_balance(self):
        for record in self:
            total_debit = sum(line.debit for line in record.simpanan_line_ids)
            record.balance = total_debit

    @api.onchange('simpanan_line_ids')
    def _onchange_simpanan_line_ids(self):
        valid_lines = self.simpanan_line_ids.filtered(lambda line: line.tgl_simpanan)
        sorted_lines = valid_lines.sorted(key=lambda r: r.tgl_simpanan)
        current_balance = 0
        for line in sorted_lines:
            line.balance = current_balance + line.debit - line.credit
            current_balance = line.balance

    @api.model
    def create(self, vals):
        vals['ref'] = self._generate_sequence()
        return super(SimpananAnggota, self).create(vals)

    def _generate_sequence(self):
        sequence_code = 'simpanan.anggota.sequence'
        sequence = self.env['ir.sequence'].sudo().search([('code', '=', sequence_code)], limit=1)

        if not sequence:
            sequence = self.env['ir.sequence'].sudo().create({
                'name': 'Simpanan Anggota Sequence',
                'code': sequence_code,
                'padding': 4,  # Ubah sesuai kebutuhan
                'implementation': 'no_gap',
            })

        return sequence.next_by_id()

    @api.depends('balance', 'product_id')
    def _compute_amount_maxdebit(self):
        for record in self:
            if record.product_id and record.product_id.name in ['SIMPANAN HARI RAYA', 'SIMPANAN SUKARELA']:
                record.max_debit = record.balance * 0.8
            elif record.product_id and record.product_id.name in ['SIMPANAN POKOK', 'SIMPANAN WAJIB']:
                record.max_debit = record.balance  # Max debit = 100% of balance
            else:
                record.max_debit = 0.0

    def func_submit(self):
        if self.state == 'draft':
            self.state = 'submit'

    def func_approve(self):
        if self.state == 'submit':
            self.state = 'active'

    def func_close(self):
        if self.state == 'approve':
            self.state = 'close'

    simpanan_line_ids = fields.One2many('form.simpanan.line', 'simpanan_id', string='Simpanan Line Ids')

class SimpananAnggotaLine(models.Model):
    _name = "form.simpanan.line"
    _description = "Simpanan Line Anggota"

    simpanan_id = fields.Many2one('form.simpanan', 'Simpanan ID')
    tgl_simpanan = fields.Date('Tanggal')
    debit = fields.Float('Debit')
    credit = fields.Float('Kredit')
    keterangan = fields.Text('Keterangan')
    balance = fields.Float('Saldo')