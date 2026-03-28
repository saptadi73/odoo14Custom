# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from datetime import date,datetime
from dateutil.relativedelta import relativedelta 

class medical_patient(models.Model):
    _name = 'medical.patient'
    _rec_name = 'patient_id'

    # @api.onchange('patient_id')
    # def _onchange_patient(self):
    #     '''
    #     The purpose of the method is to define a domain for the available
    #     purchase orders.
    #     '''
    #     address_id = self.patient_id
    #     self.partner_address_id = address_id

    def print_report(self):
        return self.env.ref('basic_hms.report_print_patient_card').report_action(self)

    # @api.depends('date_of_birth')
    # def onchange_age(self):
    #     for rec in self:
    #         if rec.date_of_birth:
    #             d1 = rec.date_of_birth
    #             d2 = datetime.today().date()
    #             rd = relativedelta(d2, d1)
    #             rec.age = str(rd.years) + "y" +" "+ str(rd.months) + "m" +" "+ str(rd.days) + "d"
    #         else:
    #             rec.age = "No Date Of Birth!!"

    patient_id = fields.Many2one('res.partner', string="Patient", required=False, domain="[('is_sapi', '=', True)]")
    id_sapi = fields.Many2one('sapi', string='Sapi')
    name = fields.Char(string='ID', readonly=True)
    last_name = fields.Char('Last Name')
    date_of_birth = fields.Date(related="id_sapi.date_of_birth", string="Date of Birth")
    sex = fields.Selection([('m', 'Male'),('f', 'Female')], string ="Sex")
    age = fields.Char(related="id_sapi.age", string="Patient Age",store=True)
    critical_info = fields.Text(string="Patient Critical Information")
    image_1920 = fields.Binary(string="Picture")
    blood_type = fields.Selection([('A', 'A'),('B', 'B'),('AB', 'AB'),('O', 'O')], string ="Blood Type")
    rh = fields.Selection([('-+', '+'),('--', '-')], string ="Rh")
    marital_status = fields.Selection([('s','Single'),('m','Married'),('w','Widowed'),('d','Divorced'),('x','Seperated')],string='Marital Status')
    deceased = fields.Boolean(string='Deceased')
    date_of_death = fields.Datetime(string="Date of Death")
    cause_of_death = fields.Char(string='Cause of Death')
    receivable = fields.Float(string="Receivable", readonly=True)
    current_insurance_id = fields.Many2one('medical.insurance',string="Insurance")
    partner_address_id = fields.Text(string="Address")
    phone = fields.Char(string="Phone")
    primary_care_physician_id = fields.Many2one('res.users', string="Primary Care Doctor")
    patient_status = fields.Char(string="Hospitalization Status",readonly=True)
    patient_disease_ids = fields.One2many('medical.patient.disease','patient_id')
    patient_psc_ids = fields.One2many('medical.patient.psc','patient_id')
    excercise = fields.Boolean(string='Excercise')
    excercise_minutes_day = fields.Integer(string="Minutes/Day")
    sleep_hours = fields.Integer(string="Hours of sleep")
    sleep_during_daytime = fields.Boolean(string="Sleep at daytime")
    number_of_meals = fields.Integer(string="Meals per day")
    coffee = fields.Boolean('Coffee')
    coffee_cups = fields.Integer(string='Cups Per Day')
    eats_alone = fields.Boolean(string="Eats alone")
    soft_drinks = fields.Boolean(string="Soft drinks(sugar)")
    salt = fields.Boolean(string="Salt")
    diet = fields.Boolean(string=" Currently on a diet ")
    diet_info = fields.Integer(string=' Diet info ')
    general_info = fields.Text(string="Info")
    lifestyle_info = fields.Text('Lifestyle Information')
    smoking = fields.Boolean(string="Smokes")
    smoking_number = fields.Integer(string="Cigarretes a day")
    ex_smoker = fields.Boolean(string="Ex-smoker")
    second_hand_smoker = fields.Boolean(string="Passive smoker")
    age_start_smoking = fields.Integer(string="Age started to smoke")
    age_quit_smoking = fields.Integer(string="Age of quitting")
    drug_usage = fields.Boolean(string='Drug Habits')
    drug_iv = fields.Boolean(string='IV drug user')
    ex_drug_addict = fields.Boolean(string='Ex drug addict')
    age_start_drugs = fields.Integer(string='Age started drugs')
    age_quit_drugs = fields.Integer(string="Age quit drugs")
    alcohol = fields.Boolean(string="Drinks Alcohol")
    ex_alcohol = fields.Boolean(string="Ex alcoholic")
    age_start_drinking = fields.Integer(string="Age started to drink")
    age_quit_drinking = fields.Integer(string="Age quit drinking")
    alcohol_beer_number = fields.Integer(string="Beer / day")
    alcohol_wine_number = fields.Integer(string="Wine / day")
    alcohol_liquor_number = fields.Integer(string="Liquor / day")
    cage_ids = fields.One2many('medical.patient.cage','patient_id')
    sex_oral = fields.Selection([('0','None'),
                                 ('1','Active'),
                                 ('2','Passive'),
                                 ('3','Both')],string='Oral Sex')
    sex_anal = fields.Selection([('0','None'),
                                 ('1','Active'),
                                 ('2','Passive'),
                                 ('3','Both')],string='Anal Sex')
    prostitute = fields.Boolean(string='Prostitute')
    sex_with_prostitutes = fields.Boolean(string=' Sex with prostitutes ')
    sexual_preferences = fields.Selection([
            ('h', 'Heterosexual'),
            ('g', 'Homosexual'),
            ('b', 'Bisexual'),
            ('t', 'Transexual'),
        ], 'Sexual Orientation', sort=False)
    sexual_practices = fields.Selection([
            ('s', 'Safe / Protected sex'),
            ('r', 'Risky / Unprotected sex'),
        ], 'Sexual Practices', sort=False)
    sexual_partners = fields.Selection([
            ('m', 'Monogamous'),
            ('t', 'Polygamous'),
        ], 'Sexual Partners', sort=False)
    sexual_partners_number = fields.Integer('Number of sexual partners')
    first_sexual_encounter = fields.Integer('Age first sexual encounter')
    anticonceptive = fields.Selection([
            ('0', 'None'),
            ('1', 'Pill / Minipill'),
            ('2', 'Male condom'),
            ('3', 'Vasectomy'),
            ('4', 'Female sterilisation'),
            ('5', 'Intra-uterine device'),
            ('6', 'Withdrawal method'),
            ('7', 'Fertility cycle awareness'),
            ('8', 'Contraceptive injection'),
            ('9', 'Skin Patch'),
            ('10', 'Female condom'),
        ], 'Anticonceptive Method', sort=False)
    sexuality_info = fields.Text('Extra Information')
    motorcycle_rider = fields.Boolean('Motorcycle Rider', help="The patient rides motorcycles")
    helmet = fields.Boolean('Uses helmet', help="The patient uses the proper motorcycle helmet")
    traffic_laws = fields.Boolean('Obeys Traffic Laws', help="Check if the patient is a safe driver")
    car_revision = fields.Boolean('Car Revision', help="Maintain the vehicle. Do periodical checks - tires,breaks ...")
    car_seat_belt = fields.Boolean('Seat belt', help="Safety measures when driving : safety belt")
    car_child_safety = fields.Boolean('Car Child Safety', help="Safety measures when driving : child seats, proper seat belting, not seating on the front seat, ....")
    home_safety = fields.Boolean('Home safety', help="Keep safety measures for kids in the kitchen, correct storage of chemicals, ...")
    fertile = fields.Boolean('Fertile')
    menarche = fields.Integer('Menarche age')
    menopausal = fields.Boolean('Menopausal')
    menopause = fields.Integer('Menopause age')
    menstrual_history_ids = fields.One2many('medical.patient.menstrual.history','patient_id')
    breast_self_examination = fields.Boolean('Breast self-examination')
    mammography = fields.Boolean('Mammography')
    pap_test = fields.Boolean('PAP test')
    last_pap_test = fields.Date('Last PAP test')
    colposcopy = fields.Boolean('Colposcopy')
    mammography_history_ids = fields.One2many('medical.patient.mammography.history','patient_id')
    pap_history_ids = fields.One2many('medical.patient.pap.history','patient_id')
    colposcopy_history_ids = fields.One2many('medical.patient.colposcopy.history','patient_id')
    pregnancies = fields.Integer('Pregnancies')
    premature = fields.Integer('Premature')
    stillbirths = fields.Integer('Stillbirths')
    abortions = fields.Integer('Abortions')
    pregnancy_history_ids = fields.One2many('medical.patient.pregnency','patient_id')
    family_history_ids = fields.Many2many('medical.family.disease',string="Family Disease Lines")
    perinatal_ids = fields.Many2many('medical.preinatal')
    ex_alcoholic = fields.Boolean('Ex alcoholic')
    currently_pregnant = fields.Boolean('Currently Pregnant')
    born_alive = fields.Integer('Born Alive')
    gpa = fields.Char('GPA')
    works_at_home = fields.Boolean('Works At Home')
    colposcopy_last = fields.Date('Last colposcopy')
    mammography_last = fields.Date('Last mammography')
    ses = fields.Selection([
            ('None', ''),
            ('0', 'Lower'),
            ('1', 'Lower-middle'),
            ('2', 'Middle'),
            ('3', 'Middle-upper'),
            ('4', 'Higher'),
        ], 'Socioeconomics', help="SES - Socioeconomic Status", sort=False)
    education = fields.Selection([('o','None'),('1','Incomplete Primary School'),
                                  ('2','Primary School'),
                                  ('3','Incomplete Secondary School'),
                                  ('4','Secondary School'),
                                  ('5','University')],string='Education Level')
    housing = fields.Selection([
            ('None', ''),
            ('0', 'Shanty, deficient sanitary conditions'),
            ('1', 'Small, crowded but with good sanitary conditions'),
            ('2', 'Comfortable and good sanitary conditions'),
            ('3', 'Roomy and excellent sanitary conditions'),
            ('4', 'Luxury and excellent sanitary conditions'),
        ], 'Housing conditions', help="Housing and sanitary living conditions", sort=False)
    works = fields.Boolean('Works')
    hours_outside = fields.Integer('Hours outside home', help="Number of hours a day the patient spend outside the house")
    hostile_area = fields.Boolean('Hostile Area')
    notes = fields.Text(string="Extra info")
    sewers = fields.Boolean('Sanitary Sewers')
    water = fields.Boolean('Running Water')
    trash = fields.Boolean('Trash recollection')
    electricity = fields.Boolean('Electrical supply')
    gas = fields.Boolean('Gas supply')
    telephone = fields.Boolean('Telephone')
    television = fields.Boolean('Television')
    internet = fields.Boolean('Internet')
    single_parent= fields.Boolean('Single parent family')
    domestic_violence = fields.Boolean('Domestic violence')
    working_children = fields.Boolean('Working children')
    teenage_pregnancy = fields.Boolean('Teenage pregnancy')
    sexual_abuse = fields.Boolean('Sexual abuse')
    drug_addiction = fields.Boolean('Drug addiction')
    school_withdrawal = fields.Boolean('School withdrawal')
    prison_past = fields.Boolean('Has been in prison')
    prison_current = fields.Boolean('Is currently in prison')
    relative_in_prison = fields.Boolean('Relative in prison', help="Check if someone from the nuclear family - parents sibblings  is or has been in prison")
    fam_apgar_help = fields.Selection([
            ('None', ''),
            ('0', 'None'),
            ('1', 'Moderately'),
            ('2', 'Very much'),
        ], 'Help from family',
            help="Is the patient satisfied with the level of help coming from the family when there is a problem ?", sort=False)
    fam_apgar_discussion = fields.Selection([
            ('None', ''),
            ('0', 'None'),
            ('1', 'Moderately'),
            ('2', 'Very much'),
        ], 'Problems discussion',
            help="Is the patient satisfied with the level talking over the problems as family ?", sort=False)
    fam_apgar_decisions = fields.Selection([
            ('None', ''),
            ('0', 'None'),
            ('1', 'Moderately'),
            ('2', 'Very much'),
        ], 'Decision making',
            help="Is the patient satisfied with the level of making important decisions as a group ?", sort=False)
    fam_apgar_timesharing = fields.Selection([
            ('None', ''),
            ('0', 'None'),
            ('1', 'Moderately'),
            ('2', 'Very much'),
        ], 'Time sharing',
            help="Is the patient satisfied with the level of time that they spend together ?", sort=False)
    fam_apgar_affection = fields.Selection([
            ('None', ''),
            ('0', 'None'),
            ('1', 'Moderately'),
            ('2', 'Very much'),
        ], 'Family affection',
            help="Is the patient satisfied with the level of affection coming from the family ?", sort=False)
    fam_apgar_score = fields.Integer('Score', help="Total Family APGAR 7 - 10 : Functional Family 4 - 6  : Some level of disfunction \n"
                                          "0 - 3  : Severe disfunctional family \n")
    lab_test_ids = fields.One2many('medical.patient.lab.test','patient_id')
    fertile = fields.Boolean('Fertile')
    menarche_age  = fields.Integer('Menarche age')
    menopausal = fields.Boolean('Menopausal')
    pap_test_last = fields.Date('Last PAP Test')
    colposcopy = fields.Boolean('Colpscopy')
    gravida = fields.Integer('Pregnancies')
    medical_vaccination_ids = fields.One2many('medical.vaccination','medical_patient_vaccines_id')
    medical_appointments_ids = fields.One2many('medical.appointment','patient_id',string='Appointments')
    lastname = fields.Char('Last Name')
    report_date = fields.Date('Date',default = datetime.today().date())
    medication_ids = fields.One2many('medical.patient.medication1','medical_patient_medication_id')
    medication_line_ids = fields.One2many('medical.prescription.line','medical_patient')
    deaths_2nd_week = fields.Integer('Deceased after 2nd week')
    deaths_1st_week = fields.Integer('Deceased after 1st week')
    full_term = fields.Integer('Full Term')
    ses_notes = fields.Text('Notes')
    weight = fields.Float(related="id_sapi.bobot", string='Bobot')
    height = fields.Integer(related="id_sapi.height", string='Tinggi')
    panjang = fields.Integer(related="id_sapi.panjang", string='Panjang')
    lgkr_perut = fields.Integer (related="id_sapi.lgkr_perut", string='Lingkar Perut')
    category = fields.Selection([('c1','Class 1'),('c2','Class 2'),('c3','Class 3')], string="Category")
    peternak_id = fields.Many2one('peternak.sapi', 'Peternak')
    code_sapi = fields.Char( string='ID Sapi')
    jenis_sapi = fields.Many2one('jenis.sapi.master', related='id_sapi.jenis_sapi', string='Jenis Sapi')
    #kehamilan
    status_rep = fields.Selection([
        ('1', 'Tidak Ada'),
        ('2', 'Pernah di IB/KAWIN'),
        ('3', 'Kosong'),
        ('4', 'Bunting'),
        ('5', 'Melahirkan'),
        ('6', 'Donor'),
        ], 'Status Reproduksi')
    tanda_kebun = fields.Selection([
        ('1', 'Fluktuas'),
        ('2', 'Slip Membran'),
        ('3', 'Kotiledon'),
        ('4', 'Undulasi'),
        ('5', 'Kornua Kiri'),
        ('6', 'Kornua Kanan'),
        ('7', 'Bifurcatio'),
        ('8', 'Amniotic Vesicle'),
        ], 'Tanda Kebuntingan')
    umur_khmln = fields.Integer('Umur Kehamilan')
    bcs = fields.Float('Body Condition Score', required=True)

    #kelahiran
    jmlh_lahir = fields.Integer('jumlah Lahir')
    jmlh_mati = fields.Integer('Jumlah Mati')
    jns_kelam = fields.Selection([
        ('m', 'Male'),
        ('f', 'Female'),
    ], 'Jenis Kelamin')
    id_status_reproduksi = fields.Many2one('master.status.reproduksi', 'Status Reproduksi')
    metode_perolehan_id = fields.Many2one('master.metoda', 'Metode Perolehan')
    stts_laktasi_id = fields.Many2one('master.status.laktasi', 'Status Laktasi')
    tipe_id = fields.Many2one('master.tipe.sapi', string='Tipe')
    laktasi_ke = fields.Integer('Laktasi Ke')
    id_induk = fields.Many2one('sapi', 'Induk')
    id_ayah = fields.Many2one('sapi', 'Ayah')

    jml_puting = fields.Integer('Jumlah Puting')
    kon_kaki = fields.Selection([
        ('sim', 'Simetris'),
        ('tdk', 'Tidak Simetris'),
    ], string='Kondisi Kaki')
    punggung = fields.Selection([
        ('lor', 'Lordosis'),
        ('kif', 'Kifosis'),
        ('lur', 'Lurus'),
    ], string='Punggung')

    @api.onchange('tipe')
    def onchange_tipe(self):
        if self.tipe and self.id_sapi:
            # Ubah nilai tipe di objek sapi_id jika field sapi_tipe diisi
            self.id_sapi.write({'tipe': self.tipe})

    @api.onchange('id_sapi.tipe')
    def onchange_tipe_sapi(self):
        if self.id_sapi.tipe == '1':
            # Lakukan sesuatu jika tipe sapi = Induk
            pass
        elif self.id_sapi.tipe == '2':
            # Lakukan sesuatu jika tipe sapi = Dara
            pass
        elif self.id_sapi.tipe == '3':
            # Lakukan sesuatu jika tipe sapi = Pedet Btn
            pass

    @api.onchange('id_sapi')
    def onchange_sapi_id_sex(self):
        if self.id_sapi:
            if self.id_sapi.sex:
                self.sex = self.id_sapi.sex
        else:
            self.sex = ''

    @api.onchange('id_sapi')
    def onchange_peternak_id(self):
        if self.id_sapi:
            if self.id_sapi.peternak_id:
                self.peternak_id = self.id_sapi.peternak_id
        else:
            self.peternak_id = ''

    @api.onchange('patient_id')
    def _onchange_patient_id_image(self):
        if self.patient_id:
            self.image_1920 = self.patient_id.image_1920

    @api.model
    def create(self,val):
        appointment = self._context.get('appointment_id')
        res_partner_obj = self.env['res.partner']
        if appointment:
            val_1 = {'name': self.env['res.partner'].browse(val['patient_id']).name}
            patient= res_partner_obj.create(val_1)
            val.update({'patient_id': patient.id})
        if val.get('date_of_birth'):
            dt = val.get('date_of_birth')
            d1 = datetime.strptime(str(dt), "%Y-%m-%d").date()
            d2 = datetime.today().date()
            rd = relativedelta(d2, d1)
            age = str(rd.years) + "y" +" "+ str(rd.months) + "m" +" "+ str(rd.days) + "d"
            val.update({'age':age} )

        patient_id  = self.env['ir.sequence'].next_by_code('medical.patient')
        if patient_id:
            val.update({
                        'name':patient_id,
                       })
        result = super(medical_patient, self).create(val)
        return result

    appointment_count = fields.Integer(compute='compute_appointment_count')

    def get_appointment(self):
        action = self.env.ref('basic_hms.'
                              'action_medical_appointment').read()[0]
        action['domain'] = [('patient_id', 'in', self.ids)]
        return action

    def compute_appointment_count(self):
        for record in self:
            record.appointment_count = self.env['medical.appointment'].search_count(
                [('patient_id', 'in', self.ids)])

    inpatient_count = fields.Integer(compute='compute_inpatient_count')

    def get_inpatient(self):
        action = self.env.ref('basic_hms.'
                              'action_medical_inpatient_registration').read()[0]
        action['domain'] = [('patient_id', 'in', self.ids)]
        return action

    def compute_inpatient_count(self):
        for record in self:
            record.inpatient_count = self.env['medical.inpatient.registration'].search_count(
                [('patient_id', 'in', self.ids)])

    # lab_count = fields.Integer(compute='compute_lab_count')
    #
    # def get_lab(self):
    #     action = self.env.ref('basic_hms.'
    #                           'action_medical_lab_form').read()[0]
    #     action['domain'] = [('patient_id', 'in', self.ids)]
    #     return action
    #
    # def compute_lab_count(self):
    #     for record in self:
    #         record.lab_count = self.env['medical.lab'].search_count(
    #             [('patient_id', 'in', self.ids)])

    medicament_count = fields.Integer(compute='compute_medicament_count')

    def get_medicament(self):
        action = self.env.ref('basic_hms.'
                              'action_medical_prescription_order').read()[0]
        action['domain'] = [('patient_id', 'in', self.ids)]
        return action

    def compute_medicament_count(self):
        for record in self:
            record.medicament_count = self.env['medical.prescription.order'].search_count(
                [('patient_id', 'in', self.ids)])
