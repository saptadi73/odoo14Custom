from odoo import models, fields, api
from datetime import datetime, timedelta
from odoo.exceptions import UserError
from collections import defaultdict

class liter_sapi(models.Model):
    _name = "liter.sapi"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Liter Sapi"
    _rec_name = 'tps_id'

    tgl_awal = fields.Date('Tanggal Awal', readonly=False)
    tgl_akhir = fields.Date('Tanggal Akhir', readonly=False)
    tps_id = fields.Many2one('tps.liter', string='TPS')
    peternak_id = fields.Many2one('peternak.sapi', 'Peternak')
    partner_id = fields.Many2one('res.partner', related='peternak_id.partner_id', string='Partner')
    tipe_mitra = fields.Selection([
        ('1', 'Mitra 1'),
        ('2', 'Mitra 2'),
    ], string='Tipe Mitra')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('appr_usaha', 'Approve Usaha'),
        ('tlk_usaha', 'Tolak Usaha'),
        ('cln_anggota', 'Calon Anggota'),
        ('anggota', 'Anggota Penuh'),
        ('resign', 'Non Active'),
    ], string='Status', related='peternak_id.state')
    kode_peternak = fields.Char(related='peternak_id.kode_peternak', string='ID Peternak')
    id_sapi = fields.Many2many('sapi', string='Nama Sapi', domain=[('state', '=', 'laktasi')], related='peternak_id.sapi_ids', readonly=False)
    sapi_ids = fields.Many2many('sapi', 'liter_sapi_sapi_rel', string='Nama Sapi', readonly=False)
    # sapi_ids = fields.One2many('sapi', 'peternak_id', string='Nama Sapi', compute='_compute_sapi_ids', readonly=False,
    #                            store=True, domain=[('state', '=', 'kering')])
    kelompok_id = fields.Many2one(related='peternak_id.kelompok_id', string='Kelompok Peternak')
    contact_address = fields.Char('Alamat', related='peternak_id.contact_address')
    setor = fields.Char('Setor Liter')
    bj = fields.Integer('BJ')
    purchase_count = fields.Integer(compute='compute_purchase_count')
    total_setoran_pagi = fields.Float('Total Setoran Pagi (KG)', compute='_compute_total_setoran_pagi')
    total_setoran_sore = fields.Float('Total Setoran Sore (KG', compute='_compute_total_setoran_sore')
    total_setoran_pagi_l = fields.Float('Total Setoran Pagi (L)', compute='_compute_total_setoran_pagi_l')
    total_setoran_sore_l = fields.Float('Total Setoran Sore (L', compute='_compute_total_setoran_sore_l')
    setoran = fields.Float('Total Setoran Susu (KG)', compute='_compute_total_setoran', readonly=True)
    setoran_l = fields.Float('Total Setoran Susu (L)', compute='_compute_total_setoran_l')
    # harga_kual = fields.Float('Harga Kualitas', compute='hitung_harga_kualitas')
    harga_kual = fields.Float('Harga Kualitas', compute='_compute_harga_kual')
    insen_prod = fields.Float('Insentif Produksi', compute='jumlah_insen_prod')
    insen_pmk = fields.Float('Insentif PMK', compute='jumlah_insen_pmk')
    insen_daya_saing = fields.Float('Insentif Daya Saing', compute='_compute_insen_daya_saing')
    harga_satuan = fields.Float('Harga Satuan', compute='hitung_jumlah_harga_satuan')
    harga_real = fields.Float('Harga Real')
    harga_selisih = fields.Float('Harga Selisih', compute='_compute_harga_selish')
    total_harga_selisih = fields.Float('Total Harga Selisih', compute='hitung_total_harga_susu_selisih')
    #lab
    suhu = fields.Float('Suhu')
    fat_id = fields.Many2one('tabel.fat', 'FAT')
    snf = fields.Float('SNF')
    ts = fields.Float('TS', digits=(1, 3), compute='_compute_ts', store=True, readonly=True)
    pro = fields.Float('Pro')
    lac = fields.Float('Lac')
    salts = fields.Float('Salts')
    add_water = fields.Float('Add Water')
    freez_point = fields.Float('Freezing Point')
    tpc_kan_id = fields.Many2one('tabel.tpc.kan', 'TPC KAN')
    tpc_kan = fields.Char('TPC KAN')
    mbrt_id = fields.Many2one('tabel.mbrt', 'MBRT')
    grade_id = fields.Many2one('tabel.grade', 'Grade')
    nilai_grade = fields.Float('Nilai Grade', related='grade_id.nilai')
    pres_grade = fields.Float('%Grade')
    # jenis_pelanggaran_liter_ids = fields.One2many('pelanggaran.peternak', 'peternak_name', 'Jenis Pelanggaran')
    jenis_pelanggaran = fields.Many2one('pelanggaran.peternak', 'Pelanggaran')
    keterangan = fields.Text(related='jenis_pelanggaran.keterangan', string='Keterangan')
    product_id = fields.Many2one('product.template', 'Product', domain=[('is_liter', '=', 'true')])

    total_harga_estimasi = fields.Float('Total Harga Estimasi', compute='hitung_total_harga_susu')
    total_harga_real = fields.Float('Total Harga Real', compute='hitung_total_harga_susu_real')
    jumlah_hari = fields.Integer('Jumlah Hari', compute='_compute_jumlah_hari', store=False)
    avg_setor = fields.Float('Rata-Rata Setor', compute='hitung_avg_setor')
    periode_id = fields.Many2one('periode.setoran', 'Periode')
    total_sapi = fields.Integer('Total Sapi', compute='_compute_total_sapi', store=True)
    produktifitas = fields.Float('Produktifitas', compute='_compute_produktifitas')
    krit_prod = fields.Selection([
        ('1', 'Tidak Setor'),
        ('2', 'Produktifitas <=5'),
        ('3', 'Produktifitas <=10'),
        ('4', 'Produktifitas <=15'),
        ('5', 'Produktifitas <=20'),
        ('6', 'Produktifitas <=25'),
        ('7', 'Produktifitas >25'),
    ], string='Kriteria Produksi')
    qty_po = fields.Float('Qty PO', compute='_compute_qty_po', store=False)
    tot_setoran_pagi_date = fields.Float('Total Setoran Pagi Date', compute='_compute_total_setoran_pagi_date')
    tot_setoran_sore_date = fields.Float('Total Setoran Sore Date', compute='_compute_total_setoran_sore_date')
    tot_setoran_pagi_sore_date = fields.Float('Total', compute='_compute_total_setoran_date')
    sum_bj_pagi_date = fields.Float('Total BJ Pagi', compute='_compute_sum_bj_pagi_date', digits=(1, 4))
    sum_bj_sore_date = fields.Float('Total BJ Sore', compute='_compute_sum_bj_sore_date', digits=(1, 4))
    avg_bj_pagi = fields.Float('Rata-Rata BJ Pagi', compute='_compute_avg_bj_pagi', digits=(1, 4))
    avg_bj_sore = fields.Float('Rata-Rata BJ Sore', compute='_compute_avg_bj_sore', digits=(1, 4))
    tot_rata_rata_bj = fields.Float('Total Rata-Rata BJ',compute='_compute_tot_rata_rata_bj', digits=(1, 4))
    avg_bj_pagi_sore = fields.Float('Rata-Rata BJ Pagi Sore', compute='_compute_avg_bj_pagi_sore', digits=(1, 4))
    avg_bj_harian = fields.Float('Rata-Rata BJ Per Hari', compute='_compute_avg_bj_harian', digits=(1, 4))
    bj_id = fields.Many2one('tabel.bj.fat', 'BJ', compute='_compute_bj_id', store=True, readonly=False)
    is_mitra = fields.Boolean('Mitra?', default=False)

    fat_mitra = fields.Float('FAT')
    ts_mitra = fields.Float('TS')
    pro_mitra = fields.Float('Pro')
    tpc_kan_mitra = fields.Float('TPC KAN')

    setoran_mitra = fields.Float('Total Setoran Susu Mitra (KG)')

    fat_master = fields.Float('FAT Master')
    fat_dasar = fields.Float('FAT Dasar')
    pro_master = fields.Float('Pro Master')
    pro_dasar = fields.Float('Pro Dasar')
    ts_master = fields.Float('TS Master')
    ts_dasar = fields.Float('TS Dasar')
    transport = fields.Float('Transport', related='peternak_id.transport')
    daya_saing = fields.Float('Daya Saing', related='peternak_id.daya_saing')
    pakan = fields.Float('Pakan', related='peternak_id.pakan')
    develop = fields.Float('Development', related='peternak_id.develop')
    pmk = fields.Float('PMK', related='peternak_id.pmk')
    tot_insen = fields.Float('Total Insentif', related='peternak_id.tot_insen')

    total_fat = fields.Float('Total FAT', compute='_compute_tot_fat')
    total_pro = fields.Float('Total Pro', compute='_compute_tot_pro')
    total_ts = fields.Float('Total TS', compute='_compute_tot_ts')
    # total_tpc = fields.Float('Total TPC', compute='_compute_total_tpc')

    tpc_id = fields.Many2one('tabel.tpc', 'TPC')
    nilai_tpc = fields.Float('Nilai TPC', related='tpc_id.nilai_tpc', store=True)

    insen_prod_mitra_id = fields.Many2one('tabel.insentif.prod', 'Insentf Prod')
    nilai_insen_prod_mitra = fields.Float('Nilai Insentif Prod', related='insen_prod_mitra_id.nilai_insen_prod_mitra')

    is_fat = fields.Boolean('Is Fat?')
    is_ts = fields.Boolean('Is TS?')
    is_pro = fields.Boolean('Is Pro?')

    harga_satuan_mitra = fields.Float('Harga Satuan Mitra', compute='_compute_harga_sautan_mitra')

    jumlah_tes = fields.Float('Jumlah Tes', compute='_compute_jumlah_tes', store=True)
    jumlah_mbrt = fields.Float('Jumlah MBRT', compute='_compute_jumlah_mbrt', readonly=False, store=True)
    avg_mbrt = fields.Float('Avg MBRT', compute='_compute_avg_mbrt', readonly=False, store=True)

    total_harga_susu_selisih = fields.Float('Selisih Harga', compute='_compute_harga_selisih')

    tot_bj_pagi = fields.Float('Total BJ Pagi')
    tot_bj_sore = fields.Float('Total BJ Sore')
    avg_bj = fields.Float('Avg BJ')
    total_harga_susu = fields.Float('Total Harga Susu')
    fat = fields.Float('FAT')
    ts = fields.Float('TS')
    pro = fields.Float('Pro')
    tpc_kan = fields.Float('TPC KAN')
    tpc_ips = fields.Float('TPC IPS')
    mbrt = fields.Float('MBRT')
    grade = fields.Float('Grade')
    nilai_grade = fields.Float('Nilai Grade')
    pres_grade = fields.Float('%Grade')

    
    @api.depends('jumlah_mbrt', 'jumlah_tes')
    def _compute_avg_mbrt(self):
        for record in self:
            if record.jumlah_tes != 0:
                avg_mbrt = record.jumlah_mbrt / record.jumlah_tes
                record.avg_mbrt = avg_mbrt
            else:
                record.avg_mbrt = 0.0

    @api.onchange('avg_mbrt')
    def _onchange_avg_mbrt(self):
        if self.avg_mbrt:
            mbrt = self.env['tabel.mbrt'].search([('value', '<=', self.avg_mbrt)], order='value DESC', limit=1)
            if mbrt:
                self.mbrt_id = mbrt.id
            else:
                self.mbrt_id = False

    @api.depends('setoran_line_ids.mbrt_id')
    def _compute_jumlah_mbrt(self):
        for record in self:
            record.jumlah_mbrt = sum(line.mbrt_id.value for line in record.setoran_line_ids if line.is_mbrt)

    @api.depends('setoran_line_ids.is_mbrt')
    def _compute_jumlah_tes(self):
        for record in self:
            record.jumlah_tes = sum(1 for line in record.setoran_line_ids if line.is_mbrt)

    @api.onchange('peternak_id')
    def onchange_peternak_id(self):
        if self.peternak_id:
            self.ts_master = self.peternak_id.ts_master
            self.ts_dasar = self.peternak_id.ts_dasar
            self.fat_master = self.peternak_id.fat_master
            self.fat_dasar = self.peternak_id.fat_dasar
            self.pro_master = self.peternak_id.pro_master
            self.pro_dasar = self.peternak_id.pro_dasar


    @api.depends('total_fat', 'total_pro', 'total_ts', 'nilai_tpc', 'tot_insen', 'nilai_insen_prod_mitra')
    def _compute_harga_sautan_mitra(self):
        for record in self:
            harga_satuan_mitra = record.total_fat + record.total_pro + record.total_ts + record.nilai_tpc + record.tot_insen + record.nilai_insen_prod_mitra
            record.harga_satuan_mitra = harga_satuan_mitra

    @api.onchange('setoran', 'peternak_id')
    def _onchange_setoran_insentif(self):
        for record in self:
            if record.setoran and record.peternak_id:
                insen_prod = record.setoran
                # Mencari nilai Setoran yang sesuai berdasarkan range nilai_min, nilai_max, dan peternak_id
                insen = self.env['tabel.insentif.prod'].search([
                    ('peternak_id', '=', record.peternak_id.id),
                    ('nilai_min', '<=', insen_prod),
                    ('nilai_max', '>=', insen_prod),
                    ('is_active', '=', True)
                ], limit=1)
                if insen:
                    record.insen_prod_mitra_id = insen.id

    @api.onchange('tpc_kan_mitra', 'peternak_id')
    def _onchange_tpc_kan_mitra(self):
        for record in self:
            if record.tpc_kan_mitra and record.peternak_id:
                tpc_kan = record.tpc_kan_mitra
                # Mencari nilai TPC yang sesuai berdasarkan range nilai_min, nilai_max, dan peternak_id
                tpc = self.env['tabel.tpc'].search([
                    ('peternak_id', '=', record.peternak_id.id),
                    ('nilai_min', '<=', tpc_kan),
                    ('nilai_max', '>=', tpc_kan),
                    ('is_active', '=', True)
                ], limit=1)
                if tpc:
                    record.tpc_id = tpc.id

    @api.depends('fat_mitra', 'fat_master', 'fat_dasar')
    def _compute_tot_fat(self):
        for record in self:
            total_fat = (record.fat_mitra * 10 * record.fat_master) + record.fat_dasar
            record.total_fat = total_fat

    @api.depends('pro_mitra', 'pro_master', 'pro_dasar')
    def _compute_tot_pro(self):
        for record in self:
            total_pro = (record.pro_mitra * 10 * record.pro_master) + record.pro_dasar
            record.total_pro = total_pro

    @api.depends('ts_mitra', 'ts_master', 'ts_dasar')
    def _compute_tot_ts(self):
        for record in self:
            total_ts = (record.ts_mitra * 10 * record.ts_master) + record.ts_dasar
            record.total_ts = total_ts

    @api.depends('peternak_id.tipe_mitra')
    def _compute_insen_daya_saing(self):
        for record in self:
            if record.peternak_id.tipe_mitra == '1':
                record.insen_daya_saing = 0
            else:
                record.insen_daya_saing = 200

    @api.depends('total_purchase', 'total_harga_real')
    def _compute_harga_selisih(self):
        for record in self:
            total_harga_susu_selisih = record.total_purchase - record.total_harga_real
            record.total_harga_susu_selisih = total_harga_susu_selisih

    @api.depends('harga_satuan', 'harga_real')
    def _compute_harga_selish(self):
        for record in self:
            harga_susu_selisih = record.harga_real - record.harga_satuan
            record.harga_selisih = harga_susu_selisih

    @api.onchange('mbrt_id')
    def _onchange_mbrt_id(self):
        if self.mbrt_id:
            range_mbrt = self.env['tabel.range.mbrt'].search([('mbrt_id', '=', self.mbrt_id.id)], limit=1)
            if range_mbrt:
                self.grade_id = range_mbrt.grade_id.id
            else:
                # Atur nilai default atau tindakan lain sesuai kebutuhan Anda
                self.grade_id = False

    @api.depends('avg_bj_harian')
    def _compute_bj_id(self):
        for sapi in self:
            # Ambil nilai dari tabel_bj_fat berdasarkan kriteria tertentu, misalnya rata-rata BJ harian tertentu
            nilai_bj = self.env['tabel.bj.fat'].search([('nilai', '=', sapi.avg_bj_harian)], limit=1)

            # Isi field bj_id pada liter_sapi dengan nilai yang telah ditemukan
            sapi.bj_id = nilai_bj

    @api.depends('setoran_line_date_ids.tot_bj', 'setoran_line_date_ids.tgl_setor')
    def _compute_avg_bj_harian(self):
        for liter_sapi_rec in self:
            # Dapatkan setoran lines yang terkait dengan liter_sapi_rec
            setoran_lines = liter_sapi_rec.setoran_line_date_ids

            # Dictionary untuk menyimpan tot_bj berdasarkan tgl_setor
            tot_bj_dict = {}

            # Ambil nilai tot_bj sesuai dengan tanggal setoran terupdate
            for setoran_line in setoran_lines:
                tgl_setor = setoran_line.tgl_setor
                tot_bj_dict[tgl_setor] = setoran_line.tot_bj

            # Set nilai avg_bj_harian pada liter_sapi_rec
            avg_bj = tot_bj_dict.get(max(tot_bj_dict.keys(), default=None), 0.0)

            # Pembulatan sesuai dengan aturan yang diinginkan (ke kelipatan 0.005)
            rounded_avg_bj = round(avg_bj / 0.0005) * 0.0005

            liter_sapi_rec.avg_bj_harian = rounded_avg_bj

    @api.depends('nilai_grade', 'ts')
    def _compute_harga_kual(self):
        for record in self:
            harga_kual = (record.nilai_grade / 12) * record.ts
            record.harga_kual = harga_kual

    @api.depends('setoran_line_date_ids.tot_bj')
    def _compute_tot_rata_rata_bj(self):
        for record in self:
            tot_rata_rata_bj = sum(line.tot_bj for line in record.setoran_line_date_ids)
            record.tot_rata_rata_bj = tot_rata_rata_bj

    @api.depends('avg_bj_pagi', 'avg_bj_sore', 'tot_setoran_pagi_date', 'tot_setoran_sore_date',
                 'tot_setoran_pagi_sore_date')
    def _compute_avg_bj_pagi_sore(self):
        for record in self:
            if (record.tot_setoran_pagi_date + record.tot_setoran_sore_date) != 0:
                avg_bj_pagi_sore = (record.avg_bj_pagi * record.tot_setoran_pagi_date + record.tot_setoran_sore_date
                                    * record.avg_bj_sore) / (record.tot_setoran_pagi_date + record.tot_setoran_sore_date)
                record.avg_bj_pagi_sore = avg_bj_pagi_sore
            else:
                record.avg_bj_pagi_sore = 0  # Atau nilai default lain sesuai kebutuhan

    @api.depends('sum_bj_pagi_date', 'tot_setoran_pagi_date')
    def _compute_avg_bj_pagi(self):
        for record in self:
            if record.tot_setoran_pagi_date != 0:
                avg_bj_pagi = (record.sum_bj_pagi_date + record.tot_setoran_pagi_date) / record.tot_setoran_pagi_date
                record.avg_bj_pagi = avg_bj_pagi
            else:
                record.avg_bj_pagi = 0  # Atau nilai default lain sesuai kebutuhan

    @api.depends('sum_bj_sore_date', 'tot_setoran_sore_date')
    def _compute_avg_bj_sore(self):
        for record in self:
            if record.tot_setoran_sore_date != 0:
                avg_bj_sore = (record.sum_bj_sore_date + record.tot_setoran_sore_date) / record.tot_setoran_sore_date
                record.avg_bj_sore = avg_bj_sore
            else:
                record.avg_bj_sore = 0

    @api.depends('setoran_line_date_ids.bj_pagi')
    def _compute_sum_bj_pagi_date(self):
        for record in self:
            sum_bj_pagi_date = sum(line.bj_pagi for line in record.setoran_line_date_ids)
            record.sum_bj_pagi_date = sum_bj_pagi_date

    @api.depends('setoran_line_date_ids.bj_sore')
    def _compute_sum_bj_sore_date(self):
        for record in self:
            sum_bj_sore_date = sum(line.bj_sore for line in record.setoran_line_date_ids)
            record.sum_bj_sore_date = sum_bj_sore_date

    # @api.onchange('peternak_id')
    # def _onchange_peternak_id(self):
    #     if self.peternak_id:
    #         # Memanggil metode default_get hanya jika peternak_id sudah diisi
    #         defaults = self.default_get([])

            # Mengisi nilai-nilai default ke dalam objek self
            # if 'fat_id' in defaults and not self.fat_id:
            #     self.fat_id = defaults['fat_id']
            # if 'tpc_kan_id' in defaults and not self.tpc_kan_id:
            #     self.tpc_kan_id = defaults['tpc_kan_id']
            # if 'mbrt_id' in defaults and not self.mbrt_id:
            #     self.mbrt_id = defaults['mbrt_id']
        # else:
            # Jika peternak_id belum diisi, atur nilai-nilai default menjadi False
            # self.fat_id = False
            # self.tpc_kan_id = False
            # self.mbrt_id = False

    # @api.model
    def default_get(self, fields):
        defaults = super(liter_sapi, self).default_get(fields)

        # Cari record tabel.fat yang memiliki is_default = True
        default_fat = self.env['tabel.fat'].search([('is_default', '=', True)], limit=1)
        if default_fat:
            defaults['fat_id'] = default_fat.id

        # Cari record tabel.tpc yang memiliki is_default = True
        default_tpc_kan = self.env['tabel.tpc'].search([('is_default', '=', True)], limit=1)
        if default_tpc_kan:
            defaults['tpc_kan_id'] = default_tpc_kan.id

        # Jika peternak_id sudah diisi, cari record tabel.mbrt yang memiliki is_default = True
        # berdasarkan nilai peternak_id yang baru diisi
        default_mbrt = self.env['tabel.mbrt'].search([('is_default', '=', True)], limit=1)
        if default_mbrt:
            defaults['mbrt_id'] = default_mbrt.id

        default_product = self.env['product.template'].search([('is_liter', '=', True)], limit=1)
        if default_product:
            defaults['product_id'] = default_product.id

        return defaults

    @api.depends('fat_id', 'bj_id')
    def _compute_ts(self):
        for sapi in self:
            if sapi.fat_id and sapi.bj_id:
                # Cari nilai ts pada tabel_ts berdasarkan fat_id dan bj_id
                tabel_ts_record = self.env['tabel.ts'].search([
                    ('fat_id', '=', sapi.fat_id.id),
                    ('bj_id', '=', sapi.bj_id.id)
                ], limit=1)

                if tabel_ts_record:
                    sapi.ts = tabel_ts_record.ts
                else:
                    # Set ts menjadi 0 jika tidak ada record yang sesuai
                    sapi.ts = 0.0

    @api.depends('setoran_line_ids.setoran_pagi', 'setoran_line_ids.setoran_sore')
    def _compute_qty_po(self):
        for sapi in self:
            qty_po = 0.0
            for line in sapi.setoran_line_ids:
                if line.is_po == False :
                    qty_po += line.setoran_pagi + line.setoran_sore

            sapi.qty_po = qty_po

    @api.onchange('produktifitas')
    def _onchange_produktifitas(self):
        if self.produktifitas == 0.0:
            self.krit_prod = '1'
        elif 1.0 <= self.produktifitas <= 5.0:
            self.krit_prod = '2'
        elif 6.0 <= self.produktifitas <= 10.0:
            self.krit_prod = '3'
        elif 11.0 <= self.produktifitas <= 15.0:
            self.krit_prod = '4'
        elif 16.0 <= self.produktifitas <= 20.0:
            self.krit_prod = '5'
        elif 21.0 <= self.produktifitas <= 25.0:
            self.krit_prod = '6'
        elif self.produktifitas > 25.0:
            self.krit_prod = '7'

    @api.depends('total_sapi', 'avg_setor')
    def _compute_produktifitas(self):
        for record in self:
            if record.total_sapi == 0:
                record.produktifitas = 0.0  # Menangani pembagian oleh nol
            else:
                record.produktifitas = record.avg_setor / record.total_sapi

    @api.depends('sapi_ids')
    def _compute_total_sapi(self):
        for record in self:
            # Menghitung jumlah sapi_ids yang terisi
            record.total_sapi = len(record.sapi_ids)

    @api.depends('tgl_awal', 'tgl_akhir')
    def _compute_jumlah_hari(self):
        for record in self:
            if record.tgl_awal and record.tgl_akhir:
                tgl_awal = fields.Date.from_string(record.tgl_awal)
                tgl_akhir = fields.Date.from_string(record.tgl_akhir)
                jumlah_hari = (tgl_akhir - tgl_awal).days + 1
                record.jumlah_hari = jumlah_hari
            else:
                record.jumlah_hari = 0

    @api.onchange('periode_id')
    def _onchange_periode(self):
        if self.periode_id:
            self.tgl_awal = self.periode_id.periode_setoran_awal
            self.tgl_akhir = self.periode_id.periode_setoran_akhir

    def mass_create_po(self):
        setoran_lines_to_update = self.env['setoran.line']
        for sapi_record in self:
            for setoran_line in sapi_record.setoran_line_ids:
                setoran_lines_to_update += setoran_line
        setoran_lines_to_update.write({'is_po': True})
        return {'type': 'ir.actions.act_window_close'}

    def create_po(self):
        purchase_order_obj = self.env['purchase.order']
        purchase_order_line_obj = self.env['purchase.order.line']

        for liter in self:
            product = self.env['product.product'].search([('product_tmpl_id', '=', liter.product_id.id)])

            vals = {
                'partner_id': liter.peternak_id.partner_id.id,
                'date_order': datetime.now(),
                'state': 'draft',
                'setoran_id': liter.id
            }

            purchase_order = purchase_order_obj.create(vals)

            po_line_vals = {
                'product_id': product.id,
                'product_qty': liter.qty_po,
                'name': product.name,
                'price_unit': liter.harga_satuan,
                'date_planned': datetime.now(),
                'product_uom': product.uom_po_id.id,
                'order_id': purchase_order.id,
            }

            purchase_order_line = purchase_order_line_obj.create(po_line_vals)
            # Set is_po to True for relevant setoran_line_ids
            liter.setoran_line_ids.write({'is_po': True})

            # Set is_po to True for relevant setoran_line_date_ids
            liter.setoran_line_date_ids.write({'is_po': True})

    # @api.depends('setoran_line_ids')
    # def _compute_jumlah_hari(self):
    #     for record in self:
    #         record.jumlah_hari = len(record.setoran_line_ids)

    @api.depends('insen_pmk', 'avg_setor', 'peternak_id.tipe_mitra')
    def jumlah_insen_pmk(self):
        for record in self:
            if record.peternak_id.tipe_mitra == '1':
                # Jika tipe_mitra adalah '1', maka insen_pmk diatur menjadi 0
                record.insen_pmk = 0
            else:
                # Jika tipe_mitra bukan '1', lakukan perhitungan seperti sebelumnya
                if record.avg_setor >= 1 and record.setoran_l <= 20:
                    record.insen_pmk = 600
                elif record.avg_setor > 20:
                    record.insen_pmk = 500
                else:
                    record.insen_pmk = 0

    @api.depends('setoran_l', 'jumlah_hari')
    def hitung_avg_setor(self):
        for record in self:
            if record.jumlah_hari != 0:  # Menambahkan pengecekan apakah jumlah hari tidak sama dengan nol
                if record.setoran != 0:
                    record.avg_setor = record.setoran_l / record.jumlah_hari
                else:
                    record.avg_setor = 0
            else:
                record.avg_setor = 0  # Mengatasi pembagian oleh nol dengan mengatur avg_setor menjadi 0

    @api.depends('avg_setor', 'peternak_id.tipe_mitra')
    def jumlah_insen_prod(self):
        for record in self:
            if record.peternak_id.tipe_mitra == '1':
                # Jika tipe_mitra adalah '1', maka insen_pmk diatur menjadi 0
                record.insen_prod = 0
            else:
                # Jika tipe_mitra bukan '1', lakukan perhitungan seperti sebelumnya
                if record.avg_setor >= 1 and record.avg_setor <= 20:
                    record.insen_prod = 1300
                elif record.avg_setor >= 21 and record.avg_setor <= 30:
                    record.insen_prod = 1340
                elif record.avg_setor >= 31 and record.avg_setor <= 50:
                    record.insen_prod = 1405
                elif record.avg_setor >= 51 and record.avg_setor <= 100:
                    record.insen_prod = 1470
                elif record.avg_setor > 101:
                    record.insen_prod = 1560
                else:
                    record.insen_prod = 0

    # @api.depends('setoran_line_ids.berat_setoran_pagi')
    # def _compute_setoran_pagi(self):
    #     for record in self:
    #         total_setoran_pagi = sum(setoran_pagi.berat_setoran for setoran_pagi in record.setoran_line_ids)
    #         record.setoran_pagi = total_setoran_pagi
    #
    # @api.depends('setoran_line_ids.berat_setoran_sore')
    # def _compute_setoran_sore(self):
    #     for record in self:
    #         total_setoran_sore = sum(setoran_sore.berat_setoran for setoran_sore in record.setoran_line_ids)
    #         record.setoran_sore = total_setoran_sore

    @api.depends('setoran_line_ids.setoran_pagi', 'setoran_line_ids.alkohol_pagi', 'setoran_line_ids.organol_pagi', 'setoran_line_ids.is_cancel_pagi')
    def _compute_total_setoran_pagi(self):
        for record in self:
            total_setoran_pagi = sum(line.setoran_pagi for line in record.setoran_line_ids if
                                     line.alkohol_pagi == '1' and line.organol_pagi == '1' and not line.is_cancel_pagi)
            record.total_setoran_pagi = total_setoran_pagi

    @api.depends('setoran_line_date_ids.setoran_pagi')
    def _compute_total_setoran_pagi_date(self):
        for record in self:
            total_setoran_pagi_date = sum(line.setoran_pagi for line in record.setoran_line_date_ids)
            record.tot_setoran_pagi_date = total_setoran_pagi_date

    @api.depends('setoran_line_ids.setoran_sore', 'setoran_line_ids.alkohol_sore', 'setoran_line_ids.organol_sore', 'setoran_line_ids.is_cancel_sore')
    def _compute_total_setoran_sore(self):
        for record in self:
            total_setoran_sore = sum(line.setoran_sore for line in record.setoran_line_ids if
                                     line.alkohol_sore == '1' and line.organol_sore == '1' and not line.is_cancel_sore)
            record.total_setoran_sore = total_setoran_sore

    @api.depends('setoran_line_date_ids.setoran_sore')
    def _compute_total_setoran_sore_date(self):
        for record in self:
            total_setoran_sore_date = sum(line.setoran_sore for line in record.setoran_line_date_ids)
            record.tot_setoran_sore_date = total_setoran_sore_date

    @api.depends('setoran_line_ids.setoran_pagi_l', 'setoran_line_ids.alkohol_pagi', 'setoran_line_ids.organol_pagi', 'setoran_line_ids.is_cancel_pagi')
    def _compute_total_setoran_pagi_l(self):
        for record in self:
            total_setoran_pagi_l = sum(line.setoran_pagi_l for line in record.setoran_line_ids if
                                     line.alkohol_pagi == '1' and line.organol_pagi == '1' and not line.is_cancel_pagi)
            record.total_setoran_pagi_l = total_setoran_pagi_l

    @api.depends('setoran_line_ids.setoran_sore_l', 'setoran_line_ids.alkohol_sore', 'setoran_line_ids.organol_sore', 'setoran_line_ids.is_cancel_sore')
    def _compute_total_setoran_sore_l(self):
        for record in self:
            total_setoran_sore_l = sum(line.setoran_sore_l for line in record.setoran_line_ids if
                                     line.alkohol_sore == '1' and line.organol_sore == '1' and not line.is_cancel_sore)
            record.total_setoran_sore_l = total_setoran_sore_l

    @api.depends('total_setoran_pagi', 'total_setoran_sore')
    def _compute_total_setoran(self):
        for record in self:
            total_setoran = record.total_setoran_pagi + record.total_setoran_sore
            record.setoran = total_setoran

    @api.depends('tot_setoran_pagi_date', 'tot_setoran_sore_date')
    def _compute_total_setoran_date(self):
        for record in self:
            total_setoran_date = record.tot_setoran_pagi_date + record.tot_setoran_sore_date
            record.tot_setoran_pagi_sore_date = total_setoran_date

    @api.depends('total_setoran_pagi_l', 'total_setoran_sore_l')
    def _compute_total_setoran_l(self):
        for record in self:
            total_setoran_l = record.total_setoran_pagi_l + record.total_setoran_sore_l
            record.setoran_l = total_setoran_l

    @api.onchange('peternak_id')
    def _onchange_peternak_id(self):
        if self.peternak_id:
            # Perbarui sapi_ids ketika peternak_id berubah
            self.sapi_ids = self.env['sapi'].search(
                [('peternak_id', '=', self.peternak_id.id), ('state', '=', 'laktasi')]
            )
        else:
            # Kosongkan sapi_ids ketika peternak_id tidak dipilih
            self.sapi_ids = [(5, 0, 0)]

    @api.constrains('tgl_awal', 'tgl_akhir')
    def _check_dates(self):
        for period in self:
            if period.tgl_awal > period.tgl_akhir:
                raise models.ValidationError("Tanggal Awal Harus Sebelum Tanggal Akhir!")

    @api.depends('setoran', 'harga_satuan')
    def hitung_total_harga_susu(self):
        for record in self:
            if record.setoran != 0:
                record.total_harga_estimasi = record.setoran * record.harga_satuan
            else:
                record.total_harga_estimasi = 0

    @api.depends('setoran', 'harga_real')
    def hitung_total_harga_susu_real(self):
        for record in self:
            if record.setoran != 0:
                record.total_harga_real = record.setoran * record.harga_satuan
            else:
                record.total_harga_real = 0

    @api.depends('setoran', 'harga_selisih')
    def hitung_total_harga_susu_selisih(self):
        for record in self:
            if record.setoran != 0:
                record.total_harga_selisih = record.setoran * record.harga_selisih
            else:
                record.total_harga_selisih = 0

    @api.depends('harga_kual', 'insen_prod', 'insen_pmk', 'insen_daya_saing')
    def hitung_jumlah_harga_satuan(self):
        for record in self:
            record.harga_satuan = record.harga_kual + record.insen_prod + record.insen_pmk + record.insen_daya_saing

    def get_purchase(self):
        action = self.env.ref('purchase.'
                              'purchase_form_action').read()[0]
        action['domain'] = [('setoran_id', 'in', self.ids)]
        return action

    def compute_purchase_count(self):
        for record in self:
            record.purchase_count = self.env['purchase.order'].search_count(
                [('setoran_id', 'in', self.ids)])

    purchase_order_ids = fields.One2many('purchase.order', 'setoran_id', string='Purchase Line')
    setoran_line_ids = fields.One2many('setoran.line', 'liter_sapi_id', string='Setoran Line Ids')
    setoran_line_date_ids = fields.One2many('setoran.line.date', 'liter_sapi_date_id', string='Setoran Line Date Ids')

    total_purchase = fields.Float(string='Total PO', compute='_compute_total_po', store=True)

    @api.depends('purchase_order_ids.amount_total')
    def _compute_total_po(self):
        for record in self:
            total_purchase = sum(order.amount_total for order in record.purchase_order_ids)
            record.total_purchase = total_purchase

    def merge_setoran_line(self):
        merged_lines = defaultdict(
            lambda: {'setoran_pagi_l': 0.0, 'setoran_pagi': 0.0, 'setoran_sore_l': 0.0, 'setoran_sore': 0.0,
                     'bj_pagi': 0.0, 'bj_sore': 0.0, 'tipe_setor_pagi': False, 'tipe_setor_sore': False})

        # Membuat dictionary untuk menghitung kemunculan nilai bj_sore dan bj_pagi untuk setiap tanggal
        bj_sore_counts = defaultdict(lambda: defaultdict(int))
        bj_pagi_counts = defaultdict(lambda: defaultdict(int))

        # Loop setiap setoran_line
        for setoran_line in self.setoran_line_ids:
            key = (
                setoran_line.tgl_setor,
            )

            # Tambahkan kondisi untuk alkohol_pagi, organol_pagi, dan is_cancel_pagi
            if (
                    key not in merged_lines and
                    setoran_line.alkohol_pagi != '2' and
                    setoran_line.organol_pagi != '2' and
                    not setoran_line.is_cancel_pagi and
                    setoran_line.alkohol_sore != '2' and  # Kondisi untuk alkohol_sore
                    setoran_line.organol_sore != '2' and  # Kondisi untuk organol_sore
                    not setoran_line.is_cancel_sore
            ):
                merged_lines[key] = setoran_line.read()[0]
                merged_lines[key]['setoran_pagi_l'] = setoran_line.setoran_pagi_l
                merged_lines[key]['setoran_pagi'] = setoran_line.setoran_pagi
                merged_lines[key]['setoran_sore_l'] = setoran_line.setoran_sore_l
                merged_lines[key]['setoran_sore'] = setoran_line.setoran_sore
                merged_lines[key]['bj_pagi'] = setoran_line.bj_pagi if setoran_line.bj_pagi > 0 else 0.0
                merged_lines[key]['bj_sore'] = setoran_line.bj_sore if setoran_line.bj_sore > 0 else 0.0
                merged_lines[key]['tipe_setor_pagi'] = setoran_line.tipe_setor_pagi
                merged_lines[key]['tipe_setor_sore'] = setoran_line.tipe_setor_sore
                merged_lines[key]['mbrt_id'] = setoran_line.mbrt_id
                merged_lines[key]['is_mbrt'] = setoran_line.is_mbrt
            elif (
                    key in merged_lines and
                    setoran_line.alkohol_pagi != '2' and
                    setoran_line.organol_pagi != '2' and
                    not setoran_line.is_cancel_pagi and
                    setoran_line.alkohol_sore != '2' and  # Kondisi untuk alkohol_sore
                    setoran_line.organol_sore != '2' and  # Kondisi untuk organol_sore
                    not setoran_line.is_cancel_sore
            ):
                # Akumulasi nilai setoran_pagi_l jika key sudah ada
                merged_lines[key]['setoran_pagi_l'] += setoran_line.setoran_pagi_l
                merged_lines[key]['setoran_pagi'] += setoran_line.setoran_pagi
                merged_lines[key]['setoran_sore_l'] += setoran_line.setoran_sore_l
                merged_lines[key]['setoran_sore'] += setoran_line.setoran_sore
                merged_lines[key]['tipe_setor_pagi'] = setoran_line.tipe_setor_pagi
                merged_lines[key]['tipe_setor_sore'] = setoran_line.tipe_setor_sore

                # Hitung kemunculan nilai bj_sore dan bj_pagi untuk setiap tanggal
                bj_sore_counts[key][setoran_line.bj_sore] += 1 if setoran_line.bj_sore > 0 else 0
                bj_pagi_counts[key][setoran_line.bj_pagi] += 1 if setoran_line.bj_pagi > 0 else 0

        # Ambil nilai bj_sore yang paling banyak muncul untuk setiap tanggal
        for date_key, bj_sore_count in bj_sore_counts.items():
            merged_lines[date_key]['bj_sore'] = max(bj_sore_count, key=bj_sore_count.get)

        # Ambil nilai bj_pagi yang paling banyak muncul untuk setiap tanggal
        for date_key, bj_pagi_count in bj_pagi_counts.items():
            merged_lines[date_key]['bj_pagi'] = max(bj_pagi_count, key=bj_pagi_count.get)

        # Hapus semua setoran_line_date_ids yang terkait
        self.setoran_line_date_ids.unlink()

        # Buat kembali setoran_line_date_ids dari merged_lines
        for key, values in merged_lines.items():
            mbrt_id = values.get('mbrt_id')
            if mbrt_id:
                mbrt_id = mbrt_id.id  # Ambil ID mbrt_id dari objek mbrt
            self.env['setoran.line.date'].create({
                'liter_sapi_date_id': self.id,
                'tgl_setor': values['tgl_setor'],
                'bj_pagi': values['bj_pagi'],
                'bj_sore': values['bj_sore'],
                'tipe_setor_pagi': values['tipe_setor_pagi'],
                'tipe_setor_sore': values['tipe_setor_sore'],
                'setoran_pagi_l': values['setoran_pagi_l'],
                'setoran_pagi': values['setoran_pagi'],
                'setoran_sore_l': values['setoran_sore_l'],
                'setoran_sore': values['setoran_sore'],
                'mbrt_id': mbrt_id,
                'is_mbrt': values['is_mbrt'],
                # Tambahkan field lainnya sesuai kebutuhan
            })

        return True

    @api.model
    def create(self, values):
        # Panggil metode create dari kelas induk
        record = super(liter_sapi, self).create(values)

        # Jalankan merge_setoran_line secara otomatis
        record.merge_setoran_line()

        return record

    def write(self, values):
        # Panggil fungsi write dari parent class
        result = super(liter_sapi, self).write(values)

        # Jalankan merge_setoran_line secara otomatis
        self.merge_setoran_line()

        return result

    @api.onchange('mbrt_id')
    def _onchange_mbrt_id_line(self):
        if self.mbrt_id:
            for line in self.setoran_line_ids:
                line.mbrt_id = self.mbrt_id

