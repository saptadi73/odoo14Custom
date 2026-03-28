from odoo import api, fields, models, _

class UserType(models.Model):
    _inherit = 'res.users'

    # tipe_user = fields.Selection([
    #     ('siswa', 'Siswa'),
    #     ('ortu', 'Ortu'),
	# ('mgm', 'Management'),
    # ], string='Tipe User')
    # usermail = fields.Char('Email')
    tipe_user = fields.Selection([
        ('anggota', 'Anggota'),
        ('petugas', 'Petugas'),
        ('operator', 'Operator')
    ], string='Tipe Anggota')
    usermail = fields.Char('Email User')
    pass_default = fields.Boolean('Password Default')
    tps_ids = fields.Many2many(comodel_name='tps.liter', string='TPS')

