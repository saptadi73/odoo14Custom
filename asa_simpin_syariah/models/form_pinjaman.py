from odoo import api, fields, models, _

class form_pinjaman(models.Model):
    _name = "form.pinjaman"
    _description = "Pinjaman Anggota"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'ref'

    name = fields.Char(string='Name')
    ref = fields.Char('No Pinjaman', default='/', copy=False)
    member_id = fields.Many2one('simpin_syariah.member', string='Nama Anggota')
    partner_id = fields.Many2one('res.partner', 'Customer')
    nama_pinjaman = fields.Char('Nama Pinjaman')
    tgl_pinjaman = fields.Date('Tanggal Pinjaman')
    nilai_pinjaman = fields.Float('Nilai Pinjaman')
    periode_angsuran = fields.Integer('Periode Angsuran')
    angsuran = fields.Float('Angsuran')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submit', 'Submitted'),
        ('check', 'Check Document'),
        ('approve', 'Approved'),
        ('active', 'Active'),
        ('close', 'Closed'),
        ('block', 'Blocked'),
    ], string='Status', default='draft', readonly=True, tracking=True)
    notes = fields.Text('Keterangan')

    @api.model
    def create(self, vals):
        vals['ref'] = self._generate_sequence()
        return super(form_pinjaman, self).create(vals)

    def _generate_sequence(self):
        sequence_code = 'pinjaman.anggota.sequence'
        sequence = self.env['ir.sequence'].sudo().search([('code', '=', sequence_code)], limit=1)

        if not sequence:
            sequence = self.env['ir.sequence'].sudo().create({
                'name': 'Pinjaman Anggota Sequence',
                'code': sequence_code,
                'padding': 4,  # Ubah sesuai kebutuhan
                'implementation': 'no_gap',
            })

        return sequence.next_by_id()

    def func_submit(self):
        if self.state == 'draft':
            self.state = 'submit'

    def func_approve(self):
        if self.state == 'submit':
            self.state = 'approve'

    def func_close(self):
        if self.state == 'approve':
            self.state = 'close'