# vim=expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

class form_abortus(models.Model):
    _name = 'form.abortus'
    _inherit = 'image.mixin'
    _rec_name = 'id_sapi'

    peternak_id = fields.Many2one('peternak.sapi', 'Anggota/Peternak')
    id_pemilik = fields.Char('ID Pemilik', related='peternak_id.kode_peternak')
    wilayah_id = fields.Many2one('master.wilayah', 'Wilayah')
    kelompok_id = fields.Many2one('peternak.group', related='peternak_id.kelompok_id')
    petugas_id = fields.Many2one('medical.physician', 'Petugas')
    jabatan_id = fields.Many2one('master.jabatan', ' Jabatan', readonly=False)
    id_sapi = fields.Many2one('sapi', 'Nama Sapi', domain="[('peternak_id', '=', peternak_id)]")
    eartag_id = fields.Char('ID Eartag Sapi')
    tgl_layanan = fields.Date('Tanggal Layanan')
    penyebab_abortus_id = fields.Many2one('master.abortus', 'Penyebab Abortus')
    masa_kebun = fields.Integer('Masa kebuntingan')
    komentar = fields.Text('Komentar')
    tps_id = fields.Many2one('tps.liter', 'TPS', related='id_sapi.tps_id', store=True)
    bcs = fields.Float('Body Condition Score', required=True)
    periode_id = fields.Many2one('periode.setoran', 'Periode')
    is_permohonan = fields.Boolean('Is Permohonan')

    @api.onchange('petugas_id')
    def _onchange_petugas_id(self):
        if self.petugas_id:
            self.jabatan_id = self.petugas_id.jabatan_id.id

    @api.onchange('peternak_id')
    def _onchange_peternak_id(self):
        if self.peternak_id:
            self.wilayah_id = self.peternak_id.wilayah_id.id

    @api.onchange('tgl_layanan')
    def _onchange_tgl_layanan(self):
        if self.tgl_layanan:
            periode_setoran_obj = self.env['periode.setoran']
            periode_setoran = periode_setoran_obj.search([
                ('periode_setoran_awal', '<=', self.tgl_layanan),
                ('periode_setoran_akhir', '>=', self.tgl_layanan)
            ])
            if periode_setoran:
                self.periode_id = periode_setoran.id
            else:
                # Jika tidak ada periode yang sesuai, Anda dapat menangani kasus ini sesuai kebutuhan Anda.
                # Misalnya, memberikan default atau memberikan pesan kesalahan.
                self.periode_id = False

    @api.model
    def create(self, vals):
        res = super(form_abortus, self).create(vals)
        kunjungan = self.env['form.kunjungan.gdfp'].search([('peternak_id', '=', res.peternak_id.id),('petugas_id', '=', res.petugas_id.id),
                                                            ('periode_id', '=', res.periode_id.id),('jenis_management', '=', '6')], limit=1)
        if not kunjungan:
            bcs = res.bcs
            vals = {
                'peternak_id'       : res.peternak_id.id,
                'petugas_id'        : res.petugas_id.id,
                'periode_id'        : res.periode_id.id,
                'jenis_management'  : '6',
                'total_bcs'         : res.bcs
            }
            rec= self.env['form.kunjungan.gdfp'].create(vals)
            vals = {
                        'kunjungan_gdfp_id'     : rec.id,
                        'nama_form'             : 'Form Abortus',
                        'bcs'                   : bcs
                    }
            self.env['history.form.line'].create(vals)
            count = len(rec.history_line)
            rec.write({'body_cond'  : bcs/count})
            rec._onchange_body_cond()
            rec._onchange_angka_morbi()

        else :
            vals = {
                        'kunjungan_gdfp_id'     : kunjungan.id,
                        'nama_form'             : 'Form Abortus',
                        'bcs'                   : res.bcs
                    }
            self.env['history.form.line'].create(vals)
            count = len(kunjungan.history_line)
            bcs = (kunjungan.total_bcs + res.bcs)
            vals = {
                'total_bcs'       : bcs,
                'body_cond'       : bcs/count
            }
            kunjungan.write(vals)

            kunjungan._onchange_body_cond()
            kunjungan._onchange_angka_morbi()


    
        return res

    # @api.model
    # def create(self, vals):
    #     res = super(form_abortus, self).create(vals)
    #     kunjungan = self.env['form.kunjungan.gdfp'].search([('peternak_id', '=', res.peternak_id.id),('petugas_id', '=', res.petugas_id.id),
    #                                                         ('periode_id', '=', res.periode_id.id),('jenis_management', '=', '6')], limit=1)
    #     if not kunjungan:
    #         bcs = res.bcs
    #         vals = {
    #             'peternak_id'       : res.peternak_id.id,
    #             'petugas_id'        : res.petugas_id.id,
    #             'periode_id'        : res.periode_id.id,
    #             'jenis_management'  : '6',
    #             'total_bcs'         : res.bcs,
    #             'body_cond'         : bcs/17
    #         }
    #         rec= self.env['form.kunjungan.gdfp'].create(vals)
    #         rec._onchange_body_cond()
    #         rec._onchange_angka_morbi()

    #     else :

    #         bcs = (kunjungan.total_bcs + res.bcs)
    #         vals = {
    #             'total_bcs'       : bcs,
    #             'body_cond'       : bcs/17
    #         }
    #         kunjungan.write(vals)

    #         kunjungan._onchange_body_cond()
    #         kunjungan._onchange_angka_morbi()


    
    #     return res

class form_pkb(models.Model):
    _name = 'form.pkb'
    _inherit = 'image.mixin'
    _rec_name = 'id_sapi'

    peternak_id = fields.Many2one('peternak.sapi', 'Anggota/Peternak')
    id_pemilik = fields.Char('ID Pemilik', related='peternak_id.kode_peternak')
    wilayah_id = fields.Many2one('master.wilayah', 'Wilayah')
    kelompok_id = fields.Many2one('peternak.group', related='peternak_id.kelompok_id')
    petugas_id = fields.Many2one('medical.physician', 'Petugas')
    jabatan_id = fields.Many2one('master.jabatan', ' Jabatan', readonly=False)
    id_sapi = fields.Many2one('sapi', 'Nama Sapi', domain="[('peternak_id', '=', peternak_id)]")
    eartag_id = fields.Char('ID Eartag Sapi')
    tgl_layanan = fields.Date('Tanggal Layanan')
    bcs = fields.Float('BCS')
    id_tanda_kebuntingan = fields.Many2one('master.tanda.kebuntingan', string='Tanda Kebuntingan')
    id_posisi = fields.Many2one('master.posisi', 'Posisi')
    tgl_ib_akhir = fields.Date('Tanggal IB Terakhir')
    umur_kebuntingan = fields.Integer('Umur Kebuntingan')
    tps_id = fields.Many2one('tps.liter', 'TPS', related='id_sapi.tps_id', store=True)
    bcs = fields.Float('Body Condition Score', required=True)
    periode_id = fields.Many2one('periode.setoran', 'Periode')
    cat_petugas = fields.Text('Catatan Petugas')
    is_permohonan = fields.Boolean('Is Permohonan')

    @api.model
    def create(self, vals):
        res = super(form_pkb, self).create(vals)
        kunjungan = self.env['form.kunjungan.gdfp'].search([('peternak_id', '=', res.peternak_id.id),('petugas_id', '=', res.petugas_id.id),
                                                            ('periode_id', '=', res.periode_id.id),('jenis_management', '=', '6')], limit=1)
        if not kunjungan:
            bcs = res.bcs
            vals = {
                'peternak_id'       : res.peternak_id.id,
                'petugas_id'        : res.petugas_id.id,
                'periode_id'        : res.periode_id.id,
                'jenis_management'  : '6',
                'total_bcs'         : res.bcs
            }
            rec= self.env['form.kunjungan.gdfp'].create(vals)
            vals = {
                        'kunjungan_gdfp_id'     : rec.id,
                        'nama_form'             : 'Form PKB',
                        'bcs'                   : bcs
                    }
            self.env['history.form.line'].create(vals)
            count = len(rec.history_line)
            rec.write({'body_cond'  : bcs/count})
            rec._onchange_body_cond()
            rec._onchange_angka_morbi()

        else :
            vals = {
                        'kunjungan_gdfp_id'     : kunjungan.id,
                        'nama_form'             : 'Form PKB',
                        'bcs'                   : res.bcs
                    }
            self.env['history.form.line'].create(vals)
            count = len(kunjungan.history_line)
            bcs = (kunjungan.total_bcs + res.bcs)
            vals = {
                'total_bcs'       : bcs,
                'body_cond'       : bcs/count
            }
            kunjungan.write(vals)

            kunjungan._onchange_body_cond()
            kunjungan._onchange_angka_morbi()


    
        return res

    @api.onchange('petugas_id')
    def _onchange_petugas_id(self):
        if self.petugas_id:
            self.jabatan_id = self.petugas_id.jabatan_id.id

    @api.onchange('peternak_id')
    def _onchange_peternak_id(self):
        if self.peternak_id:
            self.wilayah_id = self.peternak_id.wilayah_id.id

    @api.onchange('tgl_layanan')
    def _onchange_tgl_layanan(self):
        if self.tgl_layanan:
            periode_setoran_obj = self.env['periode.setoran']
            periode_setoran = periode_setoran_obj.search([
                ('periode_setoran_awal', '<=', self.tgl_layanan),
                ('periode_setoran_akhir', '>=', self.tgl_layanan)
            ])
            if periode_setoran:
                self.periode_id = periode_setoran.id
            else:
                # Jika tidak ada periode yang sesuai, Anda dapat menangani kasus ini sesuai kebutuhan Anda.
                # Misalnya, memberikan default atau memberikan pesan kesalahan.
                self.periode_id = False

