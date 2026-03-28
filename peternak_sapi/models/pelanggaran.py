from odoo import models, fields
class pelanggaran(models.Model):
    _name = "pelanggaran.peternak"
    _description = "Pelanggaran"
    _rec_name = 'pelanggaran'

    pelanggaran = fields.Many2one('jenis.pelanggaran', string='Pelanggaran')
    jns_kegiatan = fields.Selection([
        ('1', 'Liter'),
        ('2', 'GDFP'),
    ], string='Jenis Kegiatan', required=True, tracking=True)
    keterangan = fields.Text(string='Keterangan')
    peternak_id = fields.Many2one('peternak.sapi', string='Nama Anggota')
    kode_peternak = fields.Char(related='peternak_id.kode_peternak', string='ID Peternak')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submit', 'Submit'),
        ('check', 'Check Peternak'),
        ('validate', 'Validasi'),
    ], string='State', readonly=True, default='draft', required=True, tracking=True)

    # def func_submit(self):
    #     if self.state == 'draft':
    #         self.state = 'check'

    def func_check(self):
        if self.state == 'draft':
            self.state = 'check'

    def func_validate(self):
        if self.state == 'check':
            self.state = 'validate'
