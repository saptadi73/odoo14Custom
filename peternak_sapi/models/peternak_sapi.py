from odoo import models, fields, api, _
from odoo import exceptions

class peternak_sapi(models.Model):
    _name = "peternak.sapi"
    _description = "Peternak Sapi"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'peternak_name'

    # def print_report_card(self):
    #     return self.env.ref('peternak_sapi.report_peternak_idcard').report_action(self)

    peternak_name = fields.Char(string='Nama Peternak')
    gmbr = fields.Binary('Image')
    phone = fields.Char(string='Phone')
    gender = fields.Selection([
        ('laki', 'Laki-Laki'),
        ('p', 'Perempuan'),
        ('l', 'Lainnya'),
    ], 'Jenis Kelamin', required=True)
    active = fields.Boolean(default=True)
    contact_address = fields.Char('Alamat')
    kelompok_id = fields.Many2one('peternak.group', 'Kelompok')
    kode_peternak = fields.Char('ID Peternak', )
    kode_rfid = fields.Char('Kode RFID')
    jabatan_id = fields.Many2one('jabatan.group', 'Jabatan Kelompok')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('appr_usaha', 'Approve Usaha'),
        ('tlk_usaha', 'Tolak Usaha'),
        ('cln_anggota', 'Calon Anggota'),
        ('anggota', 'Anggota Penuh'),
        ('kan', 'KAN'),
        ('mitra', 'Mitra'),
        ('resign', 'Non Active'),
    ], string='State', readonly=True, default='draft', required=True, tracking=True)
    email = fields.Char('Email')
    wilayah_id = fields.Many2one('master.wilayah', string='Wilayah')
    thp = fields.Char('THP')
    prod_susu = fields.Char('Produksi Susu')
    jum_induk_laktasi = fields.Integer('Jumlah Induk Laktasi')
    jum_induk_kering = fields.Integer('Jumlah Induk Kering')
    jum_sapi_dara = fields.Integer('Jumlah Sapi Dara')
    fat = fields.Char('Fat')
    bj = fields.Char('BJ')
    grade = fields.Char('Grade')
    jenis_pelanggaran_ids = fields.One2many('pelanggaran.peternak', 'peternak_id', 'Jenis Pelanggaran')
    # purchase_count = fields.Integer(compute='compute_purchase_count')
    tgl_masuk = fields.Datetime('Tanggal Setor')
    name = fields.Char(string='Nama')
    sapi_ids = fields.Many2many('sapi', string='Sapi(s)')
    id_sapi = fields.Char(string='Nama Sapi')
    id_sapi = fields.Char( string='ID Sapi')
    kelompok = fields.Many2one(string='Kelompok Peternak')
    contact_address = fields.Char('Alamat')
    setor = fields.Char('Setor Liter')
    bj = fields.Integer('BJ')
    grade = fields.Char('Grade')
    purchase_count = fields.Integer()
    setoran = fields.Integer('Setoran Susu')
    harga_kual = fields.Float('Harga Kualitas')
    insen_prod = fields.Float('Insentif Produksi')
    insen_ef = fields.Float('Insentif Efesiensi')
    harga_total = fields.Float('Total Harga')
    # lab
    suhu = fields.Integer('Suhu')
    fat = fields.Integer('FAT')
    snf = fields.Integer('SNF')
    ts = fields.Float('TS')
    bj = fields.Integer('BJ')
    pro = fields.Integer('Pro')
    lac = fields.Integer('Lac')
    salts = fields.Integer('Salts')
    add_water = fields.Integer('Add Water')
    freez_point = fields.Integer('Freezing Point')
    tpc_kan = fields.Float('TPC KAN')
    mbrt = fields.Char('MBRT/Rezazurin')
    grade = fields.Integer('Grade')
    pres_grade = fields.Float('%Grade')
    tpc_ips = fields.Float('TPC IPS')
    jenis_pelanggaran_liter_ids = fields.One2many('pelanggaran.peternak', 'peternak_id', 'Jenis Pelanggaran')
    # tingkat_pend = fields.Selection([
    #     ('sd', 'SD'),
    #     ('smp', 'SMP'),
    #     ('sma', 'SMA/SMK'),
    #     ('d3', 'D3'),
    #     ('s1', 'S1'),
    #     ('s2', 'S2'),
    #     ('s3', 'S3')
    # ], string='Tingkat Pendidikan', default=False, required=True)
    ko_id = fields.Many2one('peternak.sapi', 'KO')
    ka_id = fields.Many2one('peternak.sapi', 'KA')
    tps_id = fields.Many2one('tps.liter', 'TPS')
    kode_tps = fields.Char('Kode Pos Penampungan')
    status_perkawinan = fields.Selection([
        ('1', 'Kawin'),
        ('2', 'Belum Kawin'),
        ('3', 'Cerai Hidup'),
        ('4', 'Cerai Mati'),
    ], string='Status Perkawinan')
    usaha_id = fields.Many2one('usaha.peternak', 'Unit Usaha')

    list_sapi_ids = fields.One2many('sapi', 'peternak_id', 'Sapi')
    kandang_ids = fields.One2many('kandang.sapi.perah', 'peternak_id', 'Kandang')
    list_laktasi_sapi_ids = fields.One2many('sapi', compute='_compute_list_laktasi_sapi_ids', string='Sapi Laktasi', store=False)
    tipe_mitra = fields.Selection([
        ('1', 'Mitra 1'),
        ('2', 'Mitra 2'),
    ], string='Tipe Mitra')
    pernah_setor = fields.Boolean('Pernah Setor?', default=False)
    is_ca = fields.Boolean('CA?', default=False)
    is_ap = fields.Boolean('AP?', default=False)
    is_mitra = fields.Boolean('Mitra?', default=False)

    ts_master = fields.Float('TS Master')
    ts_dasar = fields.Float('TS Dasar')
    fat_master = fields.Float('FAT Master')
    fat_dasar = fields.Float('FAT Dasar')
    pro_master = fields.Float('Pro Master')
    pro_dasar = fields.Float('Pro Dasar')

    # tpc_100 = fields.Float('TPC <100.000')
    # tpc_101 = fields.Float('TPC 101.000-200.000')
    # tpc_201 = fields.Float('TPC 201.000-300.000')
    # tpc_301 = fields.Float('TPC 301.000-400.000')
    # tpc_401 = fields.Float('TPC 401.000-500.000')
    # tpc_501 = fields.Float('TPC 501.001-1.000.000')
    # tpc_1000 = fields.Float('TPC 1.000.001-2.000.000')
    # tpc_2000 = fields.Float('TPC 2.000.001-3.000.000')
    # tpc_3000 = fields.Float('TPC >3.000.000')
    # tpc_5000 = fields.Float('TPC >5.000.000')
    # tpc_10000 = fields.Float('TPC 10.000.000')
    transport = fields.Float('Transport')
    daya_saing = fields.Float('Daya Saing')
    pakan = fields.Float('Pakan')
    develop = fields.Float('Development')
    pmk = fields.Float('PMK')
    tot_insen = fields.Float('Total Insentif', compute='_compute_tot_insen')
    # ins_prod1 = fields.Float('<8000')
    # ins_prod2 = fields.Float('>8000-10000')
    # ins_prod3 = fields.Float('>=10000-15000')
    # ins_prod4 = fields.Float('>=15000-20000')
    # ins_prod5 = fields.Float('>=20000-25000')
    # ins_prod6 = fields.Float('>=25000')

    @api.depends('transport', 'daya_saing', 'pakan', 'develop', 'pmk')
    def _compute_tot_insen(self):
        for record in self:
            tot_insen = record.transport + record.daya_saing + record.pakan + record.develop + record.pmk
            record.tot_insen = tot_insen

    @api.depends('list_sapi_ids')
    def _compute_list_laktasi_sapi_ids(self):
        for record in self:
            record.list_laktasi_sapi_ids = record.list_sapi_ids.filtered(lambda sapi: sapi.state == 'laktasi')

    # member_anggota_id = fields.Many2one('simpin_syariah.member', string='Anggota')
    # member_id = fields.Many2one('simpin_syariah.member', string='Member', store=True, readonly=True,
    #                             compute='_compute_member_id')
    #
    # @api.onchange('member_anggota_id')
    # def _onchange_member_anggota_id(self):
    #     if self.member_anggota_id:
    #         self.partner_id = self.member_anggota_id.partner_id
    #
    # @api.depends('member_anggota_id')
    # def _compute_member_id(self):
    #     for record in self:
    #         record.member_id = record.member_anggota_id

    # member_ids = fields.One2many('simpin_syariah.member', 'peternak_id', string='Members')

    def func_appr_usaha(self):
        if self.state == 'draft':
            self.state = 'appr_usaha'

    def func_tlk_usaha(self):
        if self.state == 'draft':
            self.state = 'tlk_usaha'

    def func_cln_anggota(self):
        if self.state == 'appr_usaha':
            self.state = 'cln_anggota'

    def func_mitra(self):
        if self.state == 'appr_usaha':
            self.state = 'mitra'

    def func_anggota(self):
        if self.state == 'cln_anggota':
            self.state = 'anggota'

    def func_kan(self):
        if self.state == 'cln_anggota':
            self.state = 'kan'

    def func_resign(self):
        if self.state == 'anggota':
            self.state = 'resign'

    def func_setdraft(self):
        if self.state == 'anggota':
            self.state = 'draft'

    _sql_constraints = [(
        'unique_peternak_sapi',
        'unique(name)',
        'Can not create peternak multiple times.!'
    )]

    def create_anggota(self):
        res_ids = []
        for browse_record in self:
            result = {}
            anggota_obj = self.env['simpin_syariah.member']
            # Find the corresponding peternak record based on the peternak_name string
            peternak = self.env['peternak.sapi'].search([('peternak_name', '=', browse_record.peternak_name)])
            if not peternak:
                # Handle the case where the peternak record is not found
                continue
            res = anggota_obj.create({
                'name': self.env['ir.sequence'].next_by_code('simpin_syariah.member'),
                'name': browse_record.peternak_name.id,
                'email': browse_record.email or False,
                'gmbr': browse_record.gmbr or False,
                'gender': browse_record.gender or False,
                'wilayah_id': browse_record.wilayah_id.id,
                'jabatan_id': browse_record.jabatan_id.id,
                'no_hp': browse_record.phone or False,
                'address': browse_record.contact_address or False,
                'ko_id': browse_record.ko_id.id,
                'ka_id': browse_record.ka_id.id,
                'usaha_id': browse_record.usaha_id.id,
                'kode_peternak': browse_record.kode_peternak,
                'tps_id': browse_record.tps_id.id,
                'kode_tps': browse_record.kode_tps,
                'status_perkawinan': browse_record.status_perkawinan,
                'jumlah_sapi_kering': browse_record.jumlah_sapi_kering,
                'jumlah_sapi_laktasi': browse_record.jumlah_sapi_laktasi,
                'jumlah_sapi_dara': browse_record.jumlah_sapi_dara,
                'count_sapi': browse_record.count_sapi,
                'peternak_id': peternak.id,

            })
            res_ids.append(res.id)
            if res_ids:
                ir_model_data = self.env['ir.model.data']
                action = ir_model_data.xmlid_to_object('asa_simpin_syariah.simpin_syariah_member_menu_action')
                list_view_id = ir_model_data.xmlid_to_res_id('asa_simpin_syariah.simpin_syariah_member_tree')
                form_view_id = ir_model_data.xmlid_to_res_id('asa_simpin_syariah.simpin_syariah_member_form')
                result = {
                    'name': action.name,
                    'help': action.help,
                    'type': action.type,
                    'views': [[list_view_id, 'tree'], [form_view_id, 'form']],
                    'target': action.target,
                    'context': action.context,
                    'res_model': action.res_model,
                    'res_id': res.id,
                }

            if res_ids:
                result['domain'] = "[('id','=',%s)]" % res_ids

            return result
    partner_id = fields.Many2one('res.partner', string='Partner')    
		
    count_sapi = fields.Integer(string='Jumlah Sapi', compute='_compute_count_sapi_field', store=True)

    @api.depends('list_sapi_ids.active')
    def _compute_count_sapi_field(self):
        for record in self:
            active_sapi_count = len(record.list_sapi_ids.filtered(lambda sapi: sapi.active))
            record.count_sapi = active_sapi_count

    @api.depends('list_sapi_ids.state', 'list_sapi_ids.tipe_id')
    def _compute_jumlah_sapi_per_status(self):
        for record in self:
            count_kering = 0
            count_laktasi = 0
            count_dara = 0
            for sapi in record.list_sapi_ids:
                state = sapi.state
                tipe_id = sapi.tipe_id
                if state == 'kering' and tipe_id and tipe_id.nama_tipe_sapi == 'INDUK':
                    count_kering += 1
                elif state == 'laktasi' and tipe_id and tipe_id.nama_tipe_sapi == 'INDUK':
                    count_laktasi += 1
                elif tipe_id and tipe_id.nama_tipe_sapi == 'DARA':
                    count_dara += 1
            record.jumlah_sapi_kering = count_kering
            record.jumlah_sapi_laktasi = count_laktasi
            record.jumlah_sapi_dara = count_dara

    jumlah_sapi_kering = fields.Integer(compute='_compute_jumlah_sapi_per_status', string='Jumlah Sapi Kering',
                                        store=True)
    jumlah_sapi_laktasi = fields.Integer(compute='_compute_jumlah_sapi_per_status', string='Jumlah Sapi Laktasi',
                                         store=True)
    jumlah_sapi_dara = fields.Integer(compute='_compute_jumlah_sapi_per_status', string='Jumlah Sapi Dara', store=True)


    # course_count = fields.Integer(compute='compute_course_count')

    # def get_peternak_course(self):
    #     action = self.env.ref('website_slides.'
    #                           'slide_channel_action_overview').read()[0]
    #     action['domain'] = [('user_id', 'in', self.ids)]
    #     return action
    #
    # def compute_course_count(self):
    #     for record in self:
    #         record.course_count = self.env['slide.channel.partner'].search_count(
    #             [('user_id', 'in', self.ids)])

    # @api.onchange('name')
    # def _onchange_name(self):
    #     self.user_id = self.name.user_id and self.name.user_id.id or False

    # @api.models
    # def create(self, vals):
    #     res = super(peternak_sapi, self).create(vals)
    #     if vals.get('sapi_ids', False) and res.name.user_id:
    #         sapi_ids = self.sapi_ids.browse(res.sapi_ids.ids)
    #         user_ids = [sapi_id.user_id.id for sapi_id in sapi_ids
    #                     if sapi_id.user_id]
    #         res.user_id.child_ids = [(6, 0, user_ids)]
    #     return res

    # def write(self, vals):
    #     for rec in self:
    #         res = super(peternak_sapi, self).write(vals)
    #         if vals.get('sapi_ids', False) and rec.name.user_id:
    #             sapi_ids = rec.sapi_ids.browse(rec.sapi_ids.ids)
    #             usr_ids = [sapi_id.user_id.id for sapi_id in sapi_ids
    #                        if sapi_id.user_id]
    #             rec.user_id.child_ids = [(6, 0, usr_ids)]
    #         rec.clear_caches()
    #         return res

    # def unlink(self):
    #     for record in self:
    #         if record.peternak_name.user_id:
    #             record.user_id.child_ids = [(6, 0, [])]
    #         return super(peternak_sapi, self).unlink()

    # def create_peternak_user(self):
    #     template = self.env.ref('peternak_sapi.peternak_template_user')
    #     users_res = self.env['res.users']
    #     for record in self:
    #         if not record.name.email:
    #             raise exceptions.Warning(_('Update peternak email id first.'))
    #         if not record.name.user_id:
    #             groups_id = template and template.groups_id or False
    #             user_ids = [
    #                 x.user_id.id for x in record.sapi_ids if x.user_id]
    #             user_id = users_res.create({
    #                 'name': record.name.name,
    #                 'partner_id': record.name.id,
    #                 'login': record.name.email,
    #                 'is_peternak': True,
    #                 'tz': self._context.get('tz'),
    #                 'groups_id': groups_id,
    #                 'child_ids': [(6, 0, user_ids)]
    #             })
    #             record.user_id = user_id
    #             record.name.user_id = user_id


    def create_peternak_user(self):
        user_group = self.env.ref("base.group_portal") or False
        users_res = self.env['res.users']
        for record in self:
            if not record.user_id:
                user_id = users_res.create({
                    'name': record.peternak_name,
                    'login': record.email,
                    'groups_id': user_group,
                    'is_peternak': True,
                    'tz': self._context.get('tz'),
                })
                record.user_id = user_id

    pelanggaran_count = fields.Integer(compute='compute_pelanggaran_count')

    def get_pelanggaran(self):
        action = self.env.ref('peternak_sapi.'
                              'act_pelanggaran_view').read()[0]
        action['domain'] = [('peternak_id', 'in', self.ids)]
        return action

    def compute_pelanggaran_count(self):
        for record in self:
            record.pelanggaran_count = self.env['pelanggaran.peternak'].search_count(
                [('peternak_id', 'in', self.ids)])

    kandang_line = fields.Many2many('kandang.line', 'kandang_id', string='Kandang Lines')