class form_bsk(models.Model):
    _name = 'form.bsk'
    _inherit = 'image.mixin'
    _rec_name = 'id_sapi'

    peternak_id = fields.Many2one('peternak.sapi', 'Anggota/Peternak')
    id_pemilik = fields.Char('ID Pemilik', related='peternak_id.kode_peternak')
    kelompok_id = fields.Many2one('peternak.group', related='peternak_id.kelompok_id')
    petugas_id = fields.Many2one('medical.physician', 'Petugas')
    jabatan_id = fields.Many2one('master.jabatan', ' Jabatan', readonly=False)
    id_sapi = fields.Many2one('sapi', 'Nama Sapi', domain="[('peternak_id', '=', peternak_id)]")
    eartag_id = fields.Char('ID Eartag Sapi')
    tgl_layanan = fields.Date('Tanggal Layanan')
    cat_petugas = fields.Text('Catatan Petugas')
    tps_id = fields.Many2one('tps.liter', 'TPS', related='id_sapi.tps_id', store=True)
    bcs = fields.Float('Body Condition Score', required=True)

class form_dara_metestrus(models.Model):
    _name = 'form.dm'
    _rec_name = 'id_sapi'

    peternak_id = fields.Many2one('peternak.sapi', 'Anggota/Peternak')
    id_pemilik = fields.Char('ID Pemilik', related='peternak_id.kode_peternak')
    kelompok_id = fields.Many2one('peternak.group', related='peternak_id.kelompok_id')
    petugas_id = fields.Many2one('medical.physician', 'Petugas')
    jabatan_id = fields.Many2one('master.jabatan', ' Jabatan', readonly=False)
    id_sapi = fields.Many2one('sapi', 'Nama Sapi', domain="[('peternak_id', '=', peternak_id)]")
    eartag_id = fields.Char('ID Eartag Sapi')
    tgl_layanan = fields.Date('Tanggal Layanan')
    komentar = fields.Text('Komentar')
    tps_id = fields.Many2one('tps.liter', 'TPS', related='id_sapi.tps_id', store=True)
    bcs = fields.Float('Body Condition Score', required=True)

class form_mutasi(models.Model):
    _name = 'form.mutasi'
    _rec_name = 'id_sapi'

    peternak_id = fields.Many2one('peternak.sapi', 'Anggota/Peternak')
    id_pemilik = fields.Char('ID Pemilik', related='peternak_id.kode_peternak')
    wilayah_id = fields.Many2one('master.wilayah', 'Wilayah')
    kelompok_id = fields.Many2one('peternak.group', related='peternak_id.kelompok_id')
    petugas_id = fields.Many2one('medical.physician', 'Petugas')
    jabatan_id = fields.Many2one('master.jabatan', ' Jabatan', readonly=False)
    id_sapi = fields.Many2one('sapi', 'Nama Sapi', domain="[('peternak_id', '=', peternak_id)]")
    eartag_id = fields.Char('ID Eartag Sapi')
    tgl_layanan = fields.Date('Tanggal Layanan')
    id_jenis_mutasi = fields.Many2one('master.jenis.mutasi', 'Jenis Mutasi')
    mati = fields.Boolean('Mati')
    aktif = fields.Boolean('Aktif')
    alamat1 = fields.Char('Alamat 1')
    alamat2 = fields.Char('Alamat 2')
    penerimaan = fields.Float('Penerimaan')
    bertambah = fields.Boolean('Bertambah')
    cat_petugas = fields.Text('Catatan Petugas')
    tps_id = fields.Many2one('tps.liter', 'TPS', related='id_sapi.tps_id', store=True)
    bcs = fields.Float('Body Condition Score', required=True)
    periode_id = fields.Many2one('periode.setoran', 'Periode')
    is_permohonan = fields.Boolean('Is Permohonan')

    @api.model
    def create(self, vals):
        res = super(form_mutasi, self).create(vals)
        kunjungan = self.env['form.kunjungan.gdfp'].search([('peternak_id', '=', res.peternak_id.id),('petugas_id', '=', res.petugas_id.id),
                                                            ('periode_id', '=', res.periode_id.id),('jenis_management', '=', '6')], limit=1)
        if not kunjungan:
            bcs = res.bcs
            vals = {
                'peternak_id'       : res.peternak_id.id,
                'petugas_id'        : res.petugas_id.id,
                'periode_id'        : res.periode_id.id,
                'jenis_management'  : '6',
                'total_bcs'         : res.bcs
            }
            rec= self.env['form.kunjungan.gdfp'].create(vals)
            vals = {
                        'kunjungan_gdfp_id'     : rec.id,
                        'nama_form'             : 'Form Mutasi',
                        'bcs'                   : bcs
                    }
            self.env['history.form.line'].create(vals)
            count = len(rec.history_line)
            rec.write({'body_cond'  : bcs/count})
            rec._onchange_body_cond()
            rec._onchange_angka_morbi()

        else :
            vals = {
                        'kunjungan_gdfp_id'     : kunjungan.id,
                        'nama_form'             : 'Form Mutasi',
                        'bcs'                   : res.bcs
                    }
            self.env['history.form.line'].create(vals)
            count = len(kunjungan.history_line)
            bcs = (kunjungan.total_bcs + res.bcs)
            vals = {
                'total_bcs'       : bcs,
                'body_cond'       : bcs/count
            }
            kunjungan.write(vals)

            kunjungan._onchange_body_cond()
            kunjungan._onchange_angka_morbi()


    
        return res

    @api.onchange('petugas_id')
    def _onchange_petugas_id(self):
        if self.petugas_id:
            self.jabatan_id = self.petugas_id.jabatan_id.id

    @api.onchange('peternak_id')
    def _onchange_peternak_id(self):
        if self.peternak_id:
            self.wilayah_id = self.peternak_id.wilayah_id.id

    @api.onchange('tgl_layanan')
    def _onchange_tgl_layanan(self):
        if self.tgl_layanan:
            periode_setoran_obj = self.env['periode.setoran']
            periode_setoran = periode_setoran_obj.search([
                ('periode_setoran_awal', '<=', self.tgl_layanan),
                ('periode_setoran_akhir', '>=', self.tgl_layanan)
            ])
            if periode_setoran:
                self.periode_id = periode_setoran.id
            else:
                # Jika tidak ada periode yang sesuai, Anda dapat menangani kasus ini sesuai kebutuhan Anda.
                # Misalnya, memberikan default atau memberikan pesan kesalahan.
                self.periode_id = False

class form_et(models.Model):
    _name = 'form.et'
    # _rec_name = 'id_sapi'

    # peternak_id = fields.Many2one('peternak.sapi', 'Anggota/Peternak')
    # id_pemilik = fields.Char('ID Pemilik', related='peternak_id.kode_peternak')
    # kelompok_id = fields.Many2one('peternak.group', related='peternak_id.kelompok_id')
    # petugas_id = fields.Many2one('medical.physician', 'Petugas')
    # jabatan_id = fields.Many2one('master.jabatan', ' Jabatan', readonly=False)
    # id_sapi = fields.Many2one('sapi', 'Nama Sapi', domain="[('peternak_id', '=', peternak_id)]")
    # eartag_id = fields.Char('ID Eartag Sapi')
    # tgl_layanan = fields.Datetime('Tanggal Layanan')
    # kode_embrio = fields.Char('Kode Embrio')
    # id_pejantan = fields.Char('ID Pejantan')
    # id_donor = fields.Char('ID Donor')
    # biaya = fields.Float('Biaya')
    # cat_petugas = fields.Text('Catatan Petugas')
    # tps_id = fields.Many2one('tps.liter', 'TPS', related='id_sapi.tps_id', store=True)
    # bcs = fields.Float('Body Condition Score')

class form_gis(models.Model):
    _name = 'form.gis'
    _rec_name = 'id_sapi'

    peternak_id = fields.Many2one('peternak.sapi', 'Anggota/Peternak')
    id_pemilik = fields.Char('ID Pemilik', related='peternak_id.kode_peternak')
    wilayah_id = fields.Many2one('master.wilayah', 'Wilayah')
    kelompok_id = fields.Many2one('peternak.group', related='peternak_id.kelompok_id')
    petugas_id = fields.Many2one('medical.physician', 'Petugas')
    jabatan_id = fields.Many2one('master.jabatan', ' Jabatan', readonly=False)
    id_sapi = fields.Many2one('sapi', 'Nama Sapi', domain="[('peternak_id', '=', peternak_id)]")
    eartag_id = fields.Char('ID Eartag Sapi Lama')
    tgl_layanan = fields.Date('Tanggal Layanan')
    eartag_id_baru = fields.Char('ID Eartag Sapi Baru')
    cat_petugas = fields.Text('Catatan Petugas')
    image1 = fields.Char('Gambar1')
    image2 = fields.Char('Gambar2')
    image3 = fields.Char('Gambar3')
    tps_id = fields.Many2one('tps.liter', 'TPS', related='id_sapi.tps_id', store=True)
    bcs = fields.Float('Body Condition Score', required=True)
    periode_id = fields.Many2one('periode.setoran', 'Periode')
    is_permohonan = fields.Boolean('Is Permohonan')


    @api.model
    def create(self, vals):
        # Membuat record seperti biasa
        res = super(form_gis, self).create(vals)

        # Mengupdate eartag_id dari id_sapi sesuai dengan eartag_id_baru
        if res.id_sapi and res.eartag_id_baru:
            res.id_sapi.write({'eartag_id': res.eartag_id_baru})

        # Logika yang sudah ada untuk kunjungan dan history form line
        kunjungan = self.env['form.kunjungan.gdfp'].search([('peternak_id', '=', res.peternak_id.id),('petugas_id', '=', res.petugas_id.id),
                                                            ('periode_id', '=', res.periode_id.id),('jenis_management', '=', '6')], limit=1)
        if not kunjungan:
            bcs = res.bcs
            vals = {
                'peternak_id'       : res.peternak_id.id,
                'petugas_id'        : res.petugas_id.id,
                'periode_id'        : res.periode_id.id,
                'jenis_management'  : '6',
                'total_bcs'         : res.bcs
            }
            rec = self.env['form.kunjungan.gdfp'].create(vals)
            vals = {
                'kunjungan_gdfp_id'     : rec.id,
                'nama_form'             : 'Form GIS',
                'bcs'                   : bcs
            }
            self.env['history.form.line'].create(vals)
            count = len(rec.history_line)
            rec.write({'body_cond'  : bcs/count})
            rec._onchange_body_cond()
            rec._onchange_angka_morbi()
        else:
            vals = {
                'kunjungan_gdfp_id'     : kunjungan.id,
                'nama_form'             : 'Form GIS',
                'bcs'                   : res.bcs
            }
            self.env['history.form.line'].create(vals)
            count = len(kunjungan.history_line)
            bcs = (kunjungan.total_bcs + res.bcs)
            vals = {
                'total_bcs'       : bcs,
                'body_cond'       : bcs/count
            }
            kunjungan.write(vals)

            kunjungan._onchange_body_cond()
            kunjungan._onchange_angka_morbi()

        return res

    def write(self, vals):
        # Proses update data seperti biasa
        res = super(form_gis, self).write(vals)

        # Jika eartag_id_baru diupdate, maka eartag_id di id_sapi juga diupdate
        if 'eartag_id_baru' in vals and self.id_sapi:
            self.id_sapi.write({'eartag_id': vals.get('eartag_id_baru')})

        return res

    @api.onchange('petugas_id')
    def _onchange_petugas_id(self):
        if self.petugas_id:
            self.jabatan_id = self.petugas_id.jabatan_id.id

    @api.onchange('peternak_id')
    def _onchange_peternak_id(self):
        if self.peternak_id:
            self.wilayah_id = self.peternak_id.wilayah_id.id

    @api.onchange('tgl_layanan')
    def _onchange_tgl_layanan(self):
        if self.tgl_layanan:
            periode_setoran_obj = self.env['periode.setoran']
            periode_setoran = periode_setoran_obj.search([
                ('periode_setoran_awal', '<=', self.tgl_layanan),
                ('periode_setoran_akhir', '>=', self.tgl_layanan)
            ])
            if periode_setoran:
                self.periode_id = periode_setoran.id
            else:
                # Jika tidak ada periode yang sesuai, Anda dapat menangani kasus ini sesuai kebutuhan Anda.
                # Misalnya, memberikan default atau memberikan pesan kesalahan.
                self.periode_id = False

class form_hormon(models.Model):
    _name = 'form.hormon'
    _inherit = 'image.mixin'
    _rec_name = 'eartag_id'

    petugas_id = fields.Many2one('medical.physician', 'Petugas')
    jabatan_id = fields.Many2one('master.jabatan', ' Jabatan', readonly=False)
    peternak_id = fields.Many2one('peternak.sapi', 'Anggota/Peternak') 
    id_pemilik = fields.Char('ID Pemilik')
    id_sapi = fields.Many2one('sapi', 'Nama Sapi', domain="[('peternak_id', '=', peternak_id)]")
    eartag_id = fields.Char('ID Eartag Sapi')
    tgl_layanan = fields.Date('Tanggal Layanan')
    cat_petugas = fields.Text('Catatan Petugas')
    tps_id = fields.Many2one('tps.liter', 'TPS', related='id_sapi.tps_id', store=True)
    bcs = fields.Float('Body Condition Score', required=True)

