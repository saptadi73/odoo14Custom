# from odoo import models, fields, api

# class entry_gdfp(models.Model):
#     _name = "entry.gdfp"
#     _inherit = ['mail.thread', 'mail.activity.mixin']
#     _description = "Entry GDFP"
#     _rec_name = 'jenis_kunjungan_id'

#     tanggal = fields.Datetime('Tanggal')
#     petugas_id = fields.Many2one('res.users', 'Petugas', domain=[("tipe_user", "=", "petugas")])
#     jenis_kunjungan_id = fields.Many2one('master.jenis.kunjungan', 'Jenis kunjungan')
#     anggota_id = fields.Many2one('simpin_syariah.member', 'Nama Anggota')
#     kode_anggota = fields.Char(related='anggota_id.kode_anggota', string='Kode Anggota')
#     gmbr = fields.Binary('Imagae')
#     #manajemen pakan
#     bobot_bdn = fields.Integer('Bobot Badan Kg')
#     prod_susu = fields.Integer('Produksi Susu Liter')
#     # status_reprod = fields.Selection([
#     #     ('bunting', 'Bunting'),
#     #     ('tdk_bunting', 'Tidak Bunting'),
#     # ], string='Status Reproduksi')
#     # jenis_hijauan = fields.Selection([
#     #     ('1', 'Jerami Padi'),
#     #     ('2', 'Rumput Gajah'),
#     # ], string='Jenis Hijauan')
#     jenis_hijauan_jerami = fields.Boolean('Jerami Padi', default=False)
#     nilai_bk_jerami = fields.Float('BK Jerami', default=0.80, digits=(3, 2), readonly=False)
#     nilai_tdn_jerami = fields.Float('TDN Jerami', default=0.39, digits=(3, 2), readonly=True)
#     juml_hijauan_jerami = fields.Integer('Jumlah Hijauan Kg')
#     # juml_hijauan_jeramis = fields.Integer('Jumlah Hijauan Kg')
#     jenis_hijauan_gajah = fields.Boolean('Rumput Gajah', default=False)
#     nilai_bk_gajah = fields.Float('BK Gajah', digits=(3, 2), readonly=False)
#     nilai_tdn_gajah = fields.Float('TDN gajah', default=0.52, digits=(3, 2), readonly=True)
#     juml_hijauan_gajah = fields.Integer('Jumlah Hijauan Kg')
#     # juml_hijauan_gajahs = fields.Integer('Jumlah Hijauan Kg')
#     jenis_hijauan_tebon = fields.Boolean('Rumput Tebon', default=False)
#     nilai_bk_tebon = fields.Float('BK Tebon', default=0.20, digits=(3, 2), readonly=True)
#     nilai_tdn_tebon = fields.Float('TDN Tebon', default=0.58, digits=(3, 2), readonly=True)
#     juml_hijauan_tebon = fields.Integer('Jumlah Hijauan Kg')
#     jenis_hijauan_tebu = fields.Boolean('Pucuk Tebu', default=False)
#     nilai_bk_tebu = fields.Float('BK Tebu', default=0.22, digits=(3, 2), readonly=True)
#     nilai_tdn_tebu = fields.Float('TDN Tebu', default=0.51, digits=(3, 2), readonly=True)
#     juml_hijauan_tebu = fields.Integer('Jumlah Hijauan Kg')
#     jenis_hijauan_pakchong = fields.Boolean('Rumput Pakchong', default=False)
#     nilai_bk_pakchong = fields.Float('BK Pakchong', default=0.20, digits=(3, 2), readonly=True)
#     nilai_tdn_pakchong = fields.Float('TDN Pakchong', default=0.58, digits=(3, 2), readonly=True)
#     juml_hijauan_pakchong = fields.Integer('Jumlah Hijauan Kg')
#     jenis_hijauan_odot = fields.Boolean('Rumput Odot', default=False)
#     nilai_bk_odot = fields.Float('BK Odot', default=0.20, digits=(3, 2), readonly=True)
#     nilai_tdn_odot = fields.Float('TDN Odot', default=0.65, digits=(3, 2), readonly=True)
#     juml_hijauan_odot = fields.Integer('Jumlah Hijauan Kg')
#     jenis_hijauan_lapang = fields.Boolean('Rumput Lapang', default=False)
#     nilai_bk_lapang = fields.Float('BK Lapang', default=0.20, digits=(3, 2), readonly=True)
#     nilai_tdn_lapang = fields.Float('TDN Lapang', default=0.65, digits=(3, 2), readonly=True)
#     juml_hijauan_lapang = fields.Integer('Jumlah Hijauan Kg')
#     #jenis konsentrat
#     jenis_kons_plus = fields.Boolean('Super Plus', default=False)
#     nilai_bk_plus = fields.Float('BK Plus', default=0.88, digits=(3, 2), readonly=True)
#     nilai_tdn_plus = fields.Float('TDN Plus', default=0.69, digits=(3, 2), readonly=True)
#     juml_kons_plus = fields.Integer('Jumlah konsentrat Kg')
#     jenis_kons_2a = fields.Boolean('Super 2A', default=False)
#     nilai_bk_2a = fields.Float('BK Super 2A', default=0.87, digits=(3, 2), readonly=True)
#     nilai_tdn_2a = fields.Float('TDN Super 2A', default=0.62, digits=(3, 2), readonly=True)
#     juml_kons_2a = fields.Integer('Jumlah konsentrat Kg')
#     jenis_kons_mapan = fields.Boolean('Maju Mapan', default=False)
#     nilai_bk_mapan = fields.Float('BK Maju Mapan', default=0.87, digits=(3, 2), readonly=True)
#     nilai_tdn_mapan = fields.Float('TDN Maju Mapan', default=0.66, digits=(3, 2), readonly=True)
#     juml_kons_mapan = fields.Integer('Jumlah konsentrat Kg')
#     jenis_kons_feed = fields.Boolean('Mix Feed', default=False)
#     nilai_bk_feed = fields.Float('BK Mix Feed', default=0.89, digits=(3, 2), readonly=True)
#     nilai_tdn_feed = fields.Float('TDN Mix Feed', default=0.78, digits=(3, 2), readonly=True)
#     juml_kons_feed = fields.Integer('Jumlah konsentrat Kg')
#     #jenis pakan tambah
#     jenis_tambah_selep = fields.Boolean('Roti Selep', default=False)
#     nilai_bk_selep = fields.Float('BK Roti Selep', default=0.87, digits=(3, 2), readonly=True)
#     nilai_tdn_selep = fields.Float('TDN Roti Selep', default=0.87, digits=(3, 2), readonly=True)
#     juml_tambah_selep = fields.Integer('Jumlah Pakan Tambah Kg')
#     jenis_tambah_tawar = fields.Boolean('Roti Tawar', default=False)
#     nilai_bk_tawar = fields.Float('BK Roti Tawar', default=0.87, digits=(3, 2), readonly=True)
#     nilai_tdn_tawar = fields.Float('TDN Roti Tawar', default=0.94, digits=(3, 2), readonly=True)
#     juml_tambah_tawar = fields.Integer('Jumlah Pakan Tambah Kg')
#     jenis_tambah_singkong = fields.Boolean('Singkong', default=False)
#     nilai_bk_singkong = fields.Float('BK Singkong', default=0.30, digits=(3, 2), readonly=True)
#     nilai_tdn_singkong = fields.Float('TDN Singkong', default=0.88, digits=(3, 2), readonly=True)
#     juml_tambah_singkong = fields.Integer('Jumlah Pakan Tambah Kg')
#     jenis_tambah_gamblong = fields.Boolean('Gamblong', default=False)
#     nilai_bk_gamblong = fields.Float('BK Gamblong', default=0.26, digits=(3, 2), readonly=True)
#     nilai_tdn_gamblong = fields.Float('TDN Gamblong', default=0.95, digits=(3, 2), readonly=True)
#     juml_tambah_gamblong = fields.Integer('Jumlah Pakan Tambah Kg')
#     jenis_tambah_bir = fields.Boolean('Bir', default=False)
#     nilai_bk_bir = fields.Float('BK Bir', default=0.27, digits=(3, 2), readonly=True)
#     nilai_tdn_bir = fields.Float('TDN Bir', default=0.87, digits=(3, 2), readonly=True)
#     juml_tambah_bir = fields.Integer('Jumlah Pakan Tambah Kg')
#     jenis_tambah_tahu = fields.Boolean('Tahu', default=False)
#     nilai_bk_tahu = fields.Float('BK Tahu', default=0.27, digits=(3, 2), readonly=True)
#     nilai_tdn_tahu = fields.Float('TDN Tahu', default=0.85, digits=(3, 2), readonly=True)
#     juml_tambah_tahu = fields.Integer('Jumlah Pakan Tambah Kg')
#     #lahan hijauan
#     luas_lahan = fields.Float('Luas Lahan (m2)')
#     jns_hpt = fields.Char('Jenis HPT')
#     add_jns_hpt = fields.Char('Add Jenis HPT')
#     produktivitas = fields.Float('Produktivitas/m2')
#     stts_kpmlkn = fields.Selection([
#         ('ms', 'Milik Sendiri'),
#         ('s', 'Sewa'),
#     ], string='Status Kepemilikan')
#     #choper
#     choper = fields.Selection([
#         ('1', 'Tidak Punya'),
#         ('2', 'Punya Tidak Berfungsi'),
#         ('3', 'Punya & Berfungsi'),
#     ], string='Chopper (Opsi)')