class KandangLine(models.Model):
    _name = 'kandang.line'
    _description = 'Kandang Line'

    peternak_id = fields.Many2one('peternak.sapi', 'Peternak')
    kandang_id = fields.Many2one('kandang.sapi.perah', 'Kandang')
    almt = fields.Char('Alamat')
    provinsi_id = fields.Many2one('wilayah.provinsi', 'Provinsi')
    kabkota_id = fields.Many2one('wilayah.kabkota', 'Kab/Kota')
    kecamatan_id = fields.Many2one('wilayah.kecamatan', 'Kecamatan')
    kelurahan_id = fields.Many2one('wilayah.kelurahan', 'Kelurahan')
    state = fields.Selection([
        ('sendiri', 'Milik Sendiri'),
        ('terpisah', 'Terpisah'),
        ('Perusahaan', 'Perusahaan'),
    ], string='Status Kepemilikan')
    status_kepemilikan = fields.Selection([
        ('sendiri', 'Milik Sendiri'),
        ('terpisah', 'Terpisah'),
        ('Perusahaan', 'Perusahaan'),
    ], string='Status Kepemilikan')

  
class sapi(models.Model):
    _inherit = "sapi"

    peternak_ids = fields.Many2many('peternak_sapi', string='Peternak')

    @api.model
    def create(self, vals):
        res = super(sapi, self).create(vals)
        if vals.get('peternak_ids', False):
            for peternak_id in res.peternak_ids:
                if peternak_id.user_id:
                    user_ids = [x.user_id.id for x in peternak_id.peternak_ids
                                if x.user_id]
                    peternak_id.user_id.child_ids = [(6, 0, user_ids)]
        return res

    def write(self, vals):
        res = super(sapi, self).write(vals)
        if vals.get('peternak_ids', False):
            user_ids = []
            if self.peternak_ids:
                for peternak in self.peternak_ids:
                    if peternak.user_id:
                        user_ids = [x.user_id.id for x in peternak.sapi_ids
                                    if x.user_id]
                        peternak.user_id.child_ids = [(6, 0, user_ids)]
            else:
                user_ids = self.env['res.users'].search([
                    ('child_ids', 'in', self.user_id.id)])
                for user_id in user_ids:
                    child_ids = user_id.child_ids.ids
                    child_ids.remove(self.user_id.id)
                    user_id.child_ids = [(6, 0, child_ids)]
        if vals.get('user_id', False):
            for peternak_id in self.peternak_id:
                child_ids = peternak_id.user_id.child_ids.ids
                child_ids.append(vals['user_id'])
                peternak_id.name.user_id.child_ids = [(6, 0, child_ids)]
        self.clear_caches()
        return res

    def unlink(self):
        for record in self:
            if record.peternak_ids:
                for peternak_id in record.peternak_ids:
                    child_ids = peternak_id.user_id.child_ids.ids
                    child_ids.remove(record.user_id.id)
                    peternak_id.user_id.child_ids = [(6, 0, child_ids)]
        return super(sapi, self).unlink()

    peternak_count = fields.Integer(compute='compute_peternak_count')

    def get_peternak(self):
        action = self.env.ref('peternak_sapi.'
                              'act_peternak_sapi_view').read()[0]
        action['domain'] = [('sapi_ids', 'in', self.ids)]
        return action

    def compute_peternak_count(self):
        for record in self:
            record.peternak_count = self.env['peternak.sapi'].search_count(
                [('sapi_ids', 'in', self.ids)])

class PeternakSapiInherit(models.Model):
    _inherit = "sapi"

    peternak_id = fields.Many2one('peternak.sapi', 'Peternak', ondelete='cascade')

class PeternakSapiKandang(models.Model):
    _inherit = "kandang.sapi.perah"

    peternak_id = fields.Many2one('peternak.sapi', string='Pemilik')