class form_ib(models.Model):
    _name = 'form.ib'
    _inherit = 'image.mixin'
    _rec_name = 'eartag_id'

    peternak_id = fields.Many2one('peternak.sapi', 'Anggota/Peternak')
    id_pemilik = fields.Char('ID Pemilik', related='peternak_id.kode_peternak')
    wilayah_id = fields.Many2one('master.wilayah', 'Wilayah')
    kelompok_id = fields.Many2one('peternak.group', related='peternak_id.kelompok_id')
    petugas_id = fields.Many2one('medical.physician', 'Petugas')
    jabatan_id = fields.Many2one('master.jabatan', ' Jabatan', readonly=False)
    layanan_id = fields.Many2one('jenis.pelayanan', 'Jenis Layanan')
    id_sapi = fields.Many2one('sapi', 'Nama Sapi', domain="[('peternak_id', '=', peternak_id)]")
    eartag_id = fields.Char('ID Eartag Sapi')
    tgl_layanan = fields.Date('Tanggal Layanan')
    # id_bcs = fields.Float('BCS')
    id_status_reproduksi = fields.Many2one('master.status.reproduksi', 'Status Reproduksi')
    id_pejantan = fields.Many2one('master.semen.beku', 'Nama Pejantan')
    no_pejantan = fields.Char('Kode Pejantan')
    no_batch = fields.Char('No Batch')
    lama_birahi = fields.Integer('Lama Birahi')
    ib_ke = fields.Integer('IB Ke')
    nama_pengamat_birahi = fields.Char('Pengamat Birahi')
    dose = fields.Integer('Dosis', required=True)
    cat_petugas = fields.Text('Catatan Petugas')
    tps_id = fields.Many2one('tps.liter', 'TPS', related='id_sapi.tps_id', store=True)
    bcs = fields.Float('Body Condition Score', required=True)
    semen_beku = fields.Many2one('master.semen.beku', 'Semen Beku (Pejantan)')

    # list_formib_ids = fields.One2many('ib.line', 'id_sapi', 'IB', track_visibility='onchange',
    #                                   compute='_compute_list_formib_ids')
    periode_id = fields.Many2one('periode.setoran', 'Periode')
    is_permohonan = fields.Boolean('Is Permohonan')


    @api.model
    def create(self, vals):
        res = super(form_ib, self).create(vals)
        kunjungan = self.env['form.kunjungan.gdfp'].search([('peternak_id', '=', res.peternak_id.id),('petugas_id', '=', res.petugas_id.id),
                                                            ('periode_id', '=', res.periode_id.id),('jenis_management', '=', '6')], limit=1)
        if not kunjungan:
            bcs = res.bcs
            vals = {
                'peternak_id'       : res.peternak_id.id,
                'petugas_id'        : res.petugas_id.id,
                'periode_id'        : res.periode_id.id,
                'jenis_management'  : '6',
                'total_bcs'         : res.bcs
            }
            rec= self.env['form.kunjungan.gdfp'].create(vals)
            vals = {
                        'kunjungan_gdfp_id'     : rec.id,
                        'nama_form'             : 'Form IB',
                        'bcs'                   : bcs
                    }
            self.env['history.form.line'].create(vals)
            count = len(rec.history_line)
            rec.write({'body_cond'  : bcs/count})
            rec._onchange_body_cond()
            rec._onchange_angka_morbi()

        else :
            vals = {
                        'kunjungan_gdfp_id'     : kunjungan.id,
                        'nama_form'             : 'Form IB',
                        'bcs'                   : res.bcs
                    }
            self.env['history.form.line'].create(vals)
            count = len(kunjungan.history_line)
            bcs = (kunjungan.total_bcs + res.bcs)
            vals = {
                'total_bcs'       : bcs,
                'body_cond'       : bcs/count
            }
            kunjungan.write(vals)

            kunjungan._onchange_body_cond()
            kunjungan._onchange_angka_morbi()


    
        return res

    @api.onchange('petugas_id')
    def _onchange_petugas_id(self):
        if self.petugas_id:
            self.jabatan_id = self.petugas_id.jabatan_id.id

    @api.onchange('peternak_id')
    def _onchange_peternak_id(self):
        if self.peternak_id:
            self.wilayah_id = self.peternak_id.wilayah_id.id

    @api.onchange('id_status_reproduksi')
    def _onchange_id_status_reproduksi(self):
        # Pastikan id_status_reproduksi di objek sapi diisi sesuai dengan form_ib
        if self.id_sapi:
            self.id_sapi.id_status_reproduksi = self.id_status_reproduksi

    @api.model
    def create(self, vals):
        form_ib_record = super(form_ib, self).create(vals)

        # Cari atau buat record sapi yang sesuai jika belum ada
        sapi_record = self.env['sapi'].search([('id', '=', form_ib_record.id_sapi.id)])
        if not sapi_record:
            vals_sapi = {
                'partner_id': form_ib_record.peternak_id.id,
                'first_name': form_ib_record.id_sapi.name,  # Gantilah dengan field yang sesuai
                # Isi field lainnya sesuai dengan kebutuhan
            }
            sapi_record = self.env['sapi'].create(vals_sapi)

        # Tambahkan record ib.line ke list_formib_ids pada record sapi
        ib_line_vals = {
            'master_sapi_id': sapi_record.id,
            'id_sapi': form_ib_record.id_sapi.id,
            'ib_ke': form_ib_record.ib_ke,
            'tgl': form_ib_record.tgl_layanan,  # Gantilah dengan field yang sesuai
            # 'id_pejantan': form_ib_record.id_pejantan.id,
            # Isi field lainnya sesuai dengan kebutuhan
        }
        self.env['ib.line'].create(ib_line_vals)

        # Mengembalikan ID form_ib yang baru dibuat
        return form_ib_record

    @api.onchange('tgl_layanan')
    def _onchange_tgl_layanan(self):
        if self.tgl_layanan:
            periode_setoran_obj = self.env['periode.setoran']
            periode_setoran = periode_setoran_obj.search([
                ('periode_setoran_awal', '<=', self.tgl_layanan),
                ('periode_setoran_akhir', '>=', self.tgl_layanan)
            ])
            if periode_setoran:
                self.periode_id = periode_setoran.id
            else:
                # Jika tidak ada periode yang sesuai, Anda dapat menangani kasus ini sesuai kebutuhan Anda.
                # Misalnya, memberikan default atau memberikan pesan kesalahan.
                self.periode_id = False

# class InheritSapi(models.Model):
#     _name = 'sapi'
#     _description = 'Inherit Sapi'
#
#     id_pejantan = fields.Many2one('master.semen.beku', 'Pejantan')

class form_pedet(models.Model):
    _name = 'form.pedet'
    _inherit = 'image.mixin'
    _rec_name = 'eartag_id'

    petugas_id = fields.Many2one('medical.physician', 'Petugas')
    jabatan_id = fields.Many2one('master.jabatan', ' Jabatan', readonly=False)
    id_pemilik = fields.Char('ID Pemilik')
    eartag_id = fields.Char('ID Eartag Sapi')
    tgl_layanan = fields.Date('Tanggal Layanan')
    cat_petugas = fields.Text('Catatan Petugas')


class form_kk(models.Model):
    _name = 'form.kk'
    _inherit = 'image.mixin'
    _rec_name = 'eartag_id'

    peternak_id = fields.Many2one('peternak.sapi', 'Anggota/Peternak')
    id_pemilik = fields.Char('ID Pemilik', related='peternak_id.kode_peternak')
    wilayah_id = fields.Many2one('master.wilayah', 'Wilayah')
    kelompok_id = fields.Many2one('peternak.group', related='peternak_id.kelompok_id')
    petugas_id = fields.Many2one('medical.physician', 'Petugas')
    jabatan_id = fields.Many2one('master.jabatan', ' Jabatan', readonly=False)
    id_sapi = fields.Many2one('sapi', 'Nama Sapi', domain="[('peternak_id', '=', peternak_id)]")
    eartag_id = fields.Char('ID Eartag Sapi')
    tgl_layanan = fields.Date('Tanggal Layanan')
    cat_petugas = fields.Text('Catatan Petugas')
    jenis_pengeringan_id = fields.Many2one('master.pengeringan', 'Jenis Pengeringan')
    # obat_depan_kiri = fields.Char('Depan Kiri')
    # obat_depan_kanan = fields.Char('Depan Kanan')
    # obat_blkg_kiri = fields.Char('Belakang Kiri')
    # obat_blkg_kanan = fields.Char('Belakang Kanan')
    pengobatan1 = fields.Many2one('master.obat', 'Pengobatan Lain#1')
    pengobatan2 = fields.Many2one('master.obat', 'Pengobatan Lain#2')
    saran = fields.Text('Saran')
    tps_id = fields.Many2one('tps.liter', 'TPS', related='id_sapi.tps_id', store=True)
    bcs = fields.Float('Body Condition Score', required=True)
    periode_id = fields.Many2one('periode.setoran', 'Periode')
    is_permohonan = fields.Boolean('Is Permohonan')


    @api.model
    def create(self, vals):
        res = super(form_kk, self).create(vals)
        kunjungan = self.env['form.kunjungan.gdfp'].search([('peternak_id', '=', res.peternak_id.id),('petugas_id', '=', res.petugas_id.id),
                                                            ('periode_id', '=', res.periode_id.id),('jenis_management', '=', '6')], limit=1)
        if not kunjungan:
            bcs = res.bcs
            vals = {
                'peternak_id'       : res.peternak_id.id,
                'petugas_id'        : res.petugas_id.id,
                'periode_id'        : res.periode_id.id,
                'jenis_management'  : '6',
                'total_bcs'         : res.bcs
            }
            rec= self.env['form.kunjungan.gdfp'].create(vals)
            vals = {
                        'kunjungan_gdfp_id'     : rec.id,
                        'nama_form'             : 'Form Kering Kandang',
                        'bcs'                   : bcs
                    }
            self.env['history.form.line'].create(vals)
            count = len(rec.history_line)
            rec.write({'body_cond'  : bcs/count})
            rec._onchange_body_cond()
            rec._onchange_angka_morbi()

        else :
            vals = {
                        'kunjungan_gdfp_id'     : kunjungan.id,
                        'nama_form'             : 'Form Kering Kandang',
                        'bcs'                   : res.bcs
                    }
            self.env['history.form.line'].create(vals)
            count = len(kunjungan.history_line)
            bcs = (kunjungan.total_bcs + res.bcs)
            vals = {
                'total_bcs'       : bcs,
                'body_cond'       : bcs/count
            }
            kunjungan.write(vals)

            kunjungan._onchange_body_cond()
            kunjungan._onchange_angka_morbi()


    
        return res

    @api.onchange('petugas_id')
    def _onchange_petugas_id(self):
        if self.petugas_id:
            self.jabatan_id = self.petugas_id.jabatan_id.id

    @api.onchange('peternak_id')
    def _onchange_peternak_id(self):
        if self.peternak_id:
            self.wilayah_id = self.peternak_id.wilayah_id.id

    @api.onchange('tgl_layanan')
    def _onchange_tgl_layanan(self):
        if self.tgl_layanan:
            periode_setoran_obj = self.env['periode.setoran']
            periode_setoran = periode_setoran_obj.search([
                ('periode_setoran_awal', '<=', self.tgl_layanan),
                ('periode_setoran_akhir', '>=', self.tgl_layanan)
            ])
            if periode_setoran:
                self.periode_id = periode_setoran.id
            else:
                # Jika tidak ada periode yang sesuai, Anda dapat menangani kasus ini sesuai kebutuhan Anda.
                # Misalnya, memberikan default atau memberikan pesan kesalahan.
                self.periode_id = False

class form_masuk(models.Model):
    _name = 'form.masuk'
    _inherit = 'image.mixin'
    _rec_name = 'eartag_id'

    kelompok_id = fields.Many2one('peternak.group', related='peternak_id.kelompok_id')
    peternak_id = fields.Many2one('peternak.sapi', 'Anggota/Peternak')
    id_pemilik = fields.Char('ID Pemilik', related='peternak_id.kode_peternak')
    wilayah_id = fields.Many2one('master.wilayah', 'Wilayah')
    petugas_id = fields.Many2one('medical.physician', 'Petugas')
    jabatan_id = fields.Many2one('master.jabatan', ' Jabatan', readonly=False)
    eartag_id = fields.Char('ID Eartag Sapi')
    tgl_layanan = fields.Date('Tanggal Layanan')
    cat_petugas = fields.Text('Catatan Petugas')
    eartag_id = fields.Char('EarTag')
    telinga_ki_ka = fields.Selection([
        ('l', 'Kiri'),
        ('r', 'Kanan'),
    ],'Telinga Ki/Ka')
    nama_sapi = fields.Char('Nama Sapi')
    tipe_sapi_id = fields.Many2one('master.tipe.sapi', 'Tipe Sapi')
    tgl_ident = fields.Date('Tanggal Identifikasi')
    breed_id = fields.Many2one('master.breed', 'Breed')
    metoda_id = fields.Many2one('master.metoda', 'Metoda')
    tgl_lahir = fields.Date('Tanggal Lahir')
    et = fields.Selection(
        [
            ('y', 'Ya'),
            ('t', 'Tidak'),
        ], "Hasil ET")
    kembar = fields.Selection([
        ('y', 'Ya'),
        ('t', 'Tidak')
    ], string='Kembar')
    tie = fields.Char('TIE')
    kode_klhrn_id = fields.Many2one('master.kode.kelahiran', 'Kode Kelahiran')
    stts_reprod_id = fields.Many2one('master.status.reproduksi', 'Status Produksi')
    stts_laktasi_id = fields.Many2one('master.status.laktasi', 'Status Laktasi')
    lak_ke = fields.Char('Laktasi Ke')
    ibu_id = fields.Many2one('sapi', 'Indukan')
    eartag_ibu = fields.Char('Kode Eartag Ibu')
    ayah_id = fields.Many2one('sapi', 'Bapak')
    pejantan_id = fields.Many2one('pejantan', 'Pejantan')
    eartag_ayah = fields.Char('Kode Eartag Ayah', )
    tps_id = fields.Many2one('tps.liter', 'TPS', related='peternak_id.tps_id', readonly=False)
    bcs = fields.Float('Body Condition Score' , required=True)
    periode_id = fields.Many2one('periode.setoran', 'Periode')
    state = fields.Selection([
        ('tdk_ada', 'Tidak Ada'),
        ('kering', 'Kering'),
        ('laktasi', 'Laktasi'),
    ], string='Status Sapi', readonly=False, required=True)
    image = fields.Binary('Image')
    status_aktif = fields.Selection([
        ('a', 'Aktif'),
        ('ta', 'Tidak Aktif'),
    ], "Status Aktif")
    is_permohonan = fields.Boolean('Is Permohonan')
    sex = fields.Selection([
        ('m', 'Male'),
        ('f', 'Female'),
        ('o', 'Other')
    ], 'Gender', required=True, default='m')


    @api.model
    def create(self, values):
        # Ensure 'peternak_id' is set
        if 'peternak_id' not in values or not values['peternak_id']:
            raise ValueError("ID Peternak diperlukan.")

        # Create cow record with reference to form_masuk
        sapi_record_values = {
            'peternak_id': values.get('peternak_id'),
            'first_name': values.get('nama_sapi'),
            'eartag_id': values.get('eartag_id'),
            'state': values.get('state'),
            'date_of_birth': values.get('tgl_lahir'),
            'tgl_identifikasi': values.get('tgl_ident'),
            'tipe_id': values.get('tipe_sapi_id'),
            'kembar': values.get('kembar'),
            'metoda_id': values.get('metoda_id'),
            'breed_id': values.get('breed_id'),
            'tps_id': values.get('tps_id'),
            'id_induk': values.get('ibu_id'),
            # 'id_ayah': values.get('ayah_id'),
            'pejantan_id': values.get('pejantan_id'),
            'image_1920': values.get('image'),
            'id_status_reproduksi': values.get('stts_reprod_id'),
            'status_aktif': values.get('status_aktif'),
            'posisi_eartag': values.get('telinga_ki_ka'),
            'sex': values.get('sex'),
        }
        # Create cow record
        sapi = self.env['sapi'].create(sapi_record_values)

        # Create form_masuk record
        res = super(form_masuk, self).create(values)

        # Logic for form.kunjungan.gdfp and history.form.line
        kunjungan = self.env['form.kunjungan.gdfp'].search([('peternak_id', '=', res.peternak_id.id),('petugas_id', '=', res.petugas_id.id),
                                                            ('periode_id', '=', res.periode_id.id),('jenis_management', '=', '6')], limit=1)
        if not kunjungan:
            bcs = res.bcs
            kunjungan_vals = {
                'peternak_id': res.peternak_id.id,
                'petugas_id': res.petugas_id.id,
                'periode_id': res.periode_id.id,
                'jenis_management': '6',
                'total_bcs': res.bcs
            }
            kunjungan_rec = self.env['form.kunjungan.gdfp'].create(kunjungan_vals)
            history_vals = {
                'kunjungan_gdfp_id': kunjungan_rec.id,
                'nama_form': 'Form Masuk',
                'bcs': bcs
            }
            self.env['history.form.line'].create(history_vals)
            count = len(kunjungan_rec.history_line)
            kunjungan_rec.write({'body_cond': bcs / count})
            kunjungan_rec._onchange_body_cond()
            kunjungan_rec._onchange_angka_morbi()
        else:
            history_vals = {
                'kunjungan_gdfp_id': kunjungan.id,
                'nama_form': 'Form Masuk',
                'bcs': res.bcs
            }
            self.env['history.form.line'].create(history_vals)
            count = len(kunjungan.history_line)
            bcs = (kunjungan.total_bcs + res.bcs)
            kunjungan_vals = {
                'total_bcs': bcs,
                'body_cond': bcs / count
            }
            kunjungan.write(kunjungan_vals)
            kunjungan._onchange_body_cond()
            kunjungan._onchange_angka_morbi()

        return res

    @api.onchange('petugas_id')
    def _onchange_petugas_id(self):
        if self.petugas_id:
            self.jabatan_id = self.petugas_id.jabatan_id.id

    @api.onchange('peternak_id')
    def _onchange_peternak_id(self):
        if self.peternak_id:
            self.wilayah_id = self.peternak_id.wilayah_id.id

    @api.onchange('tgl_layanan')
    def _onchange_tgl_layanan(self):
        if self.tgl_layanan:
            periode_setoran_obj = self.env['periode.setoran']
            periode_setoran = periode_setoran_obj.search([
                ('periode_setoran_awal', '<=', self.tgl_layanan),
                ('periode_setoran_akhir', '>=', self.tgl_layanan)
            ])
            if periode_setoran:
                self.periode_id = periode_setoran.id
            else:
                # Jika tidak ada periode yang sesuai, Anda dapat menangani kasus ini sesuai kebutuhan Anda.
                # Misalnya, memberikan default atau memberikan pesan kesalahan.
                self.periode_id = False


