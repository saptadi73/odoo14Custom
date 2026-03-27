from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
from datetime import date,datetime

class sapi(models.Model):
    _name = "sapi"
    _description = "Sapi"
    _inherits = {"res.partner": "partner_id"}
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'first_name'

    @api.depends('date_of_birth')
    def onchange_age(self):
        for rec in self:
            if rec.date_of_birth:
                d1 = rec.date_of_birth
                d2 = datetime.today().date()
                rd = relativedelta(d2, d1)
                rec.age = str(rd.years) + "y" +" "+ str(rd.months) + "m" +" "+ str(rd.days) + "d"
            else:
                rec.age = "No Date Of Birth!!"

    partner_id = fields.Many2one('res.partner', 'Partner',
                                 required=True, ondelete="cascade")
    # patient_id = fields.Many2one('medical.patient')
    first_name = fields.Char('Name', size=128, translate=True)
    middle_name = fields.Char('Middle Name', size=128, translate=True)
    last_name = fields.Char('Last Name', size=128, translate=True)
    date_of_birth = fields.Date('Birth Date')
    blood_group = fields.Selection([
        ('A+', 'A+ve'),
        ('B+', 'B+ve'),
        ('O+', 'O+ve'),
        ('AB+', 'AB+ve'),
        ('A-', 'A-ve'),
        ('B-', 'B-ve'),
        ('O-', 'O-ve'),
        ('AB-', 'AB-ve')
    ], string='Blood Group')
    sex = fields.Selection([
        ('m', 'Male'),
        ('f', 'Female'),
        ('o', 'Other')
    ], 'Gender', required=True, default='m')
    id_number = fields.Char('ID Card Number', size=64)
    user_id = fields.Many2one('res.users', 'User', ondelete="cascade")
    category_id = fields.Many2one('op.category', 'Category')
    active = fields.Boolean(default=True)
    emergency_contact = fields.Many2one('res.partner', 'Emergency Contact')
    id_induk = fields.Many2one('sapi', 'Induk')
    id_ayah = fields.Many2one('sapi', 'Ayah')
    pejantan_id = fields.Many2one('pejantan', 'Pejantan')
    bobot = fields.Float( string='Bobot Kg')
    panjang = fields.Integer('Panjang cm')
    kondisi_sapi = fields.Char('Kondisi Sapi')
    jenis_sapi = fields.Many2one('jenis.sapi.master', 'Jenis Sapi')
    eartag_id = fields.Char('ID Ear Tag')
    jenis_id = fields.Char(related='jenis_sapi.id_jenis_sapi', string="ID Jenis Sapi")
    keterangan = fields.Text(related="jenis_sapi.keterangan", string="Keterangan")
    tgl_kematian = fields.Datetime('Tanggal Kematian')
    alasan = fields.Char('Alasan')
    sehat = fields.Boolean('Sehat')
    sakit = fields.Boolean('Sakit')
    hamil = fields.Boolean('Hamil')
    tdk_hamil = fields.Boolean('Tidak Hamil')
    state = fields.Selection([
        ('tdk_ada', 'Tidak Ada'),
        ('kering', 'Kering'),
        ('laktasi', 'Laktasi'),
    ], string='Status Sapi', readonly=False, required=False)
    ibu_titipan = fields.Char('Ibu Titipan')
    jenis_kehamilan = fields.Selection([
        ('tdk_ada', 'Tidak Ada'),
        ('ib', 'IB'),
        ('alami', 'Alami'),
    ], string='Jenis Kehamilan', required=False)
    height = fields.Integer('Tinggi cm')
    lgkr_perut = fields.Integer('Lingkar Perut cm')
    age = fields.Char(compute=onchange_age, string="Age", store=True)
    tipe_id = fields.Many2one('master.tipe.sapi', 'Tipe Sapi')
    posisi_eartag = fields.Selection([
        ('l', 'Kiri'),
        ('r', 'Kanan')
    ], string='Posisi Eartag')
    kembar = fields.Selection([
        ('y', 'Ya'),
        ('t', 'Tidak')
    ], string='Kembar')
    tgl_identifikasi = fields.Date('Tanggal Identifikasi')
    kode_kelahiran = fields.Char('Kode Kelahiran')
    breed_id = fields.Many2one('master.breed', 'Breed')
    status_aktif = fields.Selection([
        ('a', 'Aktif'),
        ('ta', 'Tidak Aktif')
    ], string='Status Aktif')
    status_lahir = fields.Selection([
        ('h', 'Hidup'),
        ('m', 'Mati')
    ], string='Status Lahir')
    id_status_reproduksi = fields.Many2one('master.status.reproduksi', 'Status Reproduksi')
    metoda_id = fields.Many2one('master.metoda', 'Metode Perolehan')
    stts_laktasi_id = fields.Many2one('master.status.laktasi', 'Status Laktasi')
    status_kesehatan_id = fields.Many2one('master.status.kesehatan', 'Status Kesehatan')
    ib_ke = fields.Integer('IB Ke')
    tgl_ib = fields.Datetime('Tanggal IB')
    tps_id = fields.Many2one('tps.liter', 'TPS')
    id_form_masuk = fields.Many2one('form.masuk', string='Form Masuk')
    is_rearing = fields.Boolean('Rearing')
    category_cip_id = fields.Many2one('type.cip', 'Category CIP')
    tgl_perubahan_status = fields.Date('Tanggal Perubahan Status', readonly=True)

    # def func_kering(self):
    #     if self.state == 'kering':
    #         self.state = 'laktasi'
    #
    # def func_laktasi(self):
    #     if self.state == 'laktasi':
    #         self.state = 'kering'

    _sql_constraints = [(
        'unique_gr_no',
        'unique(gr_no)',
        'GR Number must be unique per student!'
    )]

    @api.model
    def create(self, vals):
        # Extract the first_name from vals
        first_name = vals.get('first_name')

        # Create the partner record with a valid name
        partner = self.env['res.partner'].create({
            'name': first_name or '',  # Set name to first_name if available, otherwise an empty string
            'is_sapi': True,
            'company_type': 'person'
        })

        # Update partner_id in vals with the created partner's ID
        vals['partner_id'] = partner.id

        # Call the super method to complete the creation of the 'sapi' record
        return super(sapi, self).create(vals)

    @api.onchange('first_name', 'middle_name', 'last_name')
    def _onchange_name(self):
        if not self.middle_name:
            self.name = str(self.first_name) + " " + str(
                self.last_name
            )
        else:
            self.name = str(self.first_name) + " " + str(
                self.middle_name) + " " + str(self.last_name)

    @api.constrains('birth_date')
    def _check_birthdate(self):
        for record in self:
            if record.birth_date > fields.Date.today():
                raise ValidationError(_(
                    "Birth Date can't be greater than current date!"))

    def create_employee(self):
        for record in self:
            vals = {
                'name': record.name,
                'country_id': record.nationality.id,
                'sex': record.sex,
                'address_home_id': record.partner_id.id
            }
            emp_id = self.env['hr.employee'].create(vals)
            record.write({'emp_id': emp_id.id})
            record.partner_id.write({'partner_share': True, 'employee': True})

    list_formib_ids = fields.One2many('ib.line', 'master_sapi_id', 'IB', track_visibility='onchange')
    list_form_melahirkan_ids = fields.One2many('melahirkan.line', 'master_sapi_id', 'IB', track_visibility='onchange')

class IBLine(models.Model):
    _name = 'ib.line'
    _description = 'IB Line'

    master_sapi_id = fields.Many2one('sapi', 'Master Sapi Id')
    id_sapi = fields.Many2one('sapi', 'Sapi')
    ib_ke = fields.Integer('IB Ke')
    tgl = fields.Date('Tanggal')

class MelahirkanLine(models.Model):
    _name = 'melahirkan.line'
    _description = 'Melahirkan Line'

    master_sapi_id = fields.Many2one('sapi', 'Master Sapi Id')
    ibu_id = fields.Many2one('sapi', 'Sapi')
    # kode_eartag = fields.Char('Kode Eartag')
    # jenis_kelamin = fields.Selection([
    #     ('m', 'Male'), ('f', 'Female')
    # ], string="Jenis Kelamin")
    tgl = fields.Date('Tanggal')