#     # #kondisi reproduksi
#     # @api.depends('status_reprod')
#     # def _compute_reproduksi(self):
#     #     for sapi in self:
#     #         if sapi.status_reprod == 'bunting':
#     #             sapi.reproduksi = 2.4
#     #         elif sapi.status_reprod == 'tdk_bunting':
#     #             sapi.reproduksi = 0

#     # tabel kebutuhan tdn pakan
#     hidup_pokok = fields.Float('Hidup Pokok', default=7.5, readonly=True)
#     produksi = fields.Float('Produksi', default=326, readonly=True)
#     reproduksi = fields.Float('Reproduksi', compute='_compute_reproduksi', store=True, readonly=True)

#     hasil_tdn_hp = fields.Float('Hasil', compute='hitung_nilai_tdn_hidup_pokok', readonly=True)
#     hasil_tdn_produksi = fields.Float('Hasil', compute='hitung_nilai_tdn_produksi', readonly=True)
#     hasil_tdn_reproduksi = fields.Float('Hasil', compute='hitung_nilai_tdn_reproduksi', readonly=True)
#     total_tdn = fields.Float('Total Kebutuhan TDN', compute='hitung_total_tdn')
#     #tabel kebutuhan tdn pakan
#     @api.depends('gdfp_line.bobot_badan', 'hidup_pokok')
#     def hitung_nilai_tdn_hidup_pokok(self):
#         for record in self:
#             record.hasil_tdn_hp = sum(line.bobot_badan * record.hidup_pokok for line in record.gdfp_line)

#     @api.depends('gdfp_line.prod_susu_liter', 'produksi')
#     def hitung_nilai_tdn_produksi(self):
#         for record in self:
#             record.hasil_tdn_produksi = sum(line.prod_susu_liter * record.produksi for line in record.gdfp_line)

#     @api.depends('gdfp_line.bobot_badan', 'gdfp_line.reproduksi')
#     def hitung_nilai_tdn_reproduksi(self):
#         for record in self:
#             record.hasil_tdn_reproduksi = sum(line.bobot_badan * line.reproduksi for line in record.gdfp_line)

#     @api.depends('hasil_tdn_hp', 'hasil_tdn_produksi', 'hasil_tdn_reproduksi')
#     def hitung_total_tdn(self):
#         for record in self:
#             record.total_tdn = record.hasil_tdn_hp + record.hasil_tdn_produksi + record.hasil_tdn_reproduksi

#     #tabel penghitungan tdn dan bk pakan hijauan
#     bk_tersedia_jerami = fields.Float('BK Tersedia', compute='_compute_bk_tersedia_jerami')
#     tdn_tersedia_jerami = fields.Float('TDN Tersedia', compute='_compute_tdn_tersedia_jerami')
#     bk_tersedia_gajah = fields.Float('BK Tersedia', compute='_compute_bk_tersedia_gajah')
#     tdn_tersedia_gajah = fields.Float('TDN Tersedia', compute='_compute_tdn_tersedia_gajah')
#     bk_tersedia_tebon = fields.Float('BK Tersedia', compute='_compute_bk_tersedia_tebon')
#     tdn_tersedia_tebon = fields.Float('TDN Tersedia', compute='_compute_tdn_tersedia_tebon')
#     bk_tersedia_tebu = fields.Float('BK Tersedia', compute='_compute_bk_tersedia_tebu')
#     tdn_tersedia_tebu = fields.Float('TDN Tersedia', compute='_compute_tdn_tersedia_tebu')
#     bk_tersedia_pakchong = fields.Float('BK Tersedia', compute='_compute_bk_tersedia_pakchong')
#     tdn_tersedia_pakchong = fields.Float('TDN Tersedia', compute='_compute_tdn_tersedia_pakchong')
#     bk_tersedia_odot = fields.Float('BK Tersedia', compute='_compute_bk_tersedia_odot')
#     tdn_tersedia_odot = fields.Float('TDN Tersedia', compute='_compute_tdn_tersedia_odot')
#     bk_tersedia_lapang = fields.Float('BK Tersedia', compute='_compute_bk_tersedia_lapang')
#     tdn_tersedia_lapang = fields.Float('TDN Tersedia', compute='_compute_tdn_tersedia_lapang')
#     #tabel penghitungan tdn dan bk pakan konsentrat
#     bk_tersedia_plus = fields.Float('BK Tersedia', compute='_compute_bk_tersedia_plus')
#     tdn_tersedia_plus = fields.Float('TDN Tersedia', compute='_compute_tdn_tersedia_plus')
#     bk_tersedia_2a = fields.Float('BK Tersedia', compute='_compute_bk_tersedia_2a')
#     tdn_tersedia_2a = fields.Float('TDN Tersedia', compute='_compute_tdn_tersedia_2a')
#     bk_tersedia_mapan = fields.Float('BK Tersedia', compute='_compute_bk_tersedia_mapan')
#     tdn_tersedia_mapan = fields.Float('TDN Tersedia', compute='_compute_tdn_tersedia_mapan')
#     bk_tersedia_feed = fields.Float('BK Tersedia', compute='_compute_bk_tersedia_feed')
#     tdn_tersedia_feed = fields.Float('TDN Tersedia', compute='_compute_tdn_tersedia_feed')
#     #tabel penghitungan tdn dan bk pakan tambah
#     bk_tersedia_selep = fields.Float('BK Tersedia', compute='_compute_bk_tersedia_selep')
#     tdn_tersedia_selep = fields.Float('TDN Tersedia', compute='_compute_tdn_tersedia_selep')
#     bk_tersedia_tawar = fields.Float('BK Tersedia', compute='_compute_bk_tersedia_tawar')
#     tdn_tersedia_tawar = fields.Float('TDN Tersedia', compute='_compute_tdn_tersedia_tawar')
#     bk_tersedia_singkong = fields.Float('BK Tersedia', compute='_compute_bk_tersedia_singkong')
#     tdn_tersedia_singkong = fields.Float('TDN Tersedia', compute='_compute_tdn_tersedia_singkong')
#     bk_tersedia_gamblong = fields.Float('BK Tersedia', compute='_compute_bk_tersedia_gamblong')
#     tdn_tersedia_gamblong = fields.Float('TDN Tersedia', compute='_compute_tdn_tersedia_gamblong')
#     bk_tersedia_bir = fields.Float('BK Tersedia', compute='_compute_bk_tersedia_bir')
#     tdn_tersedia_bir = fields.Float('TDN Tersedia', compute='_compute_tdn_tersedia_bir')
#     bk_tersedia_tahu = fields.Float('BK Tersedia', compute='_compute_bk_tersedia_tahu')
#     tdn_tersedia_tahu = fields.Float('TDN Tersedia', compute='_compute_tdn_tersedia_tahu')

#     tabel_hijauan_ids = fields.One2many('tabel.hijauan', 'entry_gdfp_id', string='Tabel Hijauan')
#     tabel_konsentrat_ids = fields.One2many('tabel.konsentrat', 'konsentrat_gdfp_id', string='Tabel Konsentrat')
#     tabel_pakan_tambah_ids = fields.One2many('tabel.pakan.tambah', 'pakan_tambah_gdfp_id', string='Tabel Pakan Tambah')


#     #menghitung pakan tersedia hijauan
#     #jerami
#     @api.depends('juml_hijauan_jerami')
#     def _compute_bk_tersedia_jerami(self):
#         for record in self:
#             nilai_bk_jerami = record.env['tabel.hijauan'].search([], limit=1).nilai_bk_jerami
#             record.bk_tersedia_jerami = nilai_bk_jerami * record.juml_hijauan_jerami

#     # @api.depends('nilai_bk_jerami', 'juml_hijauan_jerami')
#     # def hitung_bk_tersedia_jerami(self):
#     #     for record in self:
#     #         record.bk_tersedia_jerami = record.nilai_bk_jerami * record.juml_hijauan_jerami

#     @api.depends('bk_tersedia_jerami')
#     def _compute_tdn_tersedia_jerami(self):
#         for record in self:
#             nilai_tdn_jerami = record.env['tabel.hijauan'].search([], limit=1).nilai_tdn_jerami
#             tdn_tersedia = nilai_tdn_jerami * record.bk_tersedia_jerami * 1000
#             record.tdn_tersedia_jerami = tdn_tersedia

