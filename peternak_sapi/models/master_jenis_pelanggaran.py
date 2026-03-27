from odoo import models, fields
class jenis_pelanggaran(models.Model):
    _name = "jenis.pelanggaran"
    _description = "Jenis Pelanggaran"
    _rec_name = 'jenis_pelanggaran'

    jenis_pelanggaran = fields.Char('Jenis Pelanggaran')
    keterangan = fields.Text('Keterangan')

# class jabatan_group(models.Model):
#     _name = "jabatan.group"
#     _rec_name = 'jabatan'
#     _description = "Jabatan Group"
#
#     jabatan = fields.Char('Nama Jabatan')