class purchase(models.Model):
    _inherit = "purchase.order"

    setoran_id = fields.Many2one('liter.sapi', 'Setoran')
    bj = fields.Integer('BJ')
    # bj_pagi = fields.Integer('BJ Pagi')
    # bj_sore = fields.Integer('BJ Sore')
    grade = fields.Char('Grade')

class SetoranLine(models.Model):
    _name = 'setoran.line'
    _description = 'Setoran Line'


    def _default_uom_id(self):
        uom_kg = self.env['uom.uom'].search([('name', '=', 'kg')], limit=1)
        return uom_kg

    liter_sapi_id = fields.Many2one('liter.sapi', 'Liter Sapi Id')
    setoran_pagi = fields.Float('Setoran Pagi (KG)')
    setoran_sore = fields.Float('Setoran Sore (KG)')
    setoran_pagi_l = fields.Float('Setoran Pagi (L)')
    setoran_sore_l = fields.Float('Setoran Sore (L)')
    uom_id = fields.Many2one('uom.uom', 'Uom')
    tps_id = fields.Many2one('tps.liter', string='TPS', related='liter_sapi_id.tps_id', store=True)
    peternak_id = fields.Many2one('peternak.sapi', 'Peternak', related='liter_sapi_id.peternak_id', store=True)
    # harga_total = fields.Float('Total Harga', compute='hitung_jumlah_harga')
    # total_harga_susu = fields.Float('Total Harga Susu', compute='hitung_total_harga_susu')
    # harga_kual = fields.Float('Harga Kualitas', compute='hitung_harga_kualitas')
    # grade = fields.Float('Grade', compute='jumlah_grade')
    # ts = fields.Float('TS')
    # insen_prod = fields.Float('Ins Produksi')
    # insen_ef = fields.Float('Ins Efesiensi')
    tgl_setor = fields.Date('Tanggal Setor')
    tipe_setor_pagi = fields.Selection([
        ('0', ''),
        ('1', 'Pagi'),
        ('2', 'Sore')
    ], 'Tipe Setor', required=False)
    bj_pagi = fields.Float('BJ Pagi', digits=(1, 4))
    tipe_setor_sore = fields.Selection([
        ('0', ''),
        ('1', 'Pagi'),
        ('2', 'Sore')
    ], 'Tipe Setor', required=False, default='2')
    bj_sore = fields.Float('BJ Sore', digits=(1, 4))
    bj = fields.Float('BJ')
    note = fields.Char('Note')
    alkohol_pagi = fields.Selection([
        ('1', 'OK'),
        ('2', 'NOT OK'),
    ], 'Alkohol Pagi')
    organol_pagi = fields.Selection([
        ('1', 'OK'),
        ('2', 'NOT OK'),
    ], 'Organoleptik Pagi')
    alkohol_sore = fields.Selection([
        ('1', 'OK'),
        ('2', 'NOT OK'),
    ], 'Alkohol Sore')
    organol_sore = fields.Selection([
        ('1', 'OK'),
        ('2', 'NOT OK'),
    ], 'Organoleptik Sore')
    is_cancel_pagi = fields.Boolean('Cancel', default=False)
    is_cancel_sore = fields.Boolean('Cancel', default=False)
    is_po = fields.Boolean('Is PO?', default=False)
    # petugas_id = fields.Many2one('medical.physician', 'Petugas')
    # total_line_harga_susu = fields.Float('Subtotal', compute='_compute_total_line_harga_susu')
    #
    # @api.depends('setoran.line')
    # def _compute_total_line_harga_susu(self):
    #     for record in self:
    #         record.total_line_harga_susu = sum(line.total_harga_susu for line in record)

    # @api.onchange('tgl_setor')
    # def _onchange_tgl_setor(self):
    #     if self.tgl_setor:
    #         hour = fields.Datetime.from_string(self.tgl_setor).hour
    #         if 6 <= hour < 12:
    #             self.tipe_setor = '2'  # Pagi
    #         elif 12 <= hour < 17:
    #             self.tipe_setor = '1'  # Sore

    # @api.onchange('ts')
    # def _onchange_ts(self):
    #     if self.ts:
    #         # Lakukan tindakan yang sesuai untuk mengisi field "ts" di model "setoran.line"
    #         # Misalnya, lakukan sesuatu dengan nilai self.ts
    #         # self.ts = ...
    #         pass

    # @api.depends('harga_kual', 'insen_prod', 'insen_ef')
    # def hitung_jumlah_harga(self):
    #     for record in self:
    #         record.harga_total = record.harga_kual + record.insen_prod + record.insen_ef

    # @api.depends('setoran', 'harga_total')
    # def hitung_total_harga_susu(self):
    #     for record in self:
    #         if record.setoran != 0:
    #             record.total_harga_susu = record.setoran * record.harga_total
    #         else:
    #             record.total_harga_susu = 0

    # @api.depends('grade', 'ts')
    # def hitung_harga_kualitas(self):
    #     for record in self:
    #         if record.grade == 1:
    #             grade_value = 4343
    #         elif record.grade == 1.5:
    #             grade_value = 4293
    #         elif record.grade == 2:
    #             grade_value = 4243
    #         elif record.grade == 2.5:
    #             grade_value = 4193
    #         elif record.grade == 3:
    #             grade_value = 4143
    #         else:
    #             grade_value = 0
    #
    #         if record.ts >= 12:
    #             record.harga_kual = grade_value / 12 * record.ts
    #         else:
    #             record.harga_kual = 0
    mbrt_id = fields.Many2one('tabel.mbrt', 'MBRT')
    is_mbrt = fields.Boolean('Tes MBRT?')

    @api.model
    def create(self, values):
        if 'liter_sapi_id' in values and not values.get('mbrt_id'):
            liter_sapi = self.env['liter.sapi'].browse(values['liter_sapi_id'])
            if liter_sapi.mbrt_id:
                values['mbrt_id'] = liter_sapi.mbrt_id.id
        return super(SetoranLine, self).create(values)