#     # @api.depends('nilai_tdn_jerami', 'bk_tersedia_jerami')
#     # def hitung_tdn_jerami_padi(self):
#     #     for record in self:
#     #         record.tdn_tersedia_jerami = record.nilai_tdn_jerami * record.bk_tersedia_jerami * 1000
#     #rumput gajah
#     # @api.depends('nilai_bk_gajah', 'juml_hijauan_gajah')
#     # def hitung_bk_tersedia_gajah(self):
#     #     for record in self:
#     #         record.bk_tersedia_gajah = record.nilai_bk_gajah * record.juml_hijauan_gajah
#     #
#     # @api.depends('bk_tersedia_gajah', 'nilai_tdn_gajah')
#     # def hitung_tdn_rumput_gajah(self):
#     #     for record in self:
#     #         record.tdn_tersedia_gajah = record.bk_tersedia_gajah * record.nilai_tdn_gajah * 1000

#     @api.depends('juml_hijauan_gajah')
#     def _compute_bk_tersedia_gajah(self):
#         for record in self:
#             nilai_bk_gajah = record.env['tabel.hijauan'].search([], limit=1).nilai_bk_gajah
#             record.bk_tersedia_gajah = nilai_bk_gajah * record.juml_hijauan_gajah

#     @api.depends('bk_tersedia_gajah')
#     def _compute_tdn_tersedia_gajah(self):
#         for record in self:
#             nilai_tdn_gajah = record.env['tabel.hijauan'].search([], limit=1).nilai_tdn_gajah
#             tdn_tersedia = nilai_tdn_gajah * record.bk_tersedia_gajah * 1000
#             record.tdn_tersedia_gajah = tdn_tersedia

#     # rumput tebon
#     # @api.depends('nilai_bk_tebon', 'juml_hijauan_tebon')
#     # def hitung_bk_tersedia_tebon(self):
#     #     for record in self:
#     #         record.bk_tersedia_tebon = record.nilai_bk_tebon * record.juml_hijauan_tebon
#     #
#     # @api.depends('bk_tersedia_tebon', 'nilai_tdn_tebon')
#     # def hitung_tdn_rumput_tebon(self):
#     #     for record in self:
#     #         record.tdn_tersedia_tebon = record.bk_tersedia_tebon * record.nilai_tdn_tebon * 1000

#     @api.depends('juml_hijauan_tebon')
#     def _compute_bk_tersedia_tebon(self):
#         for record in self:
#             nilai_bk_tebon = record.env['tabel.hijauan'].search([], limit=1).nilai_bk_tebon
#             record.bk_tersedia_tebon = nilai_bk_tebon * record.juml_hijauan_tebon

#     @api.depends('bk_tersedia_tebon')
#     def _compute_tdn_tersedia_tebon(self):
#         for record in self:
#             nilai_tdn_tebon = record.env['tabel.hijauan'].search([], limit=1).nilai_tdn_tebon
#             tdn_tersedia = nilai_tdn_tebon * record.bk_tersedia_tebon * 1000
#             record.tdn_tersedia_tebon = tdn_tersedia

#     #pucuk tebu
#     # @api.depends('nilai_bk_tebu', 'juml_hijauan_tebu')
#     # def hitung_bk_tersedia_tebu(self):
#     #     for record in self:
#     #         record.bk_tersedia_tebu = record.nilai_bk_tebu * record.juml_hijauan_tebu
#     #
#     # @api.depends('bk_tersedia_tebu', 'nilai_tdn_tebu')
#     # def hitung_tdn_rumput_tebu(self):
#     #     for record in self:
#     #         record.tdn_tersedia_tebu = record.bk_tersedia_tebu * record.nilai_tdn_tebu * 1000

#     @api.depends('juml_hijauan_tebu')
#     def _compute_bk_tersedia_tebu(self):
#         for record in self:
#             nilai_bk_tebu = record.env['tabel.hijauan'].search([], limit=1).nilai_bk_tebu
#             record.bk_tersedia_tebu = nilai_bk_tebu * record.juml_hijauan_tebu

#     @api.depends('bk_tersedia_tebu')
#     def _compute_tdn_tersedia_tebu(self):
#         for record in self:
#             nilai_tdn_tebu = record.env['tabel.hijauan'].search([], limit=1).nilai_tdn_tebu
#             tdn_tersedia = nilai_tdn_tebu * record.bk_tersedia_tebu * 1000
#             record.tdn_tersedia_tebu = tdn_tersedia

#     #rumput pakchong
#     # @api.depends('nilai_bk_pakchong', 'juml_hijauan_pakchong')
#     # def hitung_bk_tersedia_pakchong(self):
#     #     for record in self:
#     #         record.bk_tersedia_pakchong = record.nilai_bk_pakchong * record.juml_hijauan_pakchong
#     #
#     # @api.depends('bk_tersedia_pakchong', 'nilai_tdn_pakchong')
#     # def hitung_tdn_rumput_pakchong(self):
#     #     for record in self:
#     #         record.tdn_tersedia_pakchong = record.bk_tersedia_pakchong * record.nilai_tdn_pakchong * 1000

#     @api.depends('juml_hijauan_pakchong')
#     def _compute_bk_tersedia_pakchong(self):
#         for record in self:
#             nilai_bk_pakchong = record.env['tabel.hijauan'].search([], limit=1).nilai_bk_pakchong
#             record.bk_tersedia_pakchong = nilai_bk_pakchong * record.juml_hijauan_pakchong

#     @api.depends('bk_tersedia_pakchong')
#     def _compute_tdn_tersedia_pakchong(self):
#         for record in self:
#             nilai_tdn_pakchong = record.env['tabel.hijauan'].search([], limit=1).nilai_tdn_pakchong
#             tdn_tersedia = nilai_tdn_pakchong * record.bk_tersedia_pakchong * 1000
#             record.tdn_tersedia_pakchong = tdn_tersedia

#     #rumput odot
#     # @api.depends('nilai_bk_odot', 'juml_hijauan_odot')
#     # def hitung_bk_tersedia_odot(self):
#     #     for record in self:
#     #         record.bk_tersedia_odot = record.nilai_bk_odot * record.juml_hijauan_odot
#     #
#     # @api.depends('bk_tersedia_odot', 'nilai_tdn_odot')
#     # def hitung_tdn_rumput_odot(self):
#     #     for record in self:
#     #         record.tdn_tersedia_odot = record.bk_tersedia_odot * record.nilai_tdn_odot * 1000

#     @api.depends('juml_hijauan_odot')
#     def _compute_bk_tersedia_odot(self):
#         for record in self:
#             nilai_bk_odot = record.env['tabel.hijauan'].search([], limit=1).nilai_bk_odot
#             record.bk_tersedia_odot = nilai_bk_odot * record.juml_hijauan_odot

#     @api.depends('bk_tersedia_odot')
#     def _compute_tdn_tersedia_odot(self):
#         for record in self:
#             nilai_tdn_odot = record.env['tabel.hijauan'].search([], limit=1).nilai_tdn_odot
#             tdn_tersedia = nilai_tdn_odot * record.bk_tersedia_odot * 1000
#             record.tdn_tersedia_odot = tdn_tersedia

#     #rumput lapang
#     # @api.depends('nilai_bk_lapang', 'juml_hijauan_lapang')
#     # def hitung_bk_tersedia_lapang(self):
#     #     for record in self:
#     #         record.bk_tersedia_lapang = record.nilai_bk_lapang * record.juml_hijauan_lapang
#     #
#     # @api.depends('bk_tersedia_lapang', 'nilai_tdn_lapang')
#     # def hitung_tdn_rumput_lapang(self):
#     #     for record in self:
#     #         record.tdn_tersedia_lapang = record.bk_tersedia_lapang * record.nilai_tdn_lapang * 1000

#     @api.depends('juml_hijauan_lapang')
#     def _compute_bk_tersedia_lapang(self):
#         for record in self:
#             nilai_bk_lapang = record.env['tabel.hijauan'].search([], limit=1).nilai_bk_lapang
#             record.bk_tersedia_lapang = nilai_bk_lapang * record.juml_hijauan_lapang

#     @api.depends('bk_tersedia_lapang')
#     def _compute_tdn_tersedia_lapang(self):
#         for record in self:
#             nilai_tdn_lapang = record.env['tabel.hijauan'].search([], limit=1).nilai_tdn_lapang
#             tdn_tersedia = nilai_tdn_lapang * record.bk_tersedia_lapang * 1000
#             record.tdn_tersedia_lapang = tdn_tersedia

#     #hasil total tdn tersedia hijauan
#     @api.depends('tdn_tersedia_jerami', 'tdn_tersedia_gajah', 'tdn_tersedia_tebon', 'tdn_tersedia_tebu', 'tdn_tersedia_pakchong', 'tdn_tersedia_odot', 'tdn_tersedia_lapang')
#     def hitung_total_tdn_tersedia_hijauan(self):
#         for record in self:
#             record.total_tdn_hijauan = record.tdn_tersedia_jerami + record.tdn_tersedia_gajah + record.tdn_tersedia_tebon + record.tdn_tersedia_tebu + record.tdn_tersedia_pakchong + record.tdn_tersedia_odot + record.tdn_tersedia_lapang

#     total_tdn_hijauan = fields.Float(compute='hitung_total_tdn_tersedia_hijauan', string='Total TDN Hijauan')

