# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _

class jenis_pelayanan(models.Model):
    _name = 'jenis.pelayanan'
    _rec_name = 'pelayanan_id'

    pelayanan_id = fields.Char('Nama Pelayanan')
    code_pelayanan = fields.Char('Kode Pelayanan')
    info = fields.Text('Extra Info')