class form_melahirkan(models.Model):
    _name = 'form.melahirkan'
    _rec_name = 'id_pemilik'

    kelompok_id = fields.Many2one('peternak.group', related='peternak_id.kelompok_id')
    peternak_id = fields.Many2one('peternak.sapi', 'Anggota/Peternak')
    id_pemilik = fields.Char('ID Pemilik', related='peternak_id.kode_peternak')
    wilayah_id = fields.Many2one('master.wilayah', 'Wilayah')
    tgl_layanan = fields.Date('Tanggal Layanan')
    nama_sapi = fields.Char('Nama Sapi')
    kode_eartag = fields.Char('Kode Eartag')
    petugas_id = fields.Many2one('medical.physician', 'Petugas')
    jabatan_id = fields.Many2one('master.jabatan', ' Jabatan', readonly=False)
    ibu_id = fields.Many2one('sapi', 'Indukan')
    eartag_ibu = fields.Char(related='ibu_id.eartag_id', string='Kode Eartag Ibu')
    ayah_id = fields.Many2one('sapi', 'Bapak')
    eartag_ayah = fields.Char(related='ayah_id.eartag_id', string='Kode Eartag Ayah', )
    tgl_lahir = fields.Datetime('Tanggal Lahir', required=True)
    status_lahir = fields.Selection([('hidup', 'Hidup'), ('mati', 'Mati')], string="Status Lahir")
    status_pelihara = fields.Selection([('pelihara', 'Pelihara'), ('jual', 'Jual')], string="Status Pelihara")
    jenis_kelamin = fields.Selection([('m', 'Male'), ('f', 'Female')], string="Sex")
    berat_lahir = fields.Integer('Berat Lahir')
    kondisi_lahir = fields.Selection([('lancar', 'Lancar'), ('sedikit sulit', 'Sedikit Sulit'), ('butuh bantuan', 'Butuh Bantuan'), ('ditarik paksa', 'Ditarik Paksa'), ('ekstrim sulit', 'Ekstrim Sulit')], string="Kondisi Lahir")
    jumlah_lahir = fields.Integer('Jumlah Lahir')
    jumlah_pelihara = fields.Integer('Jumlah Pelihara')
    jumlah_mati = fields.Integer('Jumlah Mati')
    jumlah_dijual = fields.Integer('Jumlah Dijual')
    harga_jual = fields.Integer('Harga Jual')
    keadaan_saat_melahirkan_id = fields.Many2one('master.keadaan.melahirkan', 'Keadaan Saat Melahirkan')
    cat_petugas = fields.Text('Catatan Petugas')
    tps_id = fields.Many2one('tps.liter', 'TPS', related='peternak_id.tps_id', store=True)
    bcs = fields.Float('Body Condition Score', required=True)

    # list_form_melahirkan_ids = fields.One2many('melahirkan.line', 'ibu_id', 'Melahirkan', track_visibility='onchange')
    periode_id = fields.Many2one('periode.setoran', 'Periode')
    pejantans_id = fields.Many2one('master.semen.beku', 'Pejantan')
    pejantan_id = fields.Many2one('pejantan', 'Pejantan')
    is_permohonan = fields.Boolean('Is Permohonan')


    @api.model
    def create(self, vals):
        res = super(form_melahirkan, self).create(vals)
        kunjungan = self.env['form.kunjungan.gdfp'].search([('peternak_id', '=', res.peternak_id.id),('petugas_id', '=', res.petugas_id.id),
                                                            ('periode_id', '=', res.periode_id.id),('jenis_management', '=', '6')], limit=1)
        if not kunjungan:
            bcs = res.bcs
            vals = {
                'peternak_id'       : res.peternak_id.id,
                'petugas_id'        : res.petugas_id.id,
                'periode_id'        : res.periode_id.id,
                'jenis_management'  : '6',
                'total_bcs'         : res.bcs
            }
            rec= self.env['form.kunjungan.gdfp'].create(vals)
            vals = {
                        'kunjungan_gdfp_id'     : rec.id,
                        'nama_form'             : 'Form Melahirkan',
                        'bcs'                   : bcs
                    }
            self.env['history.form.line'].create(vals)
            count = len(rec.history_line)
            rec.write({'body_cond'  : bcs/count})
            rec._onchange_body_cond()
            rec._onchange_angka_morbi()

        else :
            vals = {
                        'kunjungan_gdfp_id'     : kunjungan.id,
                        'nama_form'             : 'Form Melahirkan',
                        'bcs'                   : res.bcs
                    }
            self.env['history.form.line'].create(vals)
            count = len(kunjungan.history_line)
            bcs = (kunjungan.total_bcs + res.bcs)
            vals = {
                'total_bcs'       : bcs,
                'body_cond'       : bcs/count
            }
            kunjungan.write(vals)

            kunjungan._onchange_body_cond()
            kunjungan._onchange_angka_morbi()


    
        return res

    # @api.onchange('status_lahir')
    # def onchange_status_lahir(self):
    #     if self.status_lahir and self.id_sapi:
    #         self.id_sapi.write({'status_lahir': 'h' if self.status_lahir == 'hidup' else 'm'})

    @api.onchange('petugas_id')
    def _onchange_petugas_id(self):
        if self.petugas_id:
            self.jabatan_id = self.petugas_id.jabatan_id.id

    @api.onchange('peternak_id')
    def _onchange_peternak_id(self):
        if self.peternak_id:
            self.wilayah_id = self.peternak_id.wilayah_id.id

    @api.onchange('tgl_layanan')
    def _onchange_tgl_layanan(self):
        if self.tgl_layanan:
            periode_setoran_obj = self.env['periode.setoran']
            periode_setoran = periode_setoran_obj.search([
                ('periode_setoran_awal', '<=', self.tgl_layanan),
                ('periode_setoran_akhir', '>=', self.tgl_layanan)
            ])
            if periode_setoran:
                self.periode_id = periode_setoran.id
            else:
                # Jika tidak ada periode yang sesuai, Anda dapat menangani kasus ini sesuai kebutuhan Anda.
                # Misalnya, memberikan default atau memberikan pesan kesalahan.
                self.periode_id = False

    # @api.model
    # def create(self, vals):
    #     form_melahirkan_record = super(form_melahirkan, self).create(vals)

    #     # Cari atau buat record sapi yang sesuai jika belum ada
    #     sapi_record = self.env['sapi'].search([('id', '=', form_melahirkan_record.ibu_id.id)])
    #     if not sapi_record:
    #         vals_sapi = {
    #             'partner_id': form_melahirkan_record.peternak_id.id,
    #             'first_name': form_melahirkan_record.ibu_id.name,  # Gantilah dengan field yang sesuai
    #             # Isi field lainnya sesuai dengan kebutuhan
    #         }
    #         sapi_record = self.env['sapi'].create(vals_sapi)

    #     # Tambahkan record ib.line ke list_formib_ids pada record sapi
    #     melahirkan_line_vals = {
    #         'master_sapi_id': sapi_record.id,
    #         'ibu_id': form_melahirkan_record.ibu_id.id,
    #         # 'kode_eartag': form_melahirkan_record.kode_eartag,
    #         # 'jenis_kelamin':form_melahirkan_record.jenis_kelamin,
    #         'tgl': form_melahirkan_record.tgl_layanan,  # Gantilah dengan field yang sesuai
    #         # Isi field lainnya sesuai dengan kebutuhan
    #     }
    #     self.env['melahirkan.line'].create(melahirkan_line_vals)

    #     return form_melahirkan_record

    @api.onchange('tgl_layanan')
    def _onchange_tgl_layanan(self):
        if self.tgl_layanan:
            periode_setoran_obj = self.env['periode.setoran']
            periode_setoran = periode_setoran_obj.search([
                ('periode_setoran_awal', '<=', self.tgl_layanan),
                ('periode_setoran_akhir', '>=', self.tgl_layanan)
            ])
            if periode_setoran:
                self.periode_id = periode_setoran.id
            else:
                # Jika tidak ada periode yang sesuai, Anda dapat menangani kasus ini sesuai kebutuhan Anda.
                # Misalnya, memberikan default atau memberikan pesan kesalahan.
                self.periode_id = False

class form_nkt(models.Model):
    _name = 'form.nkt'
    _rec_name = 'eartag_id'

    peternak_id = fields.Many2one('peternak.sapi', 'Anggota/Peternak')
    id_pemilik = fields.Char('ID Pemilik', related='peternak_id.kode_peternak')
    wilayah_id = fields.Many2one('master.wilayah', 'Wilayah')
    kelompok_id = fields.Many2one('peternak.group', related='peternak_id.kelompok_id')
    petugas_id = fields.Many2one('medical.physician', 'Petugas')
    jabatan_id = fields.Many2one('master.jabatan', ' Jabatan', readonly=False)
    id_sapi = fields.Many2one('sapi', 'Nama Sapi', domain="[('peternak_id', '=', peternak_id)]")
    eartag_id = fields.Char('ID Eartag Sapi')
    tgl_layanan = fields.Date('Tanggal Layanan')
    bcs = fields.Float('BCS')
    berat = fields.Float('Berat')
    tinggi = fields.Float('Tinggi')
    cat_petugas = fields.Text('Catatan Petugas')
    tps_id = fields.Many2one('tps.liter', 'TPS', related='id_sapi.tps_id', store=True)
    bcs = fields.Float('Body Condition Score', required=True)
    periode_id = fields.Many2one('periode.setoran', 'Periode')
    is_permohonan = fields.Boolean('Is Permohonan')


    @api.model
    def create(self, vals):
        res = super(form_nkt, self).create(vals)
        kunjungan = self.env['form.kunjungan.gdfp'].search([('peternak_id', '=', res.peternak_id.id),('petugas_id', '=', res.petugas_id.id),
                                                            ('periode_id', '=', res.periode_id.id),('jenis_management', '=', '6')], limit=1)
        if not kunjungan:
            bcs = res.bcs
            vals = {
                'peternak_id'       : res.peternak_id.id,
                'petugas_id'        : res.petugas_id.id,
                'periode_id'        : res.periode_id.id,
                'jenis_management'  : '6',
                'total_bcs'         : res.bcs
            }
            rec= self.env['form.kunjungan.gdfp'].create(vals)
            vals = {
                        'kunjungan_gdfp_id'     : rec.id,
                        'nama_form'             : 'Form NKT',
                        'bcs'                   : bcs
                    }
            self.env['history.form.line'].create(vals)
            count = len(rec.history_line)
            rec.write({'body_cond'  : bcs/count})
            rec._onchange_body_cond()
            rec._onchange_angka_morbi()

        else :
            vals = {
                        'kunjungan_gdfp_id'     : kunjungan.id,
                        'nama_form'             : 'Form NKT',
                        'bcs'                   : res.bcs
                    }
            self.env['history.form.line'].create(vals)
            count = len(kunjungan.history_line)
            bcs = (kunjungan.total_bcs + res.bcs)
            vals = {
                'total_bcs'       : bcs,
                'body_cond'       : bcs/count
            }
            kunjungan.write(vals)

            kunjungan._onchange_body_cond()
            kunjungan._onchange_angka_morbi()


    
        return res

    @api.onchange('petugas_id')
    def _onchange_petugas_id(self):
        if self.petugas_id:
            self.jabatan_id = self.petugas_id.jabatan_id.id

    @api.onchange('peternak_id')
    def _onchange_peternak_id(self):
        if self.peternak_id:
            self.wilayah_id = self.peternak_id.wilayah_id.id

    @api.onchange('berat', 'tinggi')
    def _onchange_berat_tinggi(self):
        # Pastikan id_sapi diisi dan isi field berat dan tinggi di objek sapi dengan nilai yang sesuai
        if self.id_sapi:
            self.id_sapi.write({'bobot': self.berat, 'height': self.tinggi})

    @api.onchange('tgl_layanan')
    def _onchange_tgl_layanan(self):
        if self.tgl_layanan:
            periode_setoran_obj = self.env['periode.setoran']
            periode_setoran = periode_setoran_obj.search([
                ('periode_setoran_awal', '<=', self.tgl_layanan),
                ('periode_setoran_akhir', '>=', self.tgl_layanan)
            ])
            if periode_setoran:
                self.periode_id = periode_setoran.id
            else:
                # Jika tidak ada periode yang sesuai, Anda dapat menangani kasus ini sesuai kebutuhan Anda.
                # Misalnya, memberikan default atau memberikan pesan kesalahan.
                self.periode_id = False