#     #hasil total tdn tersedia konsentrat
#     @api.depends('tdn_tersedia_plus', 'tdn_tersedia_2a', 'tdn_tersedia_mapan', 'tdn_tersedia_feed')
#     def hitung_total_tdn_tersedia_konsentrat(self):
#         for record in self:
#             record.total_tdn_konsentrat = record.tdn_tersedia_plus + record.tdn_tersedia_2a + record.tdn_tersedia_mapan + record.tdn_tersedia_feed

#     total_tdn_konsentrat = fields.Float(compute='hitung_total_tdn_tersedia_konsentrat', string='Total TDN Konsentrat')

#     # hasil total tdn tersedia pakan tambah
#     @api.depends('tdn_tersedia_selep', 'tdn_tersedia_tawar', 'tdn_tersedia_singkong', 'tdn_tersedia_gamblong', 'tdn_tersedia_bir', 'tdn_tersedia_tahu')
#     def hitung_total_tdn_tersedia_tambah(self):
#         for record in self:
#             record.total_tdn_tambah = record.tdn_tersedia_selep + record.tdn_tersedia_tawar + record.tdn_tersedia_singkong + record.tdn_tersedia_gamblong + record.tdn_tersedia_bir + record.tdn_tersedia_tahu

#     total_tdn_tambah = fields.Float(compute='hitung_total_tdn_tersedia_tambah', string='Total TDN Pakan Tambah')

#     #perhitungan tersedia pakan konsentrat
#     #super plus

#     @api.depends('juml_kons_plus')
#     def _compute_bk_tersedia_plus(self):
#         for record in self:
#             nilai_bk_plus = record.env['tabel.konsentrat'].search([], limit=1).nilai_bk_plus
#             record.bk_tersedia_plus = nilai_bk_plus * record.juml_kons_plus

#     # @api.depends('nilai_bk_plus', 'juml_kons_plus')
#     # def hitung_bk_tersedia_plus(self):
#     #     for record in self:
#     #         record.bk_tersedia_plus = record.nilai_bk_plus * record.juml_kons_plus

#     @api.depends('bk_tersedia_plus')
#     def _compute_tdn_tersedia_plus(self):
#         for record in self:
#             nilai_tdn_plus = record.env['tabel.konsentrat'].search([], limit=1).nilai_tdn_plus
#             tdn_tersedia = nilai_tdn_plus * record.bk_tersedia_plus * 1000
#             record.tdn_tersedia_plus = tdn_tersedia

#     # @api.depends('nilai_tdn_plus', 'bk_tersedia_plus')
#     # def hitung_tdn_kons_plus(self):
#     #     for record in self:
#     #         record.tdn_tersedia_plus = record.nilai_tdn_plus * record.bk_tersedia_plus * 1000

#     #super 2a
#     # @api.depends('nilai_bk_2a', 'juml_kons_2a')
#     # def hitung_bk_tersedia_2a(self):
#     #     for record in self:
#     #         record.bk_tersedia_2a = record.nilai_bk_2a * record.juml_kons_2a
#     #
#     # @api.depends('nilai_tdn_2a', 'bk_tersedia_2a')
#     # def hitung_tdn_kons_2a(self):
#     #     for record in self:
#     #         record.tdn_tersedia_2a = record.nilai_tdn_2a * record.bk_tersedia_2a * 1000

#     @api.depends('juml_kons_2a')
#     def _compute_bk_tersedia_2a(self):
#         for record in self:
#             nilai_bk_2a = record.env['tabel.konsentrat'].search([], limit=1).nilai_bk_2a
#             record.bk_tersedia_2a = nilai_bk_2a * record.juml_kons_2a

#     @api.depends('bk_tersedia_2a')
#     def _compute_tdn_tersedia_2a(self):
#         for record in self:
#             nilai_tdn_2a = record.env['tabel.konsentrat'].search([], limit=1).nilai_tdn_2a
#             tdn_tersedia = nilai_tdn_2a * record.bk_tersedia_2a * 1000
#             record.tdn_tersedia_2a = tdn_tersedia

#     #maju mapan
#     # @api.depends('nilai_bk_mapan', 'juml_kons_mapan')
#     # def hitung_bk_tersedia_mapan(self):
#     #     for record in self:
#     #         record.bk_tersedia_mapan = record.nilai_bk_mapan * record.juml_kons_mapan
#     #
#     # @api.depends('nilai_tdn_mapan', 'bk_tersedia_mapan')
#     # def hitung_tdn_kons_mapan(self):
#     #     for record in self:
#     #         record.tdn_tersedia_mapan = record.nilai_tdn_mapan * record.bk_tersedia_mapan * 1000

#     @api.depends('juml_kons_mapan')
#     def _compute_bk_tersedia_mapan(self):
#         for record in self:
#             nilai_bk_mapan = record.env['tabel.konsentrat'].search([], limit=1).nilai_bk_mapan
#             record.bk_tersedia_mapan = nilai_bk_mapan * record.juml_kons_mapan

#     @api.depends('bk_tersedia_mapan')
#     def _compute_tdn_tersedia_mapan(self):
#         for record in self:
#             nilai_tdn_mapan = record.env['tabel.konsentrat'].search([], limit=1).nilai_tdn_mapan
#             tdn_tersedia = nilai_tdn_mapan * record.bk_tersedia_mapan * 1000
#             record.tdn_tersedia_mapan = tdn_tersedia

#     #mix feed
#     # @api.depends('nilai_bk_feed', 'juml_kons_feed')
#     # def hitung_bk_tersedia_feed(self):
#     #     for record in self:
#     #         record.bk_tersedia_feed = record.nilai_bk_feed * record.juml_kons_feed
#     #
#     # @api.depends('nilai_tdn_feed', 'bk_tersedia_feed')
#     # def hitung_tdn_kons_feed(self):
#     #     for record in self:
#     #         record.tdn_tersedia_feed = record.nilai_tdn_feed * record.bk_tersedia_feed * 1000

#     @api.depends('juml_kons_feed')
#     def _compute_bk_tersedia_feed(self):
#         for record in self:
#             nilai_bk_feed = record.env['tabel.konsentrat'].search([], limit=1).nilai_bk_feed
#             record.bk_tersedia_feed = nilai_bk_feed * record.juml_kons_feed

#     @api.depends('bk_tersedia_feed')
#     def _compute_tdn_tersedia_feed(self):
#         for record in self:
#             nilai_bk_feed = record.env['tabel.konsentrat'].search([], limit=1).nilai_bk_feed
#             tdn_tersedia = nilai_bk_feed * record.bk_tersedia_feed * 1000
#             record.tdn_tersedia_feed = tdn_tersedia

#     #perhitungan tersedia pakan tambah
#     #selep
#     # @api.depends('nilai_bk_selep', 'juml_tambah_selep')
#     # def hitung_bk_tersedia_selep(self):
#     #     for record in self:
#     #         record.bk_tersedia_selep = record.nilai_bk_selep * record.juml_tambah_selep
#     #
#     # @api.depends('nilai_tdn_selep', 'bk_tersedia_selep')
#     # def hitung_tdn_tersedia_selep(self):
#     #     for record in self:
#     #         record.tdn_tersedia_selep = record.nilai_tdn_selep * record.bk_tersedia_selep * 1000

#     @api.depends('juml_tambah_selep')
#     def _compute_bk_tersedia_selep(self):
#         for record in self:
#             nilai_bk_selep = record.env['tabel.pakan.tambah'].search([], limit=1).nilai_bk_selep
#             record.bk_tersedia_selep = nilai_bk_selep * record.juml_tambah_selep

#     @api.depends('bk_tersedia_selep')
#     def _compute_tdn_tersedia_selep(self):
#         for record in self:
#             nilai_tdn_selep = record.env['tabel.pakan.tambah'].search([], limit=1).nilai_tdn_selep
#             tdn_tersedia = nilai_tdn_selep * record.bk_tersedia_selep * 1000
#             record.tdn_tersedia_selep = tdn_tersedia

#     #tawar
#     # @api.depends('nilai_bk_tawar', 'juml_tambah_tawar')
#     # def hitung_bk_tersedia_tawar(self):
#     #     for record in self:
#     #         record.bk_tersedia_tawar = record.nilai_bk_tawar * record.juml_tambah_tawar
#     #
#     # @api.depends('nilai_tdn_tawar', 'bk_tersedia_tawar')
#     # def hitung_tdn_tersedia_tawar(self):
#     #     for record in self:
#     #         record.tdn_tersedia_tawar = record.nilai_tdn_tawar * record.bk_tersedia_tawar * 1000

#     @api.depends('juml_tambah_tawar')
#     def _compute_bk_tersedia_tawar(self):
#         for record in self:
#             nilai_bk_tawar = record.env['tabel.pakan.tambah'].search([], limit=1).nilai_bk_tawar
#             record.bk_tersedia_tawar = nilai_bk_tawar * record.juml_tambah_tawar

#     @api.depends('bk_tersedia_tawar')
#     def _compute_tdn_tersedia_tawar(self):
#         for record in self:
#             nilai_tdn_tawar = record.env['tabel.pakan.tambah'].search([], limit=1).nilai_tdn_tawar
#             tdn_tersedia = nilai_tdn_tawar * record.bk_tersedia_tawar * 1000
#             record.tdn_tersedia_tawar = tdn_tersedia