class SetoranLineDate(models.Model):
    _name = 'setoran.line.date'
    _description = 'Setoran Line Date'

    liter_sapi_date_id = fields.Many2one('liter.sapi', 'Liter Sapi Id')
    setoran_pagi = fields.Float('Setoran Pagi (KG)')
    setoran_sore = fields.Float('Setoran Sore (KG)')
    setoran_pagi_l = fields.Float('Setoran Pagi (L)')
    setoran_sore_l = fields.Float('Setoran Sore (L)')
    uom_id = fields.Many2one('uom.uom', 'Uom')
    tps_id = fields.Many2one('tps.liter', string='TPS', related='liter_sapi_date_id.tps_id', store=True)
    peternak_id = fields.Many2one('peternak.sapi', 'Peternak', related='liter_sapi_date_id.peternak_id', store=True)
    tgl_setor = fields.Date('Tanggal Setor')
    tipe_setor_pagi = fields.Selection([
        ('0', ''),
        ('1', 'Pagi'),
        ('2', 'Sore')
    ], 'Tipe Setor', required=False)
    bj_pagi = fields.Float('BJ Pagi', digits=(1, 4))
    tipe_setor_sore = fields.Selection([
        ('0', ''),
        ('1', 'Pagi'),
        ('2', 'Sore')
    ], 'Tipe Setor', required=False)
    bj_sore = fields.Float('BJ Sore', digits=(1, 4))
    is_po = fields.Boolean('Is PO?', default=False)
    tot_bj = fields.Float('Total Bj', compute='_compute_tot_bj', digits=(1, 4))
    tot_setoran = fields.Float('Total Setoran', compute='_compute_tot_setoran')
    mbrt_id = fields.Many2one('tabel.mbrt', 'MBRT')
    is_mbrt = fields.Boolean('Tes MBRT?')

    @api.depends('setoran_pagi', 'setoran_sore')
    def _compute_tot_setoran(self):
        for record in self:
            record.tot_setoran = record.setoran_pagi + record.setoran_sore

    @api.depends('bj_pagi', 'setoran_pagi', 'bj_sore', 'setoran_sore', 'tot_setoran')
    def _compute_tot_bj(self):
        for record in self:
            if record.tot_setoran != 0:
                record.tot_bj = (record.bj_pagi * record.setoran_pagi + record.setoran_sore * record.bj_sore) / record.tot_setoran
            else:
                record.tot_bj = 0.0

