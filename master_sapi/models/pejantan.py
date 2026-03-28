from odoo import api, fields, models, _

class pejantan(models.Model):
    _name = 'pejantan'
    _rec_name = 'pejantan_id'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    pejantan_id = fields.Char('Pejantan')
    kode_pejantan = fields.Char('No Pejantan')
    asal_id = fields.Char('Asal')
    tempat_lahir = fields.Char('Tempat Lahir')
    tgl_lahir = fields.Date('Tanggal Lahir')
    beli_dari = fields.Char('Beli Dari')
    kode_dam = fields.Char('ID Dam')
    dam_id = fields.Char('Dam')
    kode_sire = fields.Char('ID Sire')
    sire_id = fields.Char('Sire')
    asal_sire_id = fields.Char('Asal Sire')
    kode_mgs = fields.Char('IDMGS')
    mgs_id = fields.Char('MGS')
    kode_mgd = fields.Char('IDMGD')
    mgd_id = fields.Char('MGD')
    kode_ggs = fields.Char('IDMGD')
    ggs_id = fields.Char('MGD')
    image = fields.Binary('Photo')
    active = fields.Boolean('Aktif')
    pejantan_name = fields.Char('Nama Pejantan')

    # @api.onchange('pejantan_id')
    # def _onchange_pejantan_id(self):
    #     if self.pejantan_id:
    #         # Di sini, Anda dapat mengatur nilai kode_pejantan sesuai dengan logika yang Anda inginkan.
    #         # Sebagai contoh, saya akan mengatur kode_pejantan menjadi kode pejantan_id.
    #         self.kode_pejantan = self.pejantan_id.kode