#     #singkong
#     # @api.depends('nilai_bk_singkong', 'juml_tambah_singkong')
#     # def hitung_bk_tersedia_singkong(self):
#     #     for record in self:
#     #         record.bk_tersedia_singkong = record.nilai_bk_singkong * record.juml_tambah_singkong
#     #
#     # @api.depends('nilai_tdn_singkong', 'bk_tersedia_singkong')
#     # def hitung_tdn_tersedia_singkong(self):
#     #     for record in self:
#     #         record.tdn_tersedia_singkong = record.nilai_tdn_singkong * record.bk_tersedia_singkong * 1000

#     @api.depends('juml_tambah_singkong')
#     def _compute_bk_tersedia_singkong(self):
#         for record in self:
#             nilai_bk_singkong = record.env['tabel.pakan.tambah'].search([], limit=1).nilai_bk_singkong
#             record.bk_tersedia_singkong = nilai_bk_singkong * record.juml_tambah_singkong

#     @api.depends('bk_tersedia_singkong')
#     def _compute_tdn_tersedia_singkong(self):
#         for record in self:
#             nilai_tdn_singkong = record.env['tabel.pakan.tambah'].search([], limit=1).nilai_tdn_singkong
#             tdn_tersedia = nilai_tdn_singkong * record.bk_tersedia_singkong * 1000
#             record.tdn_tersedia_singkong = tdn_tersedia

#     #gamblong
#     # @api.depends('nilai_bk_gamblong', 'juml_tambah_gamblong')
#     # def hitung_bk_tersedia_gamblong(self):
#     #     for record in self:
#     #         record.bk_tersedia_gamblong = record.nilai_bk_gamblong * record.juml_tambah_gamblong
#     #
#     # @api.depends('nilai_tdn_gamblong', 'bk_tersedia_gamblong')
#     # def hitung_tdn_tersedia_gamblong(self):
#     #     for record in self:
#     #         record.tdn_tersedia_gamblong = record.nilai_tdn_gamblong * record.bk_tersedia_gamblong * 1000

#     @api.depends('juml_tambah_gamblong')
#     def _compute_bk_tersedia_gamblong(self):
#         for record in self:
#             nilai_bk_gamblong = record.env['tabel.pakan.tambah'].search([], limit=1).nilai_bk_gamblong
#             record.bk_tersedia_gamblong = nilai_bk_gamblong * record.juml_tambah_gamblong

#     @api.depends('bk_tersedia_gamblong')
#     def _compute_tdn_tersedia_gamblong(self):
#         for record in self:
#             nilai_tdn_gamblong = record.env['tabel.pakan.tambah'].search([], limit=1).nilai_tdn_gamblong
#             tdn_tersedia = nilai_tdn_gamblong * record.bk_tersedia_gamblong * 1000
#             record.tdn_tersedia_gamblong = tdn_tersedia

#     #ampas bir
#     # @api.depends('nilai_bk_bir', 'juml_tambah_bir')
#     # def hitung_bk_tersedia_bir(self):
#     #     for record in self:
#     #         record.bk_tersedia_bir = record.nilai_bk_bir * record.juml_tambah_bir
#     #
#     # @api.depends('nilai_tdn_bir', 'bk_tersedia_bir')
#     # def hitung_tdn_tersedia_bir(self):
#     #     for record in self:
#     #         record.tdn_tersedia_bir = record.nilai_tdn_bir * record.bk_tersedia_bir * 1000

#     @api.depends('juml_tambah_bir')
#     def _compute_bk_tersedia_bir(self):
#         for record in self:
#             nilai_bk_bir = record.env['tabel.pakan.tambah'].search([], limit=1).nilai_bk_bir
#             record.bk_tersedia_bir = nilai_bk_bir * record.juml_tambah_bir

#     @api.depends('bk_tersedia_bir')
#     def _compute_tdn_tersedia_bir(self):
#         for record in self:
#             nilai_tdn_bir = record.env['tabel.pakan.tambah'].search([], limit=1).nilai_tdn_bir
#             tdn_tersedia = nilai_tdn_bir * record.bk_tersedia_bir * 1000
#             record.tdn_tersedia_bir = tdn_tersedia

#     #ampas tahu
#     # @api.depends('nilai_bk_tahu', 'juml_tambah_tahu')
#     # def hitung_bk_tersedia_tahu(self):
#     #     for record in self:
#     #         record.bk_tersedia_tahu = record.nilai_bk_tahu * record.juml_tambah_tahu
#     #
#     # @api.depends('nilai_tdn_tahu', 'bk_tersedia_tahu')
#     # def hitung_tdn_tersedia_tahu(self):
#     #     for record in self:
#     #         record.tdn_tersedia_tahu = record.nilai_tdn_tahu * record.bk_tersedia_tahu * 1000

#     @api.depends('juml_tambah_tahu')
#     def _compute_bk_tersedia_tahu(self):
#         for record in self:
#             nilai_bk_tahu = record.env['tabel.pakan.tambah'].search([], limit=1).nilai_bk_tahu
#             record.bk_tersedia_tahu = nilai_bk_tahu * record.juml_tambah_tahu

#     @api.depends('bk_tersedia_tahu')
#     def _compute_tdn_tersedia_tahu(self):
#         for record in self:
#             nilai_tdn_tahu = record.env['tabel.pakan.tambah'].search([], limit=1).nilai_tdn_tahu
#             tdn_tersedia = nilai_tdn_tahu * record.bk_tersedia_tahu * 1000
#             record.tdn_tersedia_tahu = tdn_tersedia

#     #total tdn tersedia
#     @api.depends('total_tdn_hijauan', 'total_tdn_konsentrat', 'total_tdn_tambah')
#     def hitung_total_tdn_tersedia(self):
#         for record in self:
#             record.total_tdn_tersedia = record.total_tdn_hijauan + record.total_tdn_konsentrat + record.total_tdn_tambah

#     total_tdn_tersedia = fields.Float(compute='hitung_total_tdn_tersedia', string='Total TDN Tersedia')

#     #hasil selisih tdn
#     @api.depends('total_tdn_tersedia', 'total_tdn')
#     def hitung_total_selisih_tdn_tersedia(self):
#         for record in self:
#             record.total_tdn_selisih = record.total_tdn - record.total_tdn_tersedia

#     total_tdn_selisih = fields.Float(compute='hitung_total_selisih_tdn_tersedia', string='Total Selisih TDN Tersedia')

#     #persentase
#     @api.depends('total_tdn_tersedia', 'total_tdn')
#     def hitung_total_persen_tdn_tersedia(self):
#         for record in self:
#             if record.total_tdn != 0:
#                 record.total_persen_tdn = record.total_tdn_tersedia / record.total_tdn * 100
#             else:
#                 record.total_persen_tdn = 0

#     total_persen_tdn = fields.Float(compute='hitung_total_persen_tdn_tersedia', string='Persentase TDN Tersedia')

#     @api.onchange('total_persen_tdn')
#     def _set_kecukupan_pakan(self):
#         if self.total_persen_tdn < 0:
#             self.kecukupan_pakan = '0'
#         elif 0 <= self.total_persen_tdn <= 50:
#             self.kecukupan_pakan = '5'
#         elif 51 <= self.total_persen_tdn <= 74:
#             self.kecukupan_pakan = '10'
#         elif 75 <= self.total_persen_tdn <= 95:
#             self.kecukupan_pakan = '20'
#         elif 96 <= self.total_persen_tdn >= 100:
#             self.kecukupan_pakan = '30'
#         else:
#             self.kecukupan_pakan = '0'

#     #score management pakan
#     kecukupan_pakan = fields.Selection([
#         ('0', ''),
#         ('5', '< 50% TDN terpenuhi'),
#         ('10', '51 - 74% TDN terpenuhi'),
#         ('20', '75 - 95% TDN terpenuhi'),
#         ('30', '96 - 100% TDN terpenuhi')
#     ], string='Kecukupan Pakan', required=False, readonly=False)

#     @api.depends('kecukupan_pakan')
#     def _hitung_score_pakan(self):
#         for record in self:
#             if record.kecukupan_pakan == '5':
#                 record.score_pakan = 5
#             elif record.kecukupan_pakan == '10':
#                 record.score_pakan = 10
#             elif record.kecukupan_pakan == '20':
#                 record.score_pakan = 20
#             elif record.kecukupan_pakan == '30':
#                 record.score_pakan = 30
#             else:
#                 record.score_pakan = 0

#     score_pakan = fields.Integer('Nilai', compute='_hitung_score_pakan')