class tabel_bj(models.Model):
    _name = "tabel.bj"
    _description = "Tabel BJ"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    bj_default_pagi = fields.Integer('BJ Default Pagi')
    bj_default_sore = fields.Integer('BJ Default Sore')

class tabel_bj_fat(models.Model):
    _name = "tabel.bj.fat"
    _description = "Tabel BJ"
    _rec_name = 'nilai'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    nilai = fields.Float('Nilai BJ', digits=(1, 4))

class tabel_ts(models.Model):
    _name = "tabel.ts"
    _description = "Tabel TS"
    _rec_name = 'ts'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    bj_id = fields.Many2one('tabel.bj.fat', 'BJ', digits=(1, 4))
    fat_id = fields.Many2one('tabel.fat', 'FAT')
    ts = fields.Float('TS', digits=(1, 3))
class TabelGrade(models.Model):
    _name = "tabel.grade"
    _description = "Tabel Grade"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Nama Grade')
    nilai = fields.Float('Nilai')
    is_default = fields.Boolean('Default')

# class TabelTpcKan(models.Model):
#     _name = "tabel.tpc.kan"
#     _description = "Tabel TPC Kan"
#     _inherit = ['mail.thread', 'mail.activity.mixin']

    # name = fields.Char('Nama TPC')
    # grade_id = fields.Many2one('tabel.grade', 'Grade')
    # nilai = fields.Float('Nilai', related='grade_id.nilai')
    # is_default = fields.Boolean('Default')
    # nilai_tpc = fields.Float('Nilai TPC')
    # peternak_id = fields.Many2one('peternak.sapi', 'Peternak')
    # tpc_id = fields.Many2one('tabel.tpc', 'TPC')
    # nilai_tpc = fields.Float('Nilai TPC', related='tpc_id.nilai_tpc')

