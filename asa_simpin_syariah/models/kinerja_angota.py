from odoo import models, fields, api

class kinerja_anggota(models.Model):
    _name = "kinerja.anggota"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Kinerja Anggota"
    _rec_name = 'anggota_id'

    anggota_id = fields.Many2one('simpin_syariah.member', string='Nama Anggota')
    kode_anggota = fields.Char('ID Anggota', related='anggota_id.kode_anggota')
    jabatan_id = fields.Char('Jabatan', compute='_compute_jabatan_id')
    aggt = fields.Boolean('Anggota')
    ko = fields.Boolean('KO')
    ka = fields.Boolean('KA')

    @api.depends('anggota_id')
    def _compute_jabatan_id(self):
        for record in self:
            record.jabatan_id = record.anggota_id.jabatan_id.jabatan if record.anggota_id and record.anggota_id.jabatan_id else False

    #kompetensi bidang organisasi
    #Anggota
    org_dsr = fields.Integer('Organisasi Dasar', compute='_hitung_nilai_org_dsr')
    org_dsr_level = fields.Selection([
        ('1', 'Pemula'),
        ('2', 'Dasar'),
        ('3', 'Terampil'),
        ('4', 'Mahir'),
        ('5', 'Ahli')
    ], string='Level Organisais Dasar', help='Informasi:\n- Pemula : Tidak mengetahui apa defenisi koperasi\n- Dasar : Mengetahui sedikit arti koperasi\n- Terampil : Memahami defenisi koperasi dan maknanya')
    bdy_org = fields.Integer('Budaya Organisasi', compute='_hitung_nilai_bdy_org')
    bdy_org_level = fields.Selection([
        ('1', 'Pemula'),
        ('2', 'Dasar'),
        ('3', 'Terampil'),
        ('4', 'Mahir'),
        ('5', 'Ahli')
    ], string='Level Budaya Organisasi')
    jti_diri = fields.Integer('Jati Diri Koperasi', compute='_hitung_nilai_jti_diri')
    jti_diri_level = fields.Selection([
        ('1', 'Pemula'),
        ('2', 'Dasar'),
        ('3', 'Terampil'),
        ('4', 'Mahir'),
        ('5', 'Ahli')
    ], string='Level Jati Diri Koperasi')
    hak_kwjbn = fields.Integer('Hak & Kewajiban', compute='_hitung_nilai_hak_kwjbn')
    hak_kwjbn_level = fields.Selection([
        ('1', 'Pemula'),
        ('2', 'Dasar'),
        ('3', 'Terampil'),
        ('4', 'Mahir'),
        ('5', 'Ahli')
    ], string='Level Hak & Kewajiban')

    standar_skor = fields.Selection([
        ('1', '1'),
        ('2', '2'),
        ('3', '3')
    ], string='Standar Skor', default='2', tracking=True)
    nilai_skor = fields.Float('Nilai Skor', compute='_compute_nilai_skor')
    nilai_skor_bdy = fields.Float('Nilai Skor', compute='_compute_nilai_skor_bdy')
    nilai_skor_jti = fields.Float('Nilai Skor', compute='_compute_nilai_skor_jti')
    nilai_skor_hak = fields.Float('Nilai Skor', compute='_compute_nilai_skor_hak')
    # total_nilai_skor = fields
    average_nilai_skor = fields.Float('Nilai Skor Rata', compute='_compute_average_nilai_skor')
    semester = fields.Selection([
        ('1', 'Ganjil'),
        ('2', 'Genap'),
    ], string='Semester')
    tgl_semester = fields.Datetime('Tanggal')

    @api.depends('nilai_skor', 'nilai_skor_bdy', 'nilai_skor_jti', 'nilai_skor_hak')
    def _compute_average_nilai_skor(self):
        for record in self:
            total_nilai_skor = record.nilai_skor + record.nilai_skor_bdy + record.nilai_skor_jti + record.nilai_skor_hak
            count = 4  # Jumlah field yang dihitung rata-ratanya

            if count > 0:
                record.average_nilai_skor = total_nilai_skor / count
            else:
                record.average_nilai_skor = 0.0

    @api.depends('org_dsr', 'standar_skor')
    def _compute_nilai_skor(self):
        for record in self:
            if record.standar_skor:
                record.nilai_skor = record.org_dsr / int(record.standar_skor)
            else:
                record.nilai_skor = 0.0

    @api.depends('bdy_org', 'standar_skor')
    def _compute_nilai_skor_bdy(self):
        for record in self:
            if record.standar_skor:
                record.nilai_skor_bdy = record.bdy_org / int(record.standar_skor)
            else:
                record.nilai_skor_bdy = 0.0

    @api.depends('jti_diri', 'standar_skor')
    def _compute_nilai_skor_jti(self):
        for record in self:
            if record.standar_skor:
                record.nilai_skor_jti = record.jti_diri / int(record.standar_skor)
            else:
                record.nilai_skor_jti = 0.0

    @api.depends('hak_kwjbn', 'standar_skor')
    def _compute_nilai_skor_hak(self):
        for record in self:
            if record.standar_skor:
                record.nilai_skor_hak = record.hak_kwjbn / int(record.standar_skor)
            else:
                record.nilai_skor_hak = 0.0

    @api.depends('org_dsr_level')
    def _hitung_nilai_org_dsr(self):
        for record in self:
            if record.org_dsr_level == '1':
                record.org_dsr = 1
            elif record.org_dsr_level == '2':
                record.org_dsr = 2
            elif record.org_dsr_level == '3':
                record.org_dsr = 3
            elif record.org_dsr_level == '4':
                record.org_dsr = 4
            elif record.org_dsr_level == '5':
                record.org_dsr = 5
            else:
                record.org_dsr = 0

    @api.depends('bdy_org_level')
    def _hitung_nilai_bdy_org(self):
        for record in self:
            if record.bdy_org_level == '1':
                record.bdy_org = 1
            elif record.bdy_org_level == '2':
                record.bdy_org = 2
            elif record.bdy_org_level == '3':
                record.bdy_org = 3
            elif record.bdy_org_level == '4':
                record.bdy_org = 4
            elif record.bdy_org_level == '5':
                record.bdy_org = 5
            else:
                record.bdy_org = 0

    @api.depends('jti_diri_level')
    def _hitung_nilai_jti_diri(self):
        for record in self:
            if record.jti_diri_level == '1':
                record.jti_diri = 1
            elif record.jti_diri_level == '2':
                record.jti_diri = 2
            elif record.jti_diri_level == '3':
                record.jti_diri = 3
            elif record.jti_diri_level == '4':
                record.jti_diri = 4
            elif record.jti_diri_level == '5':
                record.jti_diri = 5
            else:
                record.jti_diri = 0

    @api.depends('hak_kwjbn_level')
    def _hitung_nilai_hak_kwjbn(self):
        for record in self:
            if record.hak_kwjbn_level == '1':
                record.hak_kwjbn = 1
            elif record.hak_kwjbn_level == '2':
                record.hak_kwjbn = 2
            elif record.hak_kwjbn_level == '3':
                record.hak_kwjbn = 3
            elif record.hak_kwjbn_level == '4':
                record.hak_kwjbn = 4
            elif record.hak_kwjbn_level == '5':
                record.hak_kwjbn = 5
            else:
                record.hak_kwjbn = 0

    #KA
    din_kel = fields.Integer('Dinamika Kelompok')
    din_kel_level = fields.Selection([
        ('1', 'Pemula'),
        ('2', 'Dasar'),
        ('3', 'Terampil'),
        ('4', 'Mahir'),
        ('5', 'Ahli')
    ], string='Level Dinamika Kelompok')
    kmnksi = fields.Integer('Komunikasi')
    kmnksi_level = fields.Selection([
        ('1', 'Pemula'),
        ('2', 'Dasar'),
        ('3', 'Terampil'),
        ('4', 'Mahir'),
        ('5', 'Ahli')
    ], string='Level Komunikasi')
    mod_sos = fields.Integer('Modal Sosial')
    mod_sos_level = fields.Selection([
        ('1', 'Pemula'),
        ('2', 'Dasar'),
        ('3', 'Terampil'),
        ('4', 'Mahir'),
        ('5', 'Ahli')
    ], string='Level Modal Sosial')
    motivasi = fields.Integer('Motivasi')
    motivasi_level = fields.Selection([
        ('1', 'Pemula'),
        ('2', 'Dasar'),
        ('3', 'Terampil'),
        ('4', 'Mahir'),
        ('5', 'Ahli')
    ], string='Level Motivasi')

    @api.depends('din_kel_level')
    def _hitung_nilai_din_kel(self):
        for record in self:
            if record.din_kel_level == '1':
                record.din_kel = 1
            elif record.din_kel_level == '2':
                record.din_kel = 2
            elif record.din_kel_level == '3':
                record.din_kel = 3
            elif record.din_kel_level == '4':
                record.din_kel = 4
            elif record.din_kel_level == '5':
                record.din_kel = 5
            else:
                record.din_kel = 0

    @api.depends('kmnksi_level')
    def _hitung_nilai_kmnksi(self):
        for record in self:
            if record.kmnksi_level == '1':
                record.kmnksi = 1
            elif record.kmnksi_level == '2':
                record.kmnksi = 2
            elif record.kmnksi_level == '3':
                record.kmnksi = 3
            elif record.kmnksi_level == '4':
                record.kmnksi = 4
            elif record.kmnksi_level == '5':
                record.kmnksi = 5
            else:
                record.kmnksi = 0

    @api.depends('mod_sos_level')
    def _hitung_nilai_mod_sos(self):
        for record in self:
            if record.mod_sos_level == '1':
                record.mod_sos = 1
            elif record.mod_sos_level == '2':
                record.mod_sos = 2
            elif record.mod_sos_level == '3':
                record.mod_sos = 3
            elif record.mod_sos_level == '4':
                record.mod_sos = 4
            elif record.mod_sos_level == '5':
                record.mod_sos = 5
            else:
                record.mod_sos = 0

    @api.depends('motivasi_level')
    def _hitung_nilai_motivasi(self):
        for record in self:
            if record.motivasi_level == '1':
                record.motivasi = 1
            elif record.motivasi_level == '2':
                record.motivasi = 2
            elif record.motivasi_level == '3':
                record.motivasi = 3
            elif record.motivasi_level == '4':
                record.motivasi = 4
            elif record.motivasi_level == '5':
                record.motivasi = 5
            else:
                record.motivasi = 0

    #KO
    kepem_level = fields.Selection([
        ('1', 'Pemula'),
        ('2', 'Dasar'),
        ('3', 'Terampil'),
        ('4', 'Mahir'),
        ('5', 'Ahli')
    ], string='Level Kepemimpinan')
    kepem = fields.Integer('Kepemimpinan', compute='_hitung_nilai_kepem')
    dsr_org_level = fields.Selection([
        ('1', 'Pemula'),
        ('2', 'Dasar'),
        ('3', 'Terampil'),
        ('4', 'Mahir'),
        ('5', 'Ahli')
    ], string='Level TDO')
    dsr_org = fields.Integer('Teori Dasar Organisasi', compute='_hitung_nilai_dsr_org')
    mngmn_level = fields.Selection([
        ('1', 'Pemula'),
        ('2', 'Dasar'),
        ('3', 'Terampil'),
        ('4', 'Mahir'),
        ('5', 'Ahli')
    ], string='Level Management')
    mngmn = fields.Integer('Management', compute='_hitung_nilai_mngmn')
    anal_lapkeu_level = fields.Selection([
        ('1', 'Pemula'),
        ('2', 'Dasar'),
        ('3', 'Terampil'),
        ('4', 'Mahir'),
        ('5', 'Ahli')
    ], string='Level Analisa Lapkeu')
    anal_lapkeu = fields.Integer('Analisa Singkat Laporan Keuangan', compute='_hitung_nilai_anal_lapkeu')
    komit_level = fields.Selection([
        ('1', 'Pemula'),
        ('2', 'Dasar'),
        ('3', 'Terampil'),
        ('4', 'Mahir'),
        ('5', 'Ahli')
    ], string='Level komitmen')
    komit = fields.Integer('Komitmen', compute='_hitung_nilai_komit')
    sis_org_level = fields.Selection([
        ('1', 'Pemula'),
        ('2', 'Dasar'),
        ('3', 'Terampil'),
        ('4', 'Mahir'),
        ('5', 'Ahli')
    ], string='Level Sistem Organsisasi')
    sis_org = fields.Integer('Sistem Dalam Organisasi', compute='_hitung_nilai_sis_org')

    @api.depends('kepem_level')
    def _hitung_nilai_kepem(self):
        for record in self:
            if record.kepem_level == '1':
                record.kepem = 1
            elif record.kepem_level == '2':
                record.kepem = 2
            elif record.kepem_level == '3':
                record.kepem = 3
            elif record.kepem_level == '4':
                record.kepem = 4
            elif record.kepem_level == '5':
                record.kepem = 5
            else:
                record.kepem = 0

    @api.depends('mngmn_level')
    def _hitung_nilai_mngmn(self):
        for record in self:
            if record.mngmn_level == '1':
                record.mngmn = 1
            elif record.mngmn_level == '2':
                record.mngmn = 2
            elif record.mngmn_level == '3':
                record.mngmn = 3
            elif record.mngmn_level == '4':
                record.mngmn = 4
            elif record.mngmn_level == '5':
                record.mngmn = 5
            else:
                record.mngmn = 0


    @api.depends('dsr_org_level')
    def _hitung_nilai_dsr_org(self):
        for record in self:
            if record.dsr_org_level == '1':
                record.dsr_org = 1
            elif record.dsr_org_level == '2':
                record.dsr_org = 2
            elif record.dsr_org_level == '3':
                record.dsr_org = 3
            elif record.dsr_org_level == '4':
                record.dsr_org = 4
            elif record.dsr_org_level == '5':
                record.dsr_org = 5
            else:
                record.dsr_org = 0

    @api.depends('anal_lapkeu_level')
    def _hitung_nilai_anal_lapkeu(self):
        for record in self:
            if record.anal_lapkeu_level == '1':
                record.anal_lapkeu = 1
            elif record.anal_lapkeu_level == '2':
                record.anal_lapkeu = 2
            elif record.anal_lapkeu_level == '3':
                record.anal_lapkeu = 3
            elif record.anal_lapkeu_level == '4':
                record.anal_lapkeu = 4
            elif record.anal_lapkeu_level == '5':
                record.anal_lapkeu = 5
            else:
                record.anal_lapkeu = 0

    @api.depends('komit_level')
    def _hitung_nilai_komit(self):
        for record in self:
            if record.komit_level == '1':
                record.komit = 1
            elif record.komit_level == '2':
                record.komit = 2
            elif record.komit_level == '3':
                record.komit = 3
            elif record.komit_level == '4':
                record.komit = 4
            elif record.komit_level == '5':
                record.komit = 5
            else:
                record.komit = 0

    @api.depends('sis_org_level')
    def _hitung_nilai_sis_org(self):
        for record in self:
            if record.sis_org_level == '1':
                record.sis_org = 1
            elif record.sis_org_level == '2':
                record.sis_org = 2
            elif record.sis_org_level == '3':
                record.sis_org = 3
            elif record.sis_org_level == '4':
                record.sis_org = 4
            elif record.sis_org_level == '5':
                record.sis_org = 5
            else:
                record.sis_org = 0

    nilai_kompetensi = fields.Integer('Nilai Kompetensi')
    total_kompetensi = fields.Integer('Total Kompetensi')

    #Bidang Teknisi GDFP
    mpak = fields.Integer('Management Pakan')
    mkan = fields.Integer('Management Kandang')
    mpem = fields.Integer(string='Management Pemerahan')
    mbis = fields.Integer(string='Daya Saing Bisnis')
    mpel = fields.Integer(string='Pengolahan Limbah')
    mkes = fields.Integer(string='Kesehatan Hewan')
    total = fields.Integer('Total')

    @api.onchange('anggota_id')
    def _onchange_anggota_id(self):
        if not self.anggota_id:
            self.mpak = 0
            self.mkan = 0
            self.mpem = 0
            self.mbis = 0
            self.mpel = 0
            self.mkes = 0
            self.total = 0
        else:
            entry_gdfp = self.env['entry.gdfp'].search([('anggota_id', '=', self.anggota_id.id)], limit=1)
            if entry_gdfp:
                self.mpak = entry_gdfp.mpak
                self.mkan = entry_gdfp.mkan
                self.mpem = entry_gdfp.mpem
                self.mbis = entry_gdfp.mbis
                self.mpel = entry_gdfp.mpel
                self.mkes = entry_gdfp.mkes
                self.total = entry_gdfp.total
            else:
                self.mpak = 0
                self.mkan = 0
                self.mpem = 0
                self.mbis = 0
                self.mpel = 0
                self.mkes = 0
                self.total = 0

    @api.onchange('jabatan_id')
    def _onchange_jabatan_id(self):
        if self.jabatan_id == 'ANGGOTA':
            self.aggt = True
            self.ka = False
            self.ko = False
        elif self.jabatan_id == 'KOORDINATOR (KO)':
            self.aggt = False
            self.ka = False
            self.ko = True
        elif self.jabatan_id == 'KELOMPOK (KA)':
            self.aggt = False
            self.ka = True
            self.ko = False
        else:
            self.aggt = False
            self.ka = False
            self.ko = False

    #pengembangan sdma
    studi_banding_level = fields.Selection([
        ('1', 'Sesuai Kompetensi A'),
        ('2', 'Sesuai Kompetensi A'),
        ('3', 'Sesuai Kompetensi KA'),
        ('4', 'Sesuai Kompetensi KO'),
        ('5', 'Sesuai Kompetensi KO')
    ], string='Level Studi Banding')
    studi_banding = fields.Integer('Studi Banding', compute='_hitung_nilai_studi_banding')
    peny_rutin_level = fields.Selection([
        ('1', 'Sesuai Kompetensi A'),
        ('2', 'Sesuai Kompetensi A'),
        ('3', 'Sesuai Kompetensi KA'),
        ('4', 'Sesuai Kompetensi KO'),
        ('5', 'Sesuai Kompetensi KO')
    ], string='Level Penyuluhan Rutin')
    peny_rutin = fields.Integer('Penyuluhan Rutin', compute='_hitung_nilai_peny_rutin')
    peny_segmen_level = fields.Selection([
        ('1', 'Sesuai Kompetensi A'),
        ('2', 'Sesuai Kompetensi A'),
        ('3', 'Sesuai Kompetensi KA'),
        ('4', 'Sesuai Kompetensi KO'),
        ('5', 'Sesuai Kompetensi KO')
    ], string='Level Penyuluhan Segmentasi')
    peny_segmen = fields.Integer('Penyuluhan Segmentasi', compute='_hitung_nilai_peny_segmen')
    pemilik_level = fields.Selection([
        ('1', 'Sesuai Kompetensi A'),
        ('2', 'Sesuai Kompetensi A'),
        ('3', 'Sesuai Kompetensi KA'),
        ('4', 'Sesuai Kompetensi KO'),
        ('5', 'Sesuai Kompetensi KO')
    ], string='Level Pemilik')
    pemilik = fields.Integer('Pemilik', compute='_hitung_nilai_pemilik')
    peng_jasa_level = fields.Selection([
        ('1', 'Sesuai Kompetensi A'),
        ('2', 'Sesuai Kompetensi A'),
        ('3', 'Sesuai Kompetensi KA'),
        ('4', 'Sesuai Kompetensi KO'),
        ('5', 'Sesuai Kompetensi KO')
    ], string='Level Pengguna Jasa')
    peng_jasa = fields.Integer('Pemilik', compute='_hitung_nilai_peng_jasa')
    pend_teknis_level = fields.Selection([
        ('1', 'Sesuai Kompetensi A'),
        ('2', 'Sesuai Kompetensi A'),
        ('3', 'Sesuai Kompetensi KA'),
        ('4', 'Sesuai Kompetensi KO'),
        ('5', 'Sesuai Kompetensi KO')
    ], string='Level Pendamping Teknis')
    pend_teknis = fields.Integer('Pendamping Teknis', compute='_hitung_nilai_pend_teknis')
    peng_sdm = fields.Integer('Pengembangan SDM Anggota Khusus')
    total_peng_sdma = fields.Integer('Total Pengembangan SDMA')

    @api.depends('studi_banding_level')
    def _hitung_nilai_studi_banding(self):
        for record in self:
            if record.studi_banding_level == '1':
                record.studi_banding = 1
            elif record.studi_banding_level == '2':
                record.studi_banding = 2
            elif record.studi_banding_level == '3':
                record.studi_banding = 3
            elif record.studi_banding_level == '4':
                record.studi_banding = 4
            elif record.studi_banding_level == '5':
                record.studi_banding = 5
            else:
                record.studi_banding = 0

    @api.depends('peny_rutin_level')
    def _hitung_nilai_peny_rutin(self):
        for record in self:
            if record.peny_rutin_level == '1':
                record.peny_rutin = 1
            elif record.peny_rutin_level == '2':
                record.peny_rutin = 2
            elif record.peny_rutin_level == '3':
                record.peny_rutin = 3
            elif record.peny_rutin_level == '4':
                record.peny_rutin = 4
            elif record.peny_rutin_level == '5':
                record.peny_rutin = 5
            else:
                record.peny_rutin = 0

    @api.depends('peny_segmen_level')
    def _hitung_nilai_peny_segmen(self):
        for record in self:
            if record.peny_segmen_level == '1':
                record.peny_segmen = 1
            elif record.peny_segmen_level == '2':
                record.peny_segmen = 2
            elif record.peny_segmen_level == '3':
                record.peny_segmen = 3
            elif record.peny_segmen_level == '4':
                record.peny_segmen = 4
            elif record.peny_segmen_level == '5':
                record.peny_segmen = 5
            else:
                record.peny_segmen = 0

    @api.depends('pemilik_level')
    def _hitung_nilai_pemilik(self):
        for record in self:
            if record.pemilik_level == '1':
                record.pemilik = 1
            elif record.pemilik_level == '2':
                record.pemilik = 2
            elif record.pemilik_level == '3':
                record.pemilik = 3
            elif record.pemilik_level == '4':
                record.pemilik = 4
            elif record.pemilik_level == '5':
                record.pemilik = 5
            else:
                record.pemilik = 0

    @api.depends('peng_jasa_level')
    def _hitung_nilai_peng_jasa(self):
        for record in self:
            if record.peng_jasa_level == '1':
                record.peng_jasa = 1
            elif record.peng_jasa_level == '2':
                record.peng_jasa = 2
            elif record.peng_jasa_level == '3':
                record.peng_jasa = 3
            elif record.peng_jasa_level == '4':
                record.peng_jasa = 4
            elif record.peng_jasa_level == '5':
                record.peng_jasa = 5
            else:
                record.peng_jasa = 0

    @api.depends('pend_teknis_level')
    def _hitung_nilai_pend_teknis(self):
        for record in self:
            if record.pend_teknis_level == '1':
                record.pend_teknis = 1
            elif record.pend_teknis_level == '2':
                record.pend_teknis = 2
            elif record.pend_teknis_level == '3':
                record.pend_teknis = 3
            elif record.pend_teknis_level == '4':
                record.pend_teknis = 4
            elif record.pend_teknis_level == '5':
                record.pend_teknis = 5
            else:
                record.pend_teknis = 0

    #pendidikan
    kriteria = fields.Selection([
        ('sd', '>SD & Paket A'),
        ('pkt1', 'Paket B'),
        ('smp', 'SMP'),
        ('pkt2', 'Paket C'),
        ('sma', 'SMA/D1'),
        ('d3', 'D3'),
        ('s1', 'S1'),
        ('s2', 'S2'),
    ], string='Kriteria')
    nilai_kriteria = fields.Float('Nilai', compute='_hitung_nilai')

    @api.depends('kriteria')
    def _hitung_nilai(self):
        for record in self:
            if record.kriteria == 'sd':
                record.nilai_kriteria = 1
            elif record.kriteria == 'pkt1':
                record.nilai_kriteria = 1.5
            elif record.kriteria == 'smp':
                record.nilai_kriteria = 2
            elif record.kriteria == 'pkt2':
                record.nilai_kriteria = 2.5
            elif record.kriteria == 'sma':
                record.nilai_kriteria = 3
            elif record.kriteria == 'd3':
                record.nilai_kriteria = 3.5
            elif record.kriteria == 's1':
                record.nilai_kriteria = 4
            elif record.kriteria == 's2':
                record.nilai_kriteria = 5
            else:
                record.nilai_kriteria = 0

    #kehadiran
    rat = fields.Selection([
        ('1', 'Hadir 50 %, aktif'),
        ('2', 'Hadir 75%, aktif'),
        ('3', 'Hadir 100%, aktif'),
        ('4', 'Hadir 100% dan memberikan saran untuk perbaikan koperasi'),
        ('5', 'Kehadiran 100%, aktif dan pengemukakan pendapat dan saran untuk perbaikan program koperasi'),
    ], string='RAT')
    pra_rat = fields.Selection([
        ('1', 'Hadir 50 %, aktif'),
        ('2', 'Hadir 75%, aktif'),
        ('3', 'Hadir 100%, aktif'),
        ('4', 'Hadir 100% dan memberikan saran untuk perbaikan koperasi'),
        ('5', 'Kehadiran 100%, aktif dan pengemukakan pendapat dan saran untuk perbaikan program koperasi'),
    ], string='Pra RAT')
    rapat_lain = fields.Selection([
        ('1', 'Hadir 50 %, aktif'),
        ('2', 'Hadir 75%, aktif'),
        ('3', 'Hadir 100%, aktif'),
        ('4', 'Hadir 100% dan memberikan saran untuk perbaikan koperasi'),
        ('5', 'Kehadiran 100%, aktif dan pengemukakan pendapat dan saran untuk perbaikan program koperasi'),
    ], string='Rapat Lain')
    kehadiran_pelatihan = fields.Selection([
        ('1', 'Hadir 50 %, aktif'),
        ('2', 'Hadir 75%, aktif'),
        ('3', 'Hadir 100%, aktif'),
        ('4', 'Hadir 100% dan memberikan saran untuk perbaikan koperasi'),
        ('5', 'Kehadiran 100%, aktif dan pengemukakan pendapat dan saran untuk perbaikan program koperasi'),
    ], string='Pelatihan')
    kehadiran_studi_banding = fields.Selection([
        ('1', 'Hadir 50 %, aktif'),
        ('2', 'Hadir 75%, aktif'),
        ('3', 'Hadir 100%, aktif'),
        ('4', 'Hadir 100% dan memberikan saran untuk perbaikan koperasi'),
        ('5', 'Kehadiran 100%, aktif dan pengemukakan pendapat dan saran untuk perbaikan program koperasi'),
    ], string='Studi Banding')
    pertemuan_rutin = fields.Selection([
        ('1', 'Hadir 50 %, aktif'),
        ('2', 'Hadir 75%, aktif'),
        ('3', 'Hadir 100%, aktif'),
        ('4', 'Hadir 100% dan memberikan saran untuk perbaikan koperasi'),
        ('5', 'Kehadiran 100%, aktif dan pengemukakan pendapat dan saran untuk perbaikan program koperasi'),
    ], string='Pertemuan Rutin')
    pertemuan_segmentasi = fields.Selection([
        ('1', 'Hadir 50 %, aktif'),
        ('2', 'Hadir 75%, aktif'),
        ('3', 'Hadir 100%, aktif'),
        ('4', 'Hadir 100% dan memberikan saran untuk perbaikan koperasi'),
        ('5', 'Kehadiran 100%, aktif dan pengemukakan pendapat dan saran untuk perbaikan program koperasi'),
    ], string='Pertemuan Tersegmentasi')
    pemiliks = fields.Selection([
        ('1', 'Hadir 50 %, aktif'),
        ('2', 'Hadir 75%, aktif'),
        ('3', 'Hadir 100%, aktif'),
        ('4', 'Hadir 100% dan memberikan saran untuk perbaikan koperasi'),
        ('5', 'Kehadiran 100%, aktif dan pengemukakan pendapat dan saran untuk perbaikan program koperasi'),
    ], string='Pemilik')
    pengguna_jasas = fields.Selection([
        ('1', 'Hadir 50 %, aktif'),
        ('2', 'Hadir 75%, aktif'),
        ('3', 'Hadir 100%, aktif'),
        ('4', 'Hadir 100% dan memberikan saran untuk perbaikan koperasi'),
        ('5', 'Kehadiran 100%, aktif dan pengemukakan pendapat dan saran untuk perbaikan program koperasi'),
    ], string='Pengguna Jasa')
    pendamping_teknis = fields.Selection([
        ('1', 'Hadir 50 %, aktif'),
        ('2', 'Hadir 75%, aktif'),
        ('3', 'Hadir 100%, aktif'),
        ('4', 'Hadir 100% dan memberikan saran untuk perbaikan koperasi'),
        ('5', 'Kehadiran 100%, aktif dan pengemukakan pendapat dan saran untuk perbaikan program koperasi'),
    ], string='Pendamping Teknis')

    nilai_rat = fields.Float('Nilai RAT', compute='_nilai_rat')
    nilai_pra_rat = fields.Float('Nilai Pra RAT', compute='_nilai_pra_rat')
    nilai_rapat_lain = fields.Float('Nilai Rapat lain', compute='_nilai_rapat_lain')
    nilai_kehadiran_pelatihan = fields.Float('Nilai Kehadiran Pelatihan', compute='_nilai_kehadiran_pelatihan')
    nilai_kehadiran_studi_banding = fields.Float('Nilai Kehadiran Studi Banding', compute='_nilai_kehadiran_studi_banding')
    nilai_pertemuan_rutin = fields.Float('Nilai Pertemuan Rutin', compute='_nilai_pertemuan_rutin')
    nilai_pertemuan_segmentasi = fields.Float('Nilai Pertemuan Segmentasi', compute='_nilai_pertemuan_segmentasi')
    nilai_pemiliks = fields.Float('Nilai Pemilik', compute='_nilai_pemiliks')
    nilai_pengguna_jasas = fields.Float('Nilai Pengguna Jasa', compute='_nilai_pengguna_jasas')
    nilai_pendamping_teknis = fields.Float('Nilai Pendamping Teknis', compute='_nilai_pendamping_teknis')

    @api.depends('rat')
    def _nilai_rat(self):
        for record in self:
            if record.rat == '1':
                record.nilai_rat = 1
            elif record.rat == '2':
                record.nilai_rat = 2
            elif record.rat == '3':
                record.nilai_rat = 3
            elif record.rat == '4':
                record.nilai_rat = 4
            elif record.rat == '5':
                record.nilai_rat = 5
            else:
                record.nilai_rat = 0

    @api.depends('pra_rat')
    def _nilai_pra_rat(self):
        for record in self:
            if record.pra_rat == '1':
                record.nilai_pra_rat = 1
            elif record.pra_rat == '2':
                record.nilai_pra_rat = 2
            elif record.pra_rat == '3':
                record.nilai_pra_rat = 3
            elif record.pra_rat == '4':
                record.nilai_pra_rat = 4
            elif record.pra_rat == '5':
                record.nilai_pra_rat = 5
            else:
                record.nilai_pra_rat = 0

    @api.depends('rapat_lain')
    def _nilai_rapat_lain(self):
        for record in self:
            if record.rapat_lain == '1':
                record.nilai_rapat_lain = 1
            elif record.rapat_lain == '2':
                record.nilai_rapat_lain = 2
            elif record.rapat_lain == '3':
                record.nilai_rapat_lain = 3
            elif record.rapat_lain == '4':
                record.nilai_rapat_lain = 4
            elif record.rapat_lain == '5':
                record.nilai_rapat_lain = 5
            else:
                record.nilai_rapat_lain = 0

    @api.depends('kehadiran_pelatihan')
    def _nilai_kehadiran_pelatihan(self):
        for record in self:
            if record.kehadiran_pelatihan == '1':
                record.nilai_kehadiran_pelatihan = 1
            elif record.kehadiran_pelatihan == '2':
                record.nilai_kehadiran_pelatihan = 2
            elif record.kehadiran_pelatihan == '3':
                record.nilai_kehadiran_pelatihan = 3
            elif record.kehadiran_pelatihan == '4':
                record.nilai_kehadiran_pelatihan = 4
            elif record.kehadiran_pelatihan == '5':
                record.nilai_kehadiran_pelatihan = 5
            else:
                record.nilai_kehadiran_pelatihan = 0

    @api.depends('kehadiran_studi_banding')
    def _nilai_kehadiran_studi_banding(self):
        for record in self:
            if record.kehadiran_studi_banding == '1':
                record.nilai_kehadiran_studi_banding = 1
            elif record.kehadiran_studi_banding == '2':
                record.nilai_kehadiran_studi_banding = 2
            elif record.kehadiran_studi_banding == '3':
                record.nilai_kehadiran_studi_banding = 3
            elif record.kehadiran_studi_banding == '4':
                record.nilai_kehadiran_studi_banding = 4
            elif record.kehadiran_studi_banding == '5':
                record.nilai_kehadiran_studi_banding = 5
            else:
                record.nilai_kehadiran_studi_banding = 0

    @api.depends('pertemuan_rutin')
    def _nilai_pertemuan_rutin(self):
        for record in self:
            if record.pertemuan_rutin == '1':
                record.nilai_pertemuan_rutin = 1
            elif record.pertemuan_rutin == '2':
                record.nilai_pertemuan_rutin = 2
            elif record.pertemuan_rutin == '3':
                record.nilai_pertemuan_rutin = 3
            elif record.pertemuan_rutin == '4':
                record.nilai_pertemuan_rutin = 4
            elif record.pertemuan_rutin == '5':
                record.nilai_pertemuan_rutin = 5
            else:
                record.nilai_pertemuan_rutin = 0

    @api.depends('pertemuan_segmentasi')
    def _nilai_pertemuan_segmentasi(self):
        for record in self:
            if record.pertemuan_segmentasi == '1':
                record.nilai_pertemuan_segmentasi = 1
            elif record.pertemuan_segmentasi == '2':
                record.nilai_pertemuan_segmentasi = 2
            elif record.pertemuan_segmentasi == '3':
                record.nilai_pertemuan_segmentasi = 3
            elif record.pertemuan_segmentasi == '4':
                record.nilai_pertemuan_segmentasi = 4
            elif record.pertemuan_segmentasi == '5':
                record.nilai_pertemuan_segmentasi = 5
            else:
                record.nilai_pertemuan_segmentasi = 0

    @api.depends('pemiliks')
    def _nilai_pemiliks(self):
        for record in self:
            if record.pra_rat == '1':
                record.nilai_pemiliks = 1
            elif record.pra_rat == '2':
                record.nilai_pemiliks = 2
            elif record.pra_rat == '3':
                record.nilai_pemiliks = 3
            elif record.pra_rat == '4':
                record.nilai_pemiliks = 4
            elif record.pra_rat == '5':
                record.nilai_pemiliks = 5
            else:
                record.nilai_pemiliks = 0

    @api.depends('pengguna_jasas')
    def _nilai_pengguna_jasas(self):
        for record in self:
            if record.pengguna_jasas == '1':
                record.nilai_pengguna_jasas = 1
            elif record.pengguna_jasas == '2':
                record.nilai_pengguna_jasas = 2
            elif record.pengguna_jasas == '3':
                record.nilai_pengguna_jasas = 3
            elif record.pengguna_jasas == '4':
                record.nilai_pengguna_jasas = 4
            elif record.pengguna_jasas == '5':
                record.nilai_pengguna_jasas = 5
            else:
                record.nilai_pengguna_jasas = 0

    @api.depends('pendamping_teknis')
    def _nilai_pendamping_teknis(self):
        for record in self:
            if record.pendamping_teknis == '1':
                record.nilai_pendamping_teknis = 1
            elif record.pendamping_teknis == '2':
                record.nilai_pendamping_teknis = 2
            elif record.pendamping_teknis == '3':
                record.nilai_pendamping_teknis = 3
            elif record.pendamping_teknis == '4':
                record.nilai_pendamping_teknis = 4
            elif record.pendamping_teknis == '5':
                record.nilai_pendamping_teknis = 5
            else:
                record.nilai_pendamping_teknis = 0

    # kinerja hasil
    produksi = fields.Selection([
        ('1', 'SS'),
        ('2', 'Small'),
        ('3', 'Medium'),
        ('4', 'Large'),
    ], string='Produksi')
    jml_pop_lahan = fields.Selection([
        ('1', 'SS'),
        ('2', 'Small'),
        ('3', 'Medium'),
        ('4', 'Large'),
    ], string='Jumlah Populasi / Lahan')
    hrg_rata_liter_lahan = fields.Selection([
        ('1', 'SS'),
        ('2', 'Small'),
        ('3', 'Medium'),
        ('4', 'Large'),
    ], string='Harga Rata-Rata Per Liter / KW')

    nilai_produksi = fields.Float('Nilai Produksi', compute='_nilai_produksi')

    # @api.depends('produksi')
    # def _nilai_produksi(self):
    #     for record in self:
    #         if record.produksi == '1':
    #             self.kecukupan_pakan = '0'
    #         elif 0 <= self.total_persen_tdn <= 50:
    #             self.kecukupan_pakan = '5'
    #         elif record.rat == '3':
    #             record.nilai_rat = 3
    #         elif record.rat == '4':
    #             record.nilai_rat = 4
    #         elif record.rat == '5':
    #             record.nilai_rat = 5
    #         else:
    #             record.nilai_rat = 0

    #Pelanggaran
    surat_teguran = fields.Selection([
        ('1', 'SP1'),
        ('2', 'SP2'),
        ('3', 'SP3'),
    ], string='Surat Teguran')
    nilai_teguran = fields.Float('Nilai', compute='_nilai_teguran')

    @api.depends('surat_teguran')
    def _nilai_teguran(self):
        for record in self:
            if record.surat_teguran == '1':
                record.nilai_teguran = -10
            elif record.surat_teguran == '2':
                record.nilai_teguran = -30
            elif record.surat_teguran == '3':
                record.nilai_teguran = -40
            else:
                record.nilai_teguran = 0