class form_pr(models.Model):
    _name = 'form.pr'
    _rec_name = 'eartag_id'

    peternak_id = fields.Many2one('peternak.sapi', 'Anggota/Peternak')
    id_pemilik = fields.Char('ID Pemilik', related='peternak_id.kode_peternak')
    wilayah_id = fields.Many2one('master.wilayah', 'Wilayah')
    kelompok_id = fields.Many2one('peternak.group', related='peternak_id.kelompok_id')
    petugas_id = fields.Many2one('medical.physician', 'Petugas')
    jabatan_id = fields.Many2one('master.jabatan', ' Jabatan', readonly=False)
    id_sapi = fields.Many2one('sapi', 'Nama Sapi', domain="[('peternak_id', '=', peternak_id)]")
    eartag_id = fields.Char('ID Eartag Sapi')
    tgl_layanan = fields.Date('Tanggal Layanan')
    cat_petugas = fields.Text('Catatan Petugas')
    alsn_pal_rek_id = fields.Many2one('master.alasan.palpasi', 'Alasan Palpasi Rektal')
    uterus_id = fields.Many2one('master.temuan.uterus', 'Uterus')
    ovarikiri_id = fields.Many2one('master.temuan.ovarium', 'Ovarikiri')
    ovarikanan_id = fields.Many2one('master.temuan.ovarium', 'Ovarikanan')
    cervix_id = fields.Many2one('master.temuan.cervix', 'Cervix')
    perk_siklus = fields.Char('Perkiraan Siklus')
    tps_id = fields.Many2one('tps.liter', 'TPS', related='id_sapi.tps_id', store=True)
    bcs = fields.Float('Body Condition Score', required=True)
    periode_id = fields.Many2one('periode.setoran', 'Periode')
    is_permohonan = fields.Boolean('Is Permohonan')


    @api.model
    def create(self, vals):
        res = super(form_pr, self).create(vals)
        kunjungan = self.env['form.kunjungan.gdfp'].search([('peternak_id', '=', res.peternak_id.id),('petugas_id', '=', res.petugas_id.id),
                                                            ('periode_id', '=', res.periode_id.id),('jenis_management', '=', '6')], limit=1)
        if not kunjungan:
            bcs = res.bcs
            vals = {
                'peternak_id'       : res.peternak_id.id,
                'petugas_id'        : res.petugas_id.id,
                'periode_id'        : res.periode_id.id,
                'jenis_management'  : '6',
                'total_bcs'         : res.bcs
            }
            rec= self.env['form.kunjungan.gdfp'].create(vals)
            vals = {
                        'kunjungan_gdfp_id'     : rec.id,
                        'nama_form'             : 'Form Palpasi Raktal',
                        'bcs'                   : bcs
                    }
            self.env['history.form.line'].create(vals)
            count = len(rec.history_line)
            rec.write({'body_cond'  : bcs/count})
            rec._onchange_body_cond()
            rec._onchange_angka_morbi()

        else :
            vals = {
                        'kunjungan_gdfp_id'     : kunjungan.id,
                        'nama_form'             : 'Form Palpasi Rektal',
                        'bcs'                   : res.bcs
                    }
            self.env['history.form.line'].create(vals)
            count = len(kunjungan.history_line)
            bcs = (kunjungan.total_bcs + res.bcs)
            vals = {
                'total_bcs'       : bcs,
                'body_cond'       : bcs/count
            }
            kunjungan.write(vals)

            kunjungan._onchange_body_cond()
            kunjungan._onchange_angka_morbi()


    
        return res

    @api.onchange('petugas_id')
    def _onchange_petugas_id(self):
        if self.petugas_id:
            self.jabatan_id = self.petugas_id.jabatan_id.id

    @api.onchange('peternak_id')
    def _onchange_peternak_id(self):
        if self.peternak_id:
            self.wilayah_id = self.peternak_id.wilayah_id.id

    @api.onchange('tgl_layanan')
    def _onchange_tgl_layanan(self):
        if self.tgl_layanan:
            periode_setoran_obj = self.env['periode.setoran']
            periode_setoran = periode_setoran_obj.search([
                ('periode_setoran_awal', '<=', self.tgl_layanan),
                ('periode_setoran_akhir', '>=', self.tgl_layanan)
            ])
            if periode_setoran:
                self.periode_id = periode_setoran.id
            else:
                # Jika tidak ada periode yang sesuai, Anda dapat menangani kasus ini sesuai kebutuhan Anda.
                # Misalnya, memberikan default atau memberikan pesan kesalahan.
                self.periode_id = False

class form_pt(models.Model):
    _name = 'form.pt'
    _rec_name = 'eartag_id'

    peternak_id = fields.Many2one('peternak.sapi', 'Anggota/Peternak')
    id_pemilik = fields.Char('ID Pemilik', related='peternak_id.kode_peternak')
    wilayah_id = fields.Many2one('master.wilayah', 'Wilayah')
    kelompok_id = fields.Many2one('peternak.group', related='peternak_id.kelompok_id')
    petugas_id = fields.Many2one('medical.physician', 'Petugas')
    jabatan_id = fields.Many2one('master.jabatan', ' Jabatan', readonly=False)
    id_sapi = fields.Many2one('sapi', 'Nama Sapi', domain="[('peternak_id', '=', peternak_id)]")
    eartag_id = fields.Char('ID Eartag Sapi')
    tgl_layanan = fields.Date('Tanggal Layanan')
    cat_petugas = fields.Text('Catatan Petugas')
    tps_id = fields.Many2one('tps.liter', 'TPS', related='id_sapi.tps_id', store=True)
    bcs = fields.Float('Body Condition Score', required=True)
    periode_id = fields.Many2one('periode.setoran', 'Periode')
    is_permohonan = fields.Boolean('Is Permohonan')


    @api.model
    def create(self, vals):
        res = super(form_pt, self).create(vals)
        kunjungan = self.env['form.kunjungan.gdfp'].search([('peternak_id', '=', res.peternak_id.id),('petugas_id', '=', res.petugas_id.id),
                                                            ('periode_id', '=', res.periode_id.id),('jenis_management', '=', '6')], limit=1)
        if not kunjungan:
            bcs = res.bcs
            vals = {
                'peternak_id'       : res.peternak_id.id,
                'petugas_id'        : res.petugas_id.id,
                'periode_id'        : res.periode_id.id,
                'jenis_management'  : '6',
                'total_bcs'         : res.bcs
            }
            rec= self.env['form.kunjungan.gdfp'].create(vals)
            vals = {
                        'kunjungan_gdfp_id'     : rec.id,
                        'nama_form'             : 'Form Potong Tanduk',
                        'bcs'                   : bcs
                    }
            self.env['history.form.line'].create(vals)
            count = len(rec.history_line)
            rec.write({'body_cond'  : bcs/count})
            rec._onchange_body_cond()
            rec._onchange_angka_morbi()

        else :
            vals = {
                        'kunjungan_gdfp_id'     : kunjungan.id,
                        'nama_form'             : 'Form Potong Tanduk',
                        'bcs'                   : res.bcs
                    }
            self.env['history.form.line'].create(vals)
            count = len(kunjungan.history_line)
            bcs = (kunjungan.total_bcs + res.bcs)
            vals = {
                'total_bcs'       : bcs,
                'body_cond'       : bcs/count
            }
            kunjungan.write(vals)

            kunjungan._onchange_body_cond()
            kunjungan._onchange_angka_morbi()


    
        return res

    @api.onchange('petugas_id')
    def _onchange_petugas_id(self):
        if self.petugas_id:
            self.jabatan_id = self.petugas_id.jabatan_id.id

    @api.onchange('peternak_id')
    def _onchange_peternak_id(self):
        if self.peternak_id:
            self.wilayah_id = self.peternak_id.wilayah_id.id

    @api.onchange('tgl_layanan')
    def _onchange_tgl_layanan(self):
        if self.tgl_layanan:
            periode_setoran_obj = self.env['periode.setoran']
            periode_setoran = periode_setoran_obj.search([
                ('periode_setoran_awal', '<=', self.tgl_layanan),
                ('periode_setoran_akhir', '>=', self.tgl_layanan)
            ])
            if periode_setoran:
                self.periode_id = periode_setoran.id
            else:
                # Jika tidak ada periode yang sesuai, Anda dapat menangani kasus ini sesuai kebutuhan Anda.
                # Misalnya, memberikan default atau memberikan pesan kesalahan.
                self.periode_id = False

class form_sq(models.Model):
    _name = 'form.sq'
    _inherit = 'image.mixin'
    _rec_name = 'eartag_id'

    petugas_id = fields.Many2one('medical.physician', 'Petugas')
    jabatan_id = fields.Many2one('master.jabatan', ' Jabatan', readonly=False)
    peternak_id = fields.Many2one('peternak.sapi', 'Anggota/Peternak')
    id_pemilik = fields.Char('ID Pemilik', related='peternak_id.kode_peternak')
    wilayah_id = fields.Many2one('master.wilayah', 'Wilayah')
    id_sapi = fields.Many2one('sapi', 'Sapi', domain="[('peternak_id', '=', peternak_id)]")
    eartag_id = fields.Char('ID Eartag Sapi')
    tgl_layanan = fields.Date('Tanggal Layanan')
    cat_petugas = fields.Text('Catatan Petugas')
    met_pengh_jss_id = fields.Many2one('master.metode.perhitungan.jss', 'Metode Penghitungan JSS')
    knn_dpn_jss = fields.Integer('Kanan Depan JSS')
    kanan_dpn_kuman_id = fields.Many2one('master.kuman.sampel.kuartir', 'Kanan Depan Kuman')
    knn_blkg_jss = fields.Integer('Kanan Belakang JSS')
    knn_blkg_kuman_id = fields.Many2one('master.kuman.sampel.kuartir', 'Kanan Belakang Kuman')
    kiri_dpn_jss = fields.Integer('Kiri Depan JSS')
    kiri_dpn_kuman_id = fields.Many2one('master.kuman.sampel.kuartir', 'Kiri Depan Kuman')
    kiri_blkg_jss = fields.Integer('Kiri Belakang JSS')
    kiri_blkg_kuman_id = fields.Many2one('master.kuman.sampel.kuartir', 'Kiri Belakang Kuman')
    biaya = fields.Boolean('Biaya')
    tps_id = fields.Many2one('tps.liter', 'TPS', related='id_sapi.tps_id', store=True)
    bcs = fields.Float('Body Condition Score', required=True)
    periode_id = fields.Many2one('periode.setoran', 'Periode')
    is_permohonan = fields.Boolean('Is Permohonan')


    @api.model
    def create(self, vals):
        res = super(form_sq, self).create(vals)
        kunjungan = self.env['form.kunjungan.gdfp'].search([('peternak_id', '=', res.peternak_id.id),('petugas_id', '=', res.petugas_id.id),
                                                            ('periode_id', '=', res.periode_id.id),('jenis_management', '=', '6')], limit=1)
        if not kunjungan:
            bcs = res.bcs
            vals = {
                'peternak_id'       : res.peternak_id.id,
                'petugas_id'        : res.petugas_id.id,
                'periode_id'        : res.periode_id.id,
                'jenis_management'  : '6',
                'total_bcs'         : res.bcs
            }
            rec= self.env['form.kunjungan.gdfp'].create(vals)
            vals = {
                        'kunjungan_gdfp_id'     : rec.id,
                        'nama_form'             : 'Form Sampel Quartir',
                        'bcs'                   : bcs
                    }
            self.env['history.form.line'].create(vals)
            count = len(rec.history_line)
            rec.write({'body_cond'  : bcs/count})
            rec._onchange_body_cond()
            rec._onchange_angka_morbi()

        else :
            vals = {
                        'kunjungan_gdfp_id'     : kunjungan.id,
                        'nama_form'             : 'Form Sampel Quartir',
                        'bcs'                   : res.bcs
                    }
            self.env['history.form.line'].create(vals)
            count = len(kunjungan.history_line)
            bcs = (kunjungan.total_bcs + res.bcs)
            vals = {
                'total_bcs'       : bcs,
                'body_cond'       : bcs/count
            }
            kunjungan.write(vals)

            kunjungan._onchange_body_cond()
            kunjungan._onchange_angka_morbi()


    
        return res

    @api.onchange('petugas_id')
    def _onchange_petugas_id(self):
        if self.petugas_id:
            self.jabatan_id = self.petugas_id.jabatan_id.id

    @api.onchange('peternak_id')
    def _onchange_peternak_id(self):
        if self.peternak_id:
            self.wilayah_id = self.peternak_id.wilayah_id.id

    @api.onchange('tgl_layanan')
    def _onchange_tgl_layanan(self):
        if self.tgl_layanan:
            periode_setoran_obj = self.env['periode.setoran']
            periode_setoran = periode_setoran_obj.search([
                ('periode_setoran_awal', '<=', self.tgl_layanan),
                ('periode_setoran_akhir', '>=', self.tgl_layanan)
            ])
            if periode_setoran:
                self.periode_id = periode_setoran.id
            else:
                # Jika tidak ada periode yang sesuai, Anda dapat menangani kasus ini sesuai kebutuhan Anda.
                # Misalnya, memberikan default atau memberikan pesan kesalahan.
                self.periode_id = False