class TabelTPC(models.Model):
    _name = "tabel.tpc"
    _description = "Tabel TPC"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    peternak_id = fields.Many2one('peternak.sapi', 'Peternak')
    name = fields.Char('Nama TPC')
    is_default = fields.Boolean('Default')
    nilai_min = fields.Float('Nilai Min')
    nilai_max = fields.Float('Nilai Max')
    nilai_tpc = fields.Float('Nilai TPC')
    is_active = fields.Boolean('Active')

class TabelInsentifProd(models.Model):
    _name = "tabel.insentif.prod"
    _description = "Tabel Insentif Prod"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    peternak_id = fields.Many2one('peternak.sapi', 'Peternak')
    name = fields.Char('Nama TPC')
    nilai_min = fields.Float('Nilai Min')
    nilai_max = fields.Float('Nilai Max')
    nilai_insen_prod_mitra = fields.Float('Nilai Insentif Prod')
    is_active = fields.Boolean('Active')

class TabelMbrt(models.Model):
    _name = "tabel.mbrt"
    _description = "Tabel MBRT"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Nama MBRT')
    is_default = fields.Boolean('Default')
    is_mitra = fields.Boolean('Mitra')
    value = fields.Float('Nilai')

class TabelRangeMbrt(models.Model):
    _name = "tabel.range.mbrt"
    _description = "Tabel Range MBRT"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'mbrt_id'

    mbrt_id = fields.Many2one('tabel.mbrt', 'MBRT')
    grade_id = fields.Many2one('tabel.grade', 'Grade')
    nilai = fields.Float('Nilai', related='grade_id.nilai')

class TabelFat(models.Model):
    _name = "tabel.fat"
    _description = "Tabel Fat"
    _rec_name = 'nilai'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Nama Fat')
    nilai = fields.Float('Nilai')
    is_default = fields.Boolean('Default')

class SMLiter(models.Model):
    _inherit = "stock.move"

    tipe_sapi_id = fields.Many2one('master.tipe.sapi', 'Tipe Sapi')