#     # manajemen kandang
#     atap = fields.Selection([
#         ('0', ''),
#         ('1', 'Tidak ada alas kandang/ tanah'),
#         ('2', 'Lantai kayu/beton tidak berkarpet'),
#         ('3', 'Atap shade/gabble berbahan genteng'),
#     ], string='Atap Kandang', required=True)
#     lantai = fields.Selection([
#         ('0', ''),
#         ('1', 'Atap shade berbahan asbes/gelombang'),
#         ('2', 'Lantai kayu/beton tidak berkarpet'),
#         ('3', 'Lantai beton berkarpet'),
#     ], string='Lantai Kandang', required=True)
#     thi_index = fields.Selection([
#         ('0', ''),
#         ('1', 'THI Severe (80-89)'),
#         ('2', 'THI Moderate (72-79)'),
#         ('3', 'THI Light (68-71)'),
#     ], string='THI Index', required=True)
#     palungan = fields.Selection([
#         ('0', ''),
#         ('1', 'Tidak berpalungan'),
#         ('2', 'Palungan tidak permanen'),
#         ('3', 'Palungan permanen'),
#     ], string='Palungan', required=True)
#     water_adlib = fields.Selection([
#         ('0', ''),
#         ('1', 'Tidak water adlib dan diberikan air minum 2x sehari'),
#         ('2', 'Water adlib dan tidak berfungsi (air minum masih diberikan secara manual)'),
#         ('3', 'Water adlib dan berfungsi dengan baik'),
#     ], string='Water Adlib', required=True)
#     #atap
#     nilai_atap = fields.Integer('Nilai', compute='_hitung_nilai')
#     # lantai
#     nilai_lantai = fields.Integer('Nilai', compute='_hitung_nilai_lantai')
#     #thi
#     nilai_thi = fields.Integer('Nilai', compute='_hitung_nilai_thi_index')
#     # palungan
#     nilai_palungan = fields.Integer('Nilai', compute='_hitung_nilai_nilai_palungan')
#     # water
#     nilai_water = fields.Integer('Nilai', compute='_hitung_nilai_nilai_water_adlib')
#     score = fields.Integer('Score', compute='hitung_score')

#     @api.depends('atap')
#     def _hitung_nilai(self):
#         for record in self:
#             if record.atap == '1':
#                 record.nilai_atap = 1
#             elif record.atap == '2':
#                 record.nilai_atap = 2
#             elif record.atap == '3':
#                 record.nilai_atap = 3
#             else:
#                 record.nilai_atap = 0

#     @api.depends('lantai')
#     def _hitung_nilai_lantai(self):
#         for record in self:
#             if record.lantai == '1':
#                 record.nilai_lantai = 1
#             elif record.lantai == '2':
#                 record.nilai_lantai = 2
#             elif record.lantai == '3':
#                 record.nilai_lantai = 3
#             else:
#                 record.nilai_lantai = 0

#     @api.depends('thi_index')
#     def _hitung_nilai_thi_index(self):
#         for record in self:
#             if record.thi_index == '1':
#                 record.nilai_thi = 1
#             elif record.thi_index == '2':
#                 record.nilai_thi = 2
#             elif record.thi_index == '3':
#                 record.nilai_thi = 3
#             else:
#                 record.nilai_thi = 0

#     @api.depends('palungan')
#     def _hitung_nilai_nilai_palungan(self):
#         for record in self:
#             if record.palungan == '1':
#                 record.nilai_palungan = 1
#             elif record.palungan == '2':
#                 record.nilai_palungan = 2
#             elif record.palungan == '3':
#                 record.nilai_palungan = 3
#             else:
#                 record.nilai_palungan = 0

#     @api.depends('water_adlib')
#     def _hitung_nilai_nilai_water_adlib(self):
#         for record in self:
#             if record.water_adlib == '1':
#                 record.nilai_water = 1
#             elif record.water_adlib == '2':
#                 record.nilai_water = 2
#             elif record.water_adlib == '3':
#                 record.nilai_water = 3
#             else:
#                 record.nilai_water = 0

#     @api.depends('nilai_atap', 'nilai_lantai', 'nilai_thi', 'nilai_palungan', 'nilai_water')
#     def hitung_score(self):
#         for record in self:
#             record.score = record.nilai_atap + record.nilai_lantai + record.nilai_thi + record.nilai_palungan + record.nilai_water

#     #manajemen pemerahan
#     keber_susu = fields.Selection([
#         ('0', ''),
#         ('2', 'Susu disaring'),
#         ('1', 'Susu tidak disaring'),
#     ], string='Kebersihan Susu', required=True)
#     keber_can = fields.Selection([
#         ('0', ''),
#         ('2', 'Milkcan bersih'),
#         ('1', 'Milkcan kotor'),
#     ], string='Kebersihan Milkcan', required=True)
#     keber_ember = fields.Selection([
#         ('0', ''),
#         ('2', 'Ember perah bersih'),
#         ('1', 'Ember perah kotor'),
#     ], string='Kebersihan Ember Perah', required=True)
#     keber_kandang = fields.Selection([
#         ('0', ''),
#         ('1', 'Kotor, tidak dibersihkan sama sekali'),
#         ('2', 'Dibersihkan tapi lantai kandang tidak disiram'),
#         ('3', 'Dibersihkan dan lantai kandang disiram'),
#     ], string='Kebersihan Kandang', required=True)
#     keber_sapi = fields.Selection([
#         ('0', ''),
#         ('1', 'Sapi kotor'),
#         ('2', 'Sapi bersih'),
#     ], string='Kebersihan Sapi', required=True)
#     keber_peternak = fields.Selection([
#         ('0', ''),
#         ('2', 'Peternak bersih'),
#         ('1', 'Peternak kotor'),
#     ], string='Kebersihan Peternak', required=True)
#     penyetoran = fields.Selection([
#         ('0', ''),
#         ('2', 'Setor terlalu dini'),
#         ('1', 'Setor terlambat'),
#     ], string='Penyetoran', required=True)
#     nilai_susu = fields.Integer('Nilai', compute='_hitung_nilai_susu')
#     nilai_milkcan = fields.Integer('Nilai', compute='_hitung_nilai_milkcan')
#     nilai_ember = fields.Integer('Nilai', compute='_hitung_nilai_ember')
#     nilai_kandang = fields.Integer('Nilai', compute='_hitung_nilai_kandang')
#     nilai_sapi = fields.Integer('Nilai', compute='_hitung_nilai_sapi')
#     nilai_peternak = fields.Integer('Nilai', compute='_hitung_nilai_peternak')
#     nilai_penyetoran = fields.Integer('Nilai', compute='_hitung_nilai_penyetoran')
#     score_pemeliharaan = fields.Integer('Score', compute='hitung_score_pemeliharaan')

#     @api.depends('keber_susu')
#     def _hitung_nilai_susu(self):
#         for record in self:
#             if record.keber_susu == '1':
#                 record.nilai_susu = 1
#             elif record.keber_susu == '2':
#                 record.nilai_susu = 2
#             else:
#                 record.nilai_susu = 0

#     @api.depends('keber_can')
#     def _hitung_nilai_milkcan(self):
#         for record in self:
#             if record.keber_can == '1':
#                 record.nilai_milkcan = 1
#             elif record.keber_can == '2':
#                 record.nilai_milkcan = 2
#             else:
#                 record.nilai_milkcan = 0

#     @api.depends('keber_ember')
#     def _hitung_nilai_ember(self):
#         for record in self:
#             if record.keber_ember == '1':
#                 record.nilai_ember = 1
#             elif record.keber_ember == '2':
#                 record.nilai_ember = 2
#             else:
#                 record.nilai_ember = 0

#     @api.depends('keber_kandang')
#     def _hitung_nilai_kandang(self):
#         for record in self:
#             if record.keber_kandang == '1':
#                 record.nilai_kandang = 1
#             elif record.keber_kandang == '2':
#                 record.nilai_kandang = 2
#             elif record.keber_kandang == '3':
#                 record.nilai_kandang = 3
#             else:
#                 record.nilai_kandang = 0

#     @api.depends('keber_sapi')
#     def _hitung_nilai_sapi(self):
#         for record in self:
#             if record.keber_sapi == '1':
#                 record.nilai_sapi = 1
#             elif record.keber_sapi == '2':
#                 record.nilai_sapi = 2
#             else:
#                 record.nilai_sapi = 0

#     @api.depends('keber_peternak')
#     def _hitung_nilai_peternak(self):
#         for record in self:
#             if record.keber_peternak == '1':
#                 record.nilai_peternak = 1
#             elif record.keber_peternak == '2':
#                 record.nilai_peternak = 2
#             else:
#                 record.nilai_peternak = 0

#     @api.depends('penyetoran')
#     def _hitung_nilai_penyetoran(self):
#         for record in self:
#             if record.penyetoran == '1':
#                 record.nilai_penyetoran = 1
#             elif record.penyetoran == '2':
#                 record.nilai_penyetoran = 2
#             else:
#                 record.nilai_penyetoran = 0

#     @api.depends('nilai_susu', 'nilai_milkcan', 'nilai_ember', 'nilai_kandang', 'nilai_sapi', 'nilai_peternak', 'nilai_penyetoran')
#     def hitung_score_pemeliharaan(self):
#         for record in self:
#             record.score_pemeliharaan = record.nilai_susu + record.nilai_milkcan + record.nilai_ember + record.nilai_kandang + record.nilai_sapi + record.nilai_peternak + record.nilai_penyetoran