class form_specimen(models.Model):
    _name = 'form.specimen'
    _inherit = 'image.mixin'
    _rec_name = 'eartag_id'

    peternak_id = fields.Many2one('peternak.sapi', 'Anggota/Peternak')
    kelompok_id = fields.Many2one('peternak.group', related='peternak_id.kelompok_id')
    id_pemilik = fields.Char('ID Pemilik', related='peternak_id.kode_peternak')
    wilayah_id = fields.Many2one('master.wilayah', 'Wilayah')
    petugas_id = fields.Many2one('medical.physician', 'Petugas')
    jabatan_id = fields.Many2one('master.jabatan', ' Jabatan', readonly=False)
    id_sapi = fields.Many2one('sapi', 'Nama Sapi', domain="[('peternak_id', '=', peternak_id)]")
    eartag_id = fields.Char('ID Eartag Sapi')
    tgl_layanan = fields.Date('Tanggal Layanan')
    cat_petugas = fields.Text('Catatan Petugas')
    specimen_tes_id = fields.Many2one('master.specimen.tes', 'Specimen Tes')
    jns_specimen_id = fields.Many2one('master.specimen', 'Jenis Specimen')
    no_sample = fields.Char('No Sample')
    tps_id = fields.Many2one('tps.liter', 'TPS', related='id_sapi.tps_id', store=True)
    bcs = fields.Float('Body Condition Score', required=True)
    periode_id = fields.Many2one('periode.setoran', 'Periode')
    is_permohonan = fields.Boolean('Is Permohonan')


    @api.model
    def create(self, vals):
        res = super(form_specimen, self).create(vals)
        kunjungan = self.env['form.kunjungan.gdfp'].search([('peternak_id', '=', res.peternak_id.id),('petugas_id', '=', res.petugas_id.id),
                                                            ('periode_id', '=', res.periode_id.id),('jenis_management', '=', '6')], limit=1)
        if not kunjungan:
            bcs = res.bcs
            vals = {
                'peternak_id'       : res.peternak_id.id,
                'petugas_id'        : res.petugas_id.id,
                'periode_id'        : res.periode_id.id,
                'jenis_management'  : '6',
                'total_bcs'         : res.bcs
            }
            rec= self.env['form.kunjungan.gdfp'].create(vals)
            vals = {
                        'kunjungan_gdfp_id'     : rec.id,
                        'nama_form'             : 'Form Specimen',
                        'bcs'                   : bcs
                    }
            self.env['history.form.line'].create(vals)
            count = len(rec.history_line)
            rec.write({'body_cond'  : bcs/count})
            rec._onchange_body_cond()
            rec._onchange_angka_morbi()

        else :
            vals = {
                        'kunjungan_gdfp_id'     : kunjungan.id,
                        'nama_form'             : 'Form Specimen',
                        'bcs'                   : res.bcs
                    }
            self.env['history.form.line'].create(vals)
            count = len(kunjungan.history_line)
            bcs = (kunjungan.total_bcs + res.bcs)
            vals = {
                'total_bcs'       : bcs,
                'body_cond'       : bcs/count
            }
            kunjungan.write(vals)

            kunjungan._onchange_body_cond()
            kunjungan._onchange_angka_morbi()


    
        return res

    @api.onchange('petugas_id')
    def _onchange_petugas_id(self):
        if self.petugas_id:
            self.jabatan_id = self.petugas_id.jabatan_id.id

    @api.onchange('peternak_id')
    def _onchange_peternak_id(self):
        if self.peternak_id:
            self.wilayah_id = self.peternak_id.wilayah_id.id

    @api.onchange('tgl_layanan')
    def _onchange_tgl_layanan(self):
        if self.tgl_layanan:
            periode_setoran_obj = self.env['periode.setoran']
            periode_setoran = periode_setoran_obj.search([
                ('periode_setoran_awal', '<=', self.tgl_layanan),
                ('periode_setoran_akhir', '>=', self.tgl_layanan)
            ])
            if periode_setoran:
                self.periode_id = periode_setoran.id
            else:
                # Jika tidak ada periode yang sesuai, Anda dapat menangani kasus ini sesuai kebutuhan Anda.
                # Misalnya, memberikan default atau memberikan pesan kesalahan.
                self.periode_id = False

class form_peng_bb_tb(models.Model):
    _name = 'form.peng.bb.tb'
    _inherit = 'image.mixin'
    # _rec_name = 'eartag_id'
    #
    # petugas_id = fields.Many2one('medical.physician', 'Petugas')
    # jabatan_id = fields.Many2one('master.jabatan', ' Jabatan', readonly=False)
    # peternak_id = fields.Many2one('peternak.sapi', 'Anggota/Peternak')
    # id_pemilik = fields.Char('ID Pemilik')
    # id_sapi = fields.Many2one('sapi', 'Sapi')
    # eartag_id = fields.Char('ID Eartag Sapi')
    # tgl_layanan = fields.Datetime('Tanggal Layanan')
    # cat_petugas = fields.Text('Catatan Petugas')
    # nkt = fields.Integer('NKT')
    # brt_bdn = fields.Char('Berat Badan')
    # tinggi_gumba = fields.Char('Tinggi Gumba')
    # tps_id = fields.Many2one('tps.liter', 'TPS', related='id_sapi.tps_id', store=True)
    # bcs = fields.Float('Body Condition Score')

class form_ganti_pmlk(models.Model):
    _name = 'form.ganti.pmlk'
    _inherit = 'image.mixin'
    _rec_name = 'eartag_id'

    petugas_id = fields.Many2one('medical.physician', 'Petugas')
    jabatan_id = fields.Many2one('master.jabatan', ' Jabatan', readonly=False)
    id_sapi = fields.Many2one('sapi', 'Sapi')
    eartag_id = fields.Char('ID Eartag Sapi')
    kode_peternak_baru = fields.Char('Kode Peternak')
    peternak_lama_id = fields.Many2one('peternak.sapi', 'Peternak ID Lama', related='id_sapi.peternak_id')
    peternak_baru_id = fields.Many2one('peternak.sapi', 'Peternak ID Baru')
    tgl_layanan = fields.Date('Tanggal Layanan')
    keterangan = fields.Text('Keterangan')
    tps_id = fields.Many2one('tps.liter', 'TPS', related='id_sapi.tps_id', store=True)
    bcs = fields.Float('Body Condition Score', required=True)
    periode_id = fields.Many2one('periode.setoran', 'Periode')
    is_permohonan = fields.Boolean('Is Permohonan')


    @api.model
    def create(self, vals):
        res = super(form_ganti_pmlk, self).create(vals)
        kunjungan = self.env['form.kunjungan.gdfp'].search([('peternak_id', '=', res.peternak_baru_id.id),('petugas_id', '=', res.petugas_id.id),
                                                            ('periode_id', '=', res.periode_id.id),('jenis_management', '=', '6')], limit=1)
        if not kunjungan:
            bcs = res.bcs
            vals = {
                'peternak_id'       : res.peternak_baru_id.id,
                'petugas_id'        : res.petugas_id.id,
                'periode_id'        : res.periode_id.id,
                'jenis_management'  : '6',
                'total_bcs'         : res.bcs
            }
            rec= self.env['form.kunjungan.gdfp'].create(vals)
            vals = {
                        'kunjungan_gdfp_id'     : rec.id,
                        'nama_form'             : 'Form Ganti Pemilik',
                        'bcs'                   : bcs
                    }
            self.env['history.form.line'].create(vals)
            count = len(rec.history_line)
            rec.write({'body_cond'  : bcs/count})
            rec._onchange_body_cond()
            rec._onchange_angka_morbi()

        else :
            vals = {
                        'kunjungan_gdfp_id'     : kunjungan.id,
                        'nama_form'             : 'Form Ganti Pemilik',
                        'bcs'                   : res.bcs
                    }
            self.env['history.form.line'].create(vals)
            count = len(kunjungan.history_line)
            bcs = (kunjungan.total_bcs + res.bcs)
            vals = {
                'total_bcs'       : bcs,
                'body_cond'       : bcs/count
            }
            kunjungan.write(vals)

            kunjungan._onchange_body_cond()
            kunjungan._onchange_angka_morbi()


    
        return res

    @api.onchange('petugas_id')
    def _onchange_petugas_id(self):
        if self.petugas_id:
            self.jabatan_id = self.petugas_id.jabatan_id.id

    # @api.onchange('peternak_baru_id')
    # def _onchange_peternak_id(self):
    #     if self.peternak_baru_id:
    #         self.wilayah_id = self.peternak_baru_id.wilayah_id.id

    @api.onchange('tgl_layanan')
    def _onchange_tgl_layanan(self):
        if self.tgl_layanan:
            periode_setoran_obj = self.env['periode.setoran']
            periode_setoran = periode_setoran_obj.search([
                ('periode_setoran_awal', '<=', self.tgl_layanan),
                ('periode_setoran_akhir', '>=', self.tgl_layanan)
            ])
            if periode_setoran:
                self.periode_id = periode_setoran.id
            else:
                # Jika tidak ada periode yang sesuai, Anda dapat menangani kasus ini sesuai kebutuhan Anda.
                # Misalnya, memberikan default atau memberikan pesan kesalahan.
                self.periode_id = False

class form_vaksinasi(models.Model):
    _name = 'form.vaksinasi'
    _rec_name = 'eartag_id'

    petugas_id = fields.Many2one('medical.physician', 'Petugas')
    jabatan_id = fields.Many2one('master.jabatan', ' Jabatan', readonly=False)
    peternak_id = fields.Many2one('peternak.sapi', 'Anggota/Peternak')
    id_pemilik = fields.Char('ID Pemilik', related='peternak_id.kode_peternak')
    wilayah_id = fields.Many2one('master.wilayah', 'Wilayah')
    id_sapi = fields.Many2one('sapi', 'Sapi', domain="[('peternak_id', '=', peternak_id)]")
    eartag_id = fields.Char('ID Eartag Sapi')
    tgl_layanan = fields.Date('Tanggal Layanan')
    jns_vaksin = fields.Many2one('master.vaksin', 'Jenis Vaksin')
    dosis = fields.Char('Dosis')
    biaya = fields.Float('Biaya')
    # nama_vaksin = fields.Char('Nama Vaksin')
    cat_petugas = fields.Text('Catatan Petugas')
    # image = fields.Binary(string='Image')
    tps_id = fields.Many2one('tps.liter', 'TPS', related='id_sapi.tps_id', store=True)
    bcs = fields.Float('Body Condition Score', required=True)
    periode_id = fields.Many2one('periode.setoran', 'Periode')
    is_permohonan = fields.Boolean('Is Permohonan')


    @api.model
    def create(self, vals):
        res = super(form_vaksinasi, self).create(vals)
        kunjungan = self.env['form.kunjungan.gdfp'].search([('peternak_id', '=', res.peternak_id.id),('petugas_id', '=', res.petugas_id.id),
                                                            ('periode_id', '=', res.periode_id.id),('jenis_management', '=', '6')], limit=1)
        if not kunjungan:
            bcs = res.bcs
            vals = {
                'peternak_id'       : res.peternak_id.id,
                'petugas_id'        : res.petugas_id.id,
                'periode_id'        : res.periode_id.id,
                'jenis_management'  : '6',
                'total_bcs'         : res.bcs
            }
            rec= self.env['form.kunjungan.gdfp'].create(vals)
            vals = {
                        'kunjungan_gdfp_id'     : rec.id,
                        'nama_form'             : 'Form Vaksinasi',
                        'bcs'                   : bcs
                    }
            self.env['history.form.line'].create(vals)
            count = len(rec.history_line)
            rec.write({'body_cond'  : bcs/count})
            rec._onchange_body_cond()
            rec._onchange_angka_morbi()

        else :
            vals = {
                        'kunjungan_gdfp_id'     : kunjungan.id,
                        'nama_form'             : 'Form Vaksinasi',
                        'bcs'                   : res.bcs
                    }
            self.env['history.form.line'].create(vals)
            count = len(kunjungan.history_line)
            bcs = (kunjungan.total_bcs + res.bcs)
            vals = {
                'total_bcs'       : bcs,
                'body_cond'       : bcs/count
            }
            kunjungan.write(vals)

            kunjungan._onchange_body_cond()
            kunjungan._onchange_angka_morbi()


    
        return res

    @api.onchange('petugas_id')
    def _onchange_petugas_id(self):
        if self.petugas_id:
            self.jabatan_id = self.petugas_id.jabatan_id.id

    @api.onchange('peternak_id')
    def _onchange_peternak_id(self):
        if self.peternak_id:
            self.wilayah_id = self.peternak_id.wilayah_id.id

    @api.onchange('tgl_layanan')
    def _onchange_tgl_layanan(self):
        if self.tgl_layanan:
            periode_setoran_obj = self.env['periode.setoran']
            periode_setoran = periode_setoran_obj.search([
                ('periode_setoran_awal', '<=', self.tgl_layanan),
                ('periode_setoran_akhir', '>=', self.tgl_layanan)
            ])
            if periode_setoran:
                self.periode_id = periode_setoran.id
            else:
                # Jika tidak ada periode yang sesuai, Anda dapat menangani kasus ini sesuai kebutuhan Anda.
                # Misalnya, memberikan default atau memberikan pesan kesalahan.
                self.periode_id = False

class form_susu(models.Model):
    _name = 'form.susu'
    _inherit = 'image.mixin'
    _rec_name = 'eartag_id'

    petugas_id = fields.Many2one('medical.physician', 'Petugas')
    jabatan_id = fields.Many2one('master.jabatan', ' Jabatan', readonly=False)
    peternak_id = fields.Many2one('peternak.sapi', 'Anggota/Peternak')
    id_pemilik = fields.Char('ID Pemilik')
    eartag_id = fields.Char('ID Eartag Sapi')
    tgl_layanan = fields.Date('Tanggal Layanan')
    cat_petugas = fields.Text('Catatan Petugas')
    no_sample = fields.Integer('No Sample')
    susu_pgi = fields.Char('Susu Pagi')
    susu_sre = fields.Char('Susu Sore')
    fat_pgi = fields.Char('Fat Pagi')
    fat_sre = fields.Char('Fat Sore')
    prot_pgi = fields.Char('Protein Pagi')
    prot_sre = fields.Char('Protein Sore')
    jml_susu = fields.Char('Jumlah Susu')
    fat = fields.Float('%Fat')
    protein = fields.Float('%Protein')


class form_pot_kuku(models.Model):
    _name = 'form.pot.kuku'
    _inherit = 'image.mixin'
    _rec_name = 'eartag_id'

    layanan_id = fields.Many2one('jenis.pelayanan', 'Jenis Layanan')
    petugas_id = fields.Many2one('medical.physician', 'Petugas')
    jabatan_id = fields.Many2one('master.jabatan', ' Jabatan', readonly=False)
    peternak_id = fields.Many2one('peternak.sapi', 'Anggota/Peternak')
    id_pemilik = fields.Char('ID Pemilik', related='peternak_id.kode_peternak')
    wilayah_id = fields.Many2one('master.wilayah', 'Wilayah')
    id_sapi = fields.Many2one('sapi', 'Sapi', domain="[('peternak_id', '=', peternak_id)]")
    eartag_id = fields.Char('ID Eartag Sapi')
    tgl_layanan = fields.Date('Tanggal Layanan')
    alsn_ptg_kku_id = fields.Many2one('master.alasan.potkuku', 'Alasan Potong Kuku')
    dpn_kiri = fields.Char('Depan Kiri')
    dpn_kanan = fields.Char('Depan Kanan')
    blkg_kiri = fields.Char('Belakang Kiri')
    blkg_kanan = fields.Char('Belakang Kanan')
    pngbtn_lain_1_id = fields.Many2one('master.obat', 'Pengobatan Lain 1')
    pngbtn_lain_2_id = fields.Many2one('master.obat', 'Pengobatan Lain 2')
    cat_petugas = fields.Text('Catatan Petugas')
    tps_id = fields.Many2one('tps.liter', 'TPS', related='id_sapi.tps_id', store=True)
    bcs = fields.Float('Body Condition Score', required=True)
    periode_id = fields.Many2one('periode.setoran', 'Periode')
    is_permohonan = fields.Boolean('Is Permohonan')


    @api.model
    def create(self, vals):
        res = super(form_pot_kuku, self).create(vals)
        kunjungan = self.env['form.kunjungan.gdfp'].search([('peternak_id', '=', res.peternak_id.id),('petugas_id', '=', res.petugas_id.id),
                                                            ('periode_id', '=', res.periode_id.id),('jenis_management', '=', '6')], limit=1)
        if not kunjungan:
            bcs = res.bcs
            vals = {
                'peternak_id'       : res.peternak_id.id,
                'petugas_id'        : res.petugas_id.id,
                'periode_id'        : res.periode_id.id,
                'jenis_management'  : '6',
                'total_bcs'         : res.bcs
            }
            rec= self.env['form.kunjungan.gdfp'].create(vals)
            vals = {
                        'kunjungan_gdfp_id'     : rec.id,
                        'nama_form'             : 'Form Potong Kuku',
                        'bcs'                   : bcs
                    }
            self.env['history.form.line'].create(vals)
            count = len(rec.history_line)
            rec.write({'body_cond'  : bcs/count})
            rec._onchange_body_cond()
            rec._onchange_angka_morbi()

        else :
            vals = {
                        'kunjungan_gdfp_id'     : kunjungan.id,
                        'nama_form'             : 'Form Potong Kuku',
                        'bcs'                   : res.bcs
                    }
            self.env['history.form.line'].create(vals)
            count = len(kunjungan.history_line)
            bcs = (kunjungan.total_bcs + res.bcs)
            vals = {
                'total_bcs'       : bcs,
                'body_cond'       : bcs/count
            }
            kunjungan.write(vals)

            kunjungan._onchange_body_cond()
            kunjungan._onchange_angka_morbi()


    
        return res

    @api.onchange('petugas_id')
    def _onchange_petugas_id(self):
        if self.petugas_id:
            self.jabatan_id = self.petugas_id.jabatan_id.id

    @api.onchange('peternak_id')
    def _onchange_peternak_id(self):
        if self.peternak_id:
            self.wilayah_id = self.peternak_id.wilayah_id.id

    @api.onchange('tgl_layanan')
    def _onchange_tgl_layanan(self):
        if self.tgl_layanan:
            periode_setoran_obj = self.env['periode.setoran']
            periode_setoran = periode_setoran_obj.search([
                ('periode_setoran_awal', '<=', self.tgl_layanan),
                ('periode_setoran_akhir', '>=', self.tgl_layanan)
            ])
            if periode_setoran:
                self.periode_id = periode_setoran.id
            else:
                # Jika tidak ada periode yang sesuai, Anda dapat menangani kasus ini sesuai kebutuhan Anda.
                # Misalnya, memberikan default atau memberikan pesan kesalahan.
                self.periode_id = False

class form_ident(models.Model):
    _name = 'form.ident'
    _inherit = 'image.mixin'
    _rec_name = 'id_sapi'

    id_sapi = fields.Many2one('sapi', 'Sapi')
    petugas_id = fields.Many2one('medical.physician', 'Petugas')
    jabatan_id = fields.Many2one('master.jabatan', ' Jabatan', readonly=False)
    peternak_id = fields.Many2one('peternak.sapi', 'Anggota/Peternak')
    wilayah_id = fields.Many2one('master.wilayah', 'Wilayah')
    id_pemilik = fields.Char('ID Pemilik', related='peternak_id.kode_peternak')
    tgl_layanan = fields.Date('Tanggal Layanan')
    eartag_id = fields.Char('ID Eartag Sapi')
    # metoda_id = fields.Many2one('master.metoda', 'Metode Perolehan')
    tipe_id = fields.Many2one('master.tipe.sapi', 'Tipe Sapi')
    # id_status_reproduksi = fields.Many2one('master.status.reproduksi', 'Status Reproduksi')
    state = fields.Selection([
        ('tdk_ada', 'Tidak Ada'),
        ('kering', 'Kering'),
        ('laktasi', 'Laktasi'),
    ], string='Status Sapi', readonly=False, required=False)
    # kembar = fields.Selection([
    #     ('y', 'Ya'),
    #     ('t', 'Tidak')
    # ], string='Kembar')
    status_aktif = fields.Selection([
        ('a', 'Aktif'),
        ('ta', 'Tidak Aktif'),
    ], "Status Aktif")
    lak_ke = fields.Integer('Laktasi Ke')
    tgl_perubahan_status = fields.Date('Tanggal Perubahan Status')
    tps_id = fields.Many2one('tps.liter', 'TPS', related='id_sapi.tps_id', store=True)
    bcs = fields.Float('Body Condition Score', required=True)
    periode_id = fields.Many2one('periode.setoran', 'Periode')
    cat_petugas = fields.Text('Catatan Petugas')
    is_permohonan = fields.Boolean('Is Permohonan')
    # status_kesehatan_id = fields.Many2one('master.status.kesehatan', 'Status Kesehatan')
    # status_lahir = fields.Selection([
    #     ('h', 'Hidup'),
    #     ('m', 'Mati')
    # ], string='Status Lahir')

    @api.onchange('petugas_id')
    def _onchange_petugas_id(self):
        if self.petugas_id:
            self.jabatan_id = self.petugas_id.jabatan_id.id

    @api.onchange('peternak_id')
    def _onchange_peternak_id(self):
        if self.peternak_id:
            self.wilayah_id = self.peternak_id.wilayah_id.id

    @api.onchange('tgl_layanan')
    def _onchange_tgl_layanan(self):
        if self.tgl_layanan:
            periode_setoran_obj = self.env['periode.setoran']
            periode_setoran = periode_setoran_obj.search([
                ('periode_setoran_awal', '<=', self.tgl_layanan),
                ('periode_setoran_akhir', '>=', self.tgl_layanan)
            ])
            if periode_setoran:
                self.periode_id = periode_setoran.id
            else:
                # Jika tidak ada periode yang sesuai, Anda dapat menangani kasus ini sesuai kebutuhan Anda.
                # Misalnya, memberikan default atau memberikan pesan kesalahan.
                self.periode_id = False

    @api.model
    def create(self, values):
        record = super(form_ident, self).create(values)

        if record.id_sapi:
            sapi_record = record.id_sapi

            # Periksa dan perbarui nilai-nilai yang diisi
            update_values = {}
            if record.tipe_id:
                update_values['tipe_id'] = record.tipe_id.id
            # if record.id_status_reproduksi:
            #     update_values['id_status_reproduksi'] = record.id_status_reproduksi.id
            if record.state:
                update_values['state'] = record.state
            if record.status_aktif:
                update_values['status_aktif'] = record.status_aktif
            # if record.status_kesehatan_id:
            #     update_values['status_kesehatan_id'] = record.status_kesehatan_id.id
            # if record.status_lahir:
            #     update_values['status_lahir'] = record.status_lahir
            # if record.kembar:
            #     update_values['kembar'] = record.kembar
            # if record.metoda_id:
            #     update_values['metoda_id'] = record.metoda_id.id
            if record.tgl_perubahan_status:
                update_values['tgl_perubahan_status'] = record.tgl_perubahan_status

            # Perbarui objek sapi hanya jika ada nilai yang diisi
            if update_values:
                sapi_record.write(update_values)

        return record

class form_pengobatan(models.Model):
    _name = 'form.pengobatan'
    _rec_name = 'petugas_id'

    peternak_id = fields.Many2one('peternak.sapi', 'Anggota/Peternak')
    id_pemilik = fields.Char('ID Pemilik', related='peternak_id.kode_peternak')
    wilayah_id = fields.Many2one('master.wilayah', 'Wilayah')
    petugas_id = fields.Many2one('medical.physician', 'Petugas')
    jabatan_id = fields.Many2one('master.jabatan', ' Jabatan', readonly=False)
    tgl_layanan = fields.Date('Tanggal Layanan')
    id_sapi = fields.Many2one('sapi', 'Nama Sapi', domain="[('peternak_id', '=', peternak_id)]")
    tps_id = fields.Many2one('tps.liter', 'TPS', related='id_sapi.tps_id', store=True)
    bcs = fields.Float('Body Condition Score', required=True)
    eartag_id = fields.Char('ID Eartag Sapi')
    id_kasus_penyakit = fields.Many2one('master.kasus.penyakit', 'Kasus Penyakit')
    status_kesehatan_id = fields.Many2one('master.status.kesehatan', 'Status Kesehatan')
    cat_petugas = fields.Text('Catatan Petugas')
    metoda_pengobatan_id = fields.Many2one('master.metoda.pengobatan', 'Metoda Pengobatan 1')
    obat1 = fields.Many2one('master.obat', 'Obat 1', required=True)
    dose1 = fields.Integer('Dosis')
    metoda_pengobatan_id2 = fields.Many2one('master.metoda.pengobatan', 'Metoda Pengobatan 2')
    obat2 = fields.Many2one('master.obat', 'Obat 2')
    dose2 = fields.Integer('Dosis')
    metoda_pengobatan_id3 = fields.Many2one('master.metoda.pengobatan', 'Metoda Pengobatan 3')
    obat3 = fields.Many2one('master.obat', 'Obat 3')
    dose3 = fields.Integer('Dosis')
    metoda_pengobatan_id4 = fields.Many2one('master.metoda.pengobatan', 'Metoda Pengobatan 4')
    obat4 = fields.Many2one('master.obat', 'Obat 4')
    dose4 = fields.Integer('Dosis')
    metoda_pengobatan_id5 = fields.Many2one('master.metoda.pengobatan', 'Metoda Pengobatan 5')
    obat5 = fields.Many2one('master.obat', 'Obat 5')
    dose5 = fields.Integer('Dosis')
    periode_id = fields.Many2one('periode.setoran', 'Periode')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('close', 'Closed')
    ], string='Status', default='draft', readonly=True, tracking=True)
    permohonan_id = fields.Many2one('medical.appointment', 'Permohonan')
    is_permohonan = fields.Boolean('Is Permohonan')

    def submit(self):
        self.write({'state': 'close'})


    @api.model
    def create(self, vals):
        res = super(form_pengobatan, self).create(vals)
        kunjungan = self.env['form.kunjungan.gdfp'].search([('peternak_id', '=', res.peternak_id.id),('petugas_id', '=', res.petugas_id.id),
                                                            ('periode_id', '=', res.periode_id.id),('jenis_management', '=', '6')], limit=1)
        if not kunjungan:
            bcs = res.bcs
            vals = {
                'peternak_id'       : res.peternak_id.id,
                'petugas_id'        : res.petugas_id.id,
                'periode_id'        : res.periode_id.id,
                'jenis_management'  : '6',
                'total_bcs'         : res.bcs
            }
            rec= self.env['form.kunjungan.gdfp'].create(vals)
            vals = {
                        'kunjungan_gdfp_id'     : rec.id,
                        'nama_form'             : 'Form Pengobatan',
                        'bcs'                   : bcs
                    }
            self.env['history.form.line'].create(vals)
            count = len(rec.history_line)
            rec.write({'body_cond'  : bcs/count})
            if res.id_kasus_penyakit and res.id_kasus_penyakit.perbedaan_penyakit == 'l' and res.status_kesehatan_id.kode == 2:
                vals = {
                        'kunjungan_gdfp_id'     : rec.id,
                        'sapi_id'               : res.id_sapi.id,
                        'kasus_penyakit_id'     : res.id_kasus_penyakit.id,
                        'perbedaan_penyakit'    : res.id_kasus_penyakit.perbedaan_penyakit,
                        'bcs'                   : bcs
                    }
                self.env['sapi.gdfp.line'].create(vals)
                rec.write({'angka_morbi'  : res.bcs})
            rec._onchange_body_cond()
            rec._onchange_angka_morbi()

        else :
            vals = {
                        'kunjungan_gdfp_id'     : kunjungan.id,
                        'nama_form'             : 'Form Pengobatan',
                        'bcs'                   : res.bcs
                    }
            self.env['history.form.line'].create(vals)
            count = len(kunjungan.history_line)
            bcs = (kunjungan.total_bcs + res.bcs)
            vals = {
                'total_bcs'       : bcs,
                'body_cond'       : bcs/count
            }
            kunjungan.write(vals)

            if res.id_kasus_penyakit and res.id_kasus_penyakit.perbedaan_penyakit == 'l' and res.status_kesehatan_id.kode == 2:
                if kunjungan.sapi_gdfp_line :
                    for line in kunjungan.sapi_gdfp_line :
                        if line.sapi_id.id != res.id_sapi.id :
                            vals = {
                                    'kunjungan_gdfp_id'     : kunjungan.id,
                                    'sapi_id'               : res.id_sapi.id,
                                    'kasus_penyakit_id'     : res.id_kasus_penyakit.id,
                                    'perbedaan_penyakit'    : res.id_kasus_penyakit.perbedaan_penyakit,
                                    'bcs'                   : res.bcs
                                }
                            self.env['sapi.gdfp.line'].create(vals)
                    total = sum(record.bcs for record in kunjungan.sapi_gdfp_line)
                    count = len(kunjungan.sapi_gdfp_line)
                    kunjungan.write({'angka_morbi'  : total/count})
                else :
                    vals = {
                        'kunjungan_gdfp_id'     : kunjungan.id,
                        'sapi_id'               : res.id_sapi.id,
                        'kasus_penyakit_id'     : res.id_kasus_penyakit.id,
                        'perbedaan_penyakit'    : res.id_kasus_penyakit.perbedaan_penyakit,
                        'bcs'                   : res.bcs
                    }
                self.env['sapi.gdfp.line'].create(vals)
                kunjungan.write({'angka_morbi'  : res.bcs})


            kunjungan._onchange_body_cond()
            kunjungan._onchange_angka_morbi()


    
        return res

    @api.onchange('petugas_id')
    def _onchange_petugas_id(self):
        if self.petugas_id:
            self.jabatan_id = self.petugas_id.jabatan_id.id

    @api.onchange('peternak_id')
    def _onchange_peternak_id(self):
        if self.peternak_id:
            self.wilayah_id = self.peternak_id.wilayah_id.id

    @api.onchange('status_kesehatan_id')
    def _onchange_status_kesehatan_id(self):
        # Pastikan id_status_reproduksi di objek sapi diisi sesuai dengan form_ib
        if self.id_sapi:
            self.id_sapi.status_kesehatan_id = self.status_kesehatan_id

    @api.onchange('tgl_layanan')
    def _onchange_tgl_layanan(self):
        if self.tgl_layanan:
            periode_setoran_obj = self.env['periode.setoran']
            periode_setoran = periode_setoran_obj.search([
                ('periode_setoran_awal', '<=', self.tgl_layanan),
                ('periode_setoran_akhir', '>=', self.tgl_layanan)
            ])
            if periode_setoran:
                self.periode_id = periode_setoran.id
            else:
                # Jika tidak ada periode yang sesuai, Anda dapat menangani kasus ini sesuai kebutuhan Anda.
                # Misalnya, memberikan default atau memberikan pesan kesalahan.
                self.periode_id = False