#     #daya saing
#     biaya = fields.Selection([
#         ('0', ''),
#         ('1', 'Biaya >60 % per liter susu'),
#         ('2', 'Biaya 50-60% per liter susu'),
#         ('3', 'Biaya 40-50 % per liter susu'),
#         ('4', 'Biaya <30% per liter susu')
#     ], string='Biaya Per Liter Susu', required=True)
#     nilai_biaya = fields.Integer('Nilai', compute='_hitung_nilai_biaya')
#     score_daya_saing = fields.Integer('Score', compute='hitung_score_daya_saing')

#     @api.depends('biaya')
#     def _hitung_nilai_biaya(self):
#         for record in self:
#             if record.biaya == '1':
#                 record.nilai_biaya = 5
#             elif record.biaya == '2':
#                 record.nilai_biaya = 10
#             elif record.biaya == '3':
#                 record.nilai_biaya = 15
#             elif record.biaya == '4':
#                 record.nilai_biaya = 20
#             else:
#                 record.nilai_biaya = 0

#     @api.depends('nilai_biaya')
#     def hitung_score_daya_saing(self):
#         for record in self:
#             record.score_daya_saing = record.nilai_biaya

#     #pengendalian limbah
#     limbah = fields.Selection([
#         ('0', ''),
#         ('1', 'Dibuang di curah atau sungai atau biogas saja'),
#         ('2', 'Dijadikan sebagai pupuk'),
#         ('3', 'Pemanfaatan sebagai biogas saja dan pupuk'),
#     ], string='Pemanfaatan Limbah', required=True)
#     nilai_limbah = fields.Integer('Nilai', compute='_hitung_nilai_limbah')
#     score_pengendalian_limbah = fields.Integer('Score', compute='hitung_score_pengendalian_limbah')

#     @api.depends('limbah')
#     def _hitung_nilai_limbah(self):
#         for record in self:
#             if record.limbah == '1':
#                 record.nilai_limbah = 3
#             elif record.limbah == '2':
#                 record.nilai_limbah = 6
#             elif record.limbah == '3':
#                 record.nilai_limbah = 10
#             else:
#                 record.nilai_limbah = 0

#     @api.depends('nilai_limbah')
#     def hitung_score_pengendalian_limbah(self):
#         for record in self:
#             record.score_pengendalian_limbah = record.nilai_limbah

#     #Kesehatan hewan
#     body_cond = fields.Selection([
#         ('0', ''),
#         ('1', 'BCS < 2.0'),
#         ('2', 'BCS 2.0'),
#         ('3', 'BCS 2.5'),
#         ('4', 'BCS 3.0'),
#     ], string='Body Condition Score', required=True)
#     morbi = fields.Selection([
#         ('0', ''),
#         ('1', 'Ada > 2 kasus penyakit pada bulan ini'),
#         ('2', 'Ada 2 kasus penyakit pada bulan ini'),
#         ('3', 'Ada 1 kasus penyakit di bulan ini'),
#         ('4', 'Semua sapi sehat, tidak ada kasus penyakit')
#     ], string='Morbiditas', required=True)
#     nilai_body_cond = fields.Integer('Nilai', compute='_hitung_nilai_body_cond')
#     nilai_morbi = fields.Integer('Nilai', compute='_hitung_nilai_morbi')
#     score_keswan = fields.Integer('Score', compute='hitung_score_keswan')

#     @api.depends('body_cond')
#     def _hitung_nilai_body_cond(self):
#         for record in self:
#             if record.body_cond == '1':
#                 record.nilai_body_cond = 1
#             elif record.body_cond == '2':
#                 record.nilai_body_cond = 2
#             elif record.body_cond == '3':
#                 record.nilai_body_cond = 3
#             elif record.body_cond == '4':
#                 record.nilai_body_cond = 4
#             else:
#                 record.nilai_body_cond = 0

#     @api.depends('morbi')
#     def _hitung_nilai_morbi(self):
#         for record in self:
#             if record.morbi == '1':
#                 record.nilai_morbi = 0
#             elif record.morbi == '2':
#                 record.nilai_morbi = 2
#             elif record.morbi == '3':
#                 record.nilai_morbi = 4
#             elif record.morbi == '4':
#                 record.nilai_morbi = 6
#             else:
#                 record.nilai_morbi = 0

#     @api.depends('nilai_body_cond', 'nilai_morbi')
#     def hitung_score_keswan(self):
#         for record in self:
#             record.score_keswan = record.nilai_body_cond + record.nilai_morbi


#     mpak = fields.Integer(string='Management Pakan', compute='hitung_nilai_mpak')
#     mkan = fields.Integer(string='Management Kandang', compute='hitung_nilai_mkan')
#     mpem = fields.Integer(string='Management Pemerahan', compute='hitung_nilai_mpem')
#     mbis = fields.Integer(string='Daya Saing Bisnis', compute='hitung_nilai_mbis')
#     mpel = fields.Integer(string='Pengolahan Limbah', compute='hitung_nilai_mpel')
#     mkes = fields.Integer(string='Kesehatan Hewan', compute='hitung_nilai_mkes')

#     total = fields.Integer('Total', compute='hitung_total_score')

#     @api.depends('score')
#     def hitung_nilai_mpak(self):
#         for record in self:
#             record.mpak = record.score_pakan

#     @api.depends('score')
#     def hitung_nilai_mkan(self):
#         for record in self:
#             record.mkan = record.score

#     @api.depends('score')
#     def hitung_nilai_mpem(self):
#         for record in self:
#             record.mpem = record.score_pemeliharaan

#     @api.depends('score')
#     def hitung_nilai_mbis(self):
#         for record in self:
#             record.mbis = record.score_daya_saing

#     @api.depends('score')
#     def hitung_nilai_mpel(self):
#         for record in self:
#             record.mpel = record.score_pengendalian_limbah

#     @api.depends('score')
#     def hitung_nilai_mkes(self):
#         for record in self:
#             record.mkes = record.score_keswan

#     @api.depends('mpak', 'mkan', 'mpem', 'mbis', 'mpel', 'mkes')
#     def hitung_total_score(self):
#         for record in self:
#             record.total = record.mpak + record.mkan + record.mpem + record.mbis + record.mpel + record.mkes

#     state = fields.Selection([
#         ('draft', 'Draft'),
#         ('submit', 'Submit'),
#         ('validate', 'Validasi'),
#     ], string='State', readonly=True, default='draft', required=True, tracking=True)

#     def func_submit(self):
#         if self.state == 'draft':
#             self.state = 'submit'

#     def func_validate(self):
#         if self.state == 'submit':
#             self.state = 'validate'

#     gdfp_line = fields.One2many('gdfp.sapi.line', 'gdfp_id', string='GDFP Sapi Lines')

#     total_all_tdn = fields.Float(string='Total', store=True, readonly=True, compute='_compute_total_gdfp_lines', tracking=4)

#     @api.depends('gdfp_line')
#     def _compute_total_gdfp_lines(self):
#         for entry in self:
#             entry.total_all_tdn = sum(line.total_tdn for line in entry.gdfp_line)

# class GDFPSapiLine(models.Model):
#     _name = 'gdfp.sapi.line'
#     _description = 'GDFP Sapi Line'

#     peternak_id = fields.Many2one('peternak.sapi', 'Peternak')
#     id_sapi = fields.Many2one('sapi', string='Sapi', domain="[('peternak_id', '=', peternak_id)]")
#     bobot_badan = fields.Float('Bobot Badan', related='id_sapi.bobot')
#     prod_susu_liter = fields.Float('Produksi Susu Liter')
#     status_reprod = fields.Selection([
#         ('bunting', 'Bunting'),
#         ('tdk_bunting', 'Tidak Bunting'),
#     ], string='Status Reproduksi', required=True)
#     gdfp_id = fields.Many2one('entry.gdfp', string='GDFP')

#     reproduksi = fields.Float('Reproduksi', compute='_compute_reproduksi_sapi', readonly=False)
#     hidup_pokok = fields.Float('Hidup Pokok', default=7.5, readonly=True)
#     produksi = fields.Float('Produksi', default=326, readonly=True)

#     hasil_tdn_hp = fields.Float('TDN HP', compute='hitung_nilai_tdn_hidup_pokok', readonly=True)
#     hasil_tdn_produksi = fields.Float('TDN Prod', compute='hitung_nilai_tdn_produksi', readonly=True)
#     hasil_tdn_reproduksi = fields.Float('TDN Rep', compute='hitung_nilai_tdn_reproduksi', readonly=True)
#     total_tdn = fields.Float('Total TDN', compute='hitung_total_tdn')

#     @api.depends('status_reprod')
#     def _compute_reproduksi_sapi(self):
#         for sapi in self:
#             if sapi.status_reprod == 'bunting':
#                 sapi.reproduksi = 2.4
#             elif sapi.status_reprod == 'tdk_bunting':
#                 sapi.reproduksi = 0

#     # tabel kebutuhan tdn pakan
#     @api.depends('bobot_badan', 'hidup_pokok')
#     def hitung_nilai_tdn_hidup_pokok(self):
#         for record in self:
#             record.hasil_tdn_hp = sum(line.bobot_badan * record.hidup_pokok for line in record)

#     @api.depends('prod_susu_liter', 'produksi')
#     def hitung_nilai_tdn_produksi(self):
#         for record in self:
#             record.hasil_tdn_produksi = sum(line.prod_susu_liter * record.produksi for line in record)

#     @api.depends('bobot_badan', 'reproduksi')
#     def hitung_nilai_tdn_reproduksi(self):
#         for record in self:
#             record.hasil_tdn_reproduksi = sum(line.bobot_badan * line.reproduksi for line in record)

#     @api.depends('hasil_tdn_hp', 'hasil_tdn_produksi', 'hasil_tdn_reproduksi')
#     def hitung_total_tdn(self):
#         for record in self:
#             record.total_tdn = record.hasil_tdn_hp + record.hasil_tdn_produksi + record.hasil_tdn_reproduksi

# class tabel_hijauan(models.Model):
#     _name = "tabel.hijauan"
#     _description = "Tabel Hijauan"
#     _inherit = ['mail.thread', 'mail.activity.mixin']
#     _rec_name = 'hijauan'

#     hijauan = fields.Char('Name')
#     nilai_bk_jerami = fields.Float('BK Jerami', digits=(3, 2))
#     nilai_tdn_jerami = fields.Float('TDN Jerami', digits=(3, 2))
#     nilai_bk_gajah = fields.Float('BK Gajah', digits=(3, 2))
#     nilai_tdn_gajah = fields.Float('TDN gajah', digits=(3, 2))
#     nilai_bk_tebon = fields.Float('BK Tebon', digits=(3, 2))
#     nilai_tdn_tebon = fields.Float('TDN Tebon', digits=(3, 2))
#     nilai_bk_tebu = fields.Float('BK Tebu', digits=(3, 2))
#     nilai_tdn_tebu = fields.Float('TDN Tebu', digits=(3, 2))
#     nilai_bk_pakchong = fields.Float('BK Pakchong', digits=(3, 2))
#     nilai_tdn_pakchong = fields.Float('TDN Pakchong', digits=(3, 2))
#     nilai_bk_odot = fields.Float('BK Odot', digits=(3, 2))
#     nilai_tdn_odot = fields.Float('TDN Odot', digits=(3, 2))
#     nilai_bk_lapang = fields.Float('BK Lapang', digits=(3, 2))
#     nilai_tdn_lapang = fields.Float('TDN Lapang', digits=(3, 2))
#     nilai_bk_hijauan1 = fields.Float('BK Hijauan1', digits=(3, 2))
#     nilai_tdn_hijauan1 = fields.Float('TDN Hijauan1', digits=(3, 2))
#     nilai_bk_hijauan2 = fields.Float('BK Hijauan2', digits=(3, 2))
#     nilai_tdn_hijauan2 = fields.Float('TDN Hijauan2', digits=(3, 2))
#     nilai_bk_hijauan3 = fields.Float('BK Hijauan3', digits=(3, 2))
#     nilai_tdn_hijauan3 = fields.Float('TDN Hijauan3', digits=(3, 2))
#     nilai_bk_hijauan4 = fields.Float('BK Hijauan4', digits=(3, 2))
#     nilai_tdn_hijauan4 = fields.Float('TDN Hijauan4', digits=(3, 2))
#     nilai_bk_hijauan5 = fields.Float('BK Hijauan5', digits=(3, 2))
#     nilai_tdn_hijauan5 = fields.Float('TDN Hijauan5', digits=(3, 2))

#     entry_gdfp_id = fields.Many2one('entry.gdfp', string='Entry GDFP')
#     # @api.onchange('nilai_bk_gajah', 'nilai_tdn_gajah')
#     # def _onchange_nilai_bk_tdn_gajah(self):
#     #     entry_gdfp = self.env['entry.gdfp'].search([], limit=1)  # Ambil satu record pertama
#     #     if entry_gdfp:
#     #         entry_gdfp.write({
#     #             'nilai_bk_gajah': self.nilai_bk_gajah,
#     #             'nilai_tdn_gajah': self.nilai_tdn_gajah,
#     #         })

# class tabel_konsentrat(models.Model):
#     _name = "tabel.konsentrat"
#     _description = "Tabel Konsentrat"
#     _inherit = ['mail.thread', 'mail.activity.mixin']
#     _rec_name = 'konsentrat'

#     konsentrat = fields.Char('Name')
#     nilai_bk_plus = fields.Float('BK Plus', default=0.88, digits=(3, 2))
#     nilai_tdn_plus = fields.Float('TDN Plus', default=0.69, digits=(3, 2))
#     nilai_bk_2a = fields.Float('BK Super 2A', default=0.87, digits=(3, 2))
#     nilai_tdn_2a = fields.Float('TDN Super 2A', default=0.62, digits=(3, 2))
#     nilai_bk_mapan = fields.Float('BK Maju Mapan', default=0.87, digits=(3, 2))
#     nilai_tdn_mapan = fields.Float('TDN Maju Mapan', default=0.66, digits=(3, 2))
#     nilai_bk_feed = fields.Float('BK Mix Feed', default=0.89, digits=(3, 2))
#     nilai_tdn_feed = fields.Float('TDN Mix Feed', default=0.78, digits=(3, 2))
#     nilai_bk_konsentrat1 = fields.Float('BK Konsentrat1', digits=(3, 2))
#     nilai_tdn_konsentrat1 = fields.Float('TDN Konsentrat1', digits=(3, 2))
#     nilai_bk_konsentrat2 = fields.Float('BK Konsentrat2', digits=(3, 2))
#     nilai_tdn_konsentrat2 = fields.Float('TDN Konsentrat2', digits=(3, 2))
#     nilai_bk_konsentrat3 = fields.Float('BK Konsentrat3', digits=(3, 2))
#     nilai_tdn_konsentrat3 = fields.Float('TDN Konsentrat3', digits=(3, 2))
#     nilai_bk_konsentrat4 = fields.Float('BK Konsentrat4', digits=(3, 2))
#     nilai_tdn_konsentrat4 = fields.Float('TDN Konsentrat4', digits=(3, 2))
#     nilai_bk_konsentrat5 = fields.Float('BK Konsentrat5', digits=(3, 2))
#     nilai_tdn_konsentrat5 = fields.Float('TDN Konsentrat5', digits=(3, 2))

#     konsentrat_gdfp_id = fields.Many2one('entry.gdfp', string='Konsentrat GDFP')

# class tabel_pakan_tambah(models.Model):
#     _name = "tabel.pakan.tambah"
#     _description = "Tabel Pakan Tambah"
#     _inherit = ['mail.thread', 'mail.activity.mixin']
#     _rec_name = 'pakan_tambah'

#     pakan_tambah = fields.Char('Name')
#     nilai_bk_selep = fields.Float('BK Roti Selep', default=0.87, digits=(3, 2))
#     nilai_tdn_selep = fields.Float('TDN Roti Selep', default=0.87, digits=(3, 2))
#     nilai_bk_tawar = fields.Float('BK Roti Tawar', default=0.87, digits=(3, 2))
#     nilai_tdn_tawar = fields.Float('TDN Roti Tawar', default=0.94, digits=(3, 2))
#     nilai_bk_singkong = fields.Float('BK Singkong', default=0.30, digits=(3, 2))
#     nilai_tdn_singkong = fields.Float('TDN Singkong', default=0.88, digits=(3, 2))
#     nilai_bk_gamblong = fields.Float('BK Gamblong', default=0.26, digits=(3, 2))
#     nilai_tdn_gamblong = fields.Float('TDN Gamblong', default=0.95, digits=(3, 2))
#     nilai_bk_bir = fields.Float('BK Bir', default=0.27, digits=(3, 2))
#     nilai_tdn_bir = fields.Float('TDN Bir', default=0.87, digits=(3, 2))
#     nilai_bk_tahu = fields.Float('BK Tahu', default=0.27, digits=(3, 2))
#     nilai_tdn_tahu = fields.Float('TDN Tahu', default=0.85, digits=(3, 2))
#     nilai_bk_tambah1 = fields.Float('BK Tambah1', digits=(3, 2))
#     nilai_tdn_tambah1 = fields.Float('TDN Tambah1', digits=(3, 2))
#     nilai_bk_tambah2 = fields.Float('BK Tambah2', digits=(3, 2))
#     nilai_tdn_tambah2 = fields.Float('TDN Tambah2', digits=(3, 2))
#     nilai_bk_tambah3 = fields.Float('BK Tambah3', digits=(3, 2))
#     nilai_tdn_tambah3 = fields.Float('TDN Tambah3', digits=(3, 2))
#     nilai_bk_tambah4 = fields.Float('BK Tambah4', digits=(3, 2))
#     nilai_tdn_tambah4 = fields.Float('TDN Tambah4', digits=(3, 2))
#     nilai_bk_tambah5 = fields.Float('BK Tambah5', digits=(3, 2))
#     nilai_tdn_tambah5 = fields.Float('TDN Tambah5', digits=(3, 2))

#     pakan_tambah_gdfp_id = fields.Many2one('entry.gdfp', string='Pakan Tambah GDFP')