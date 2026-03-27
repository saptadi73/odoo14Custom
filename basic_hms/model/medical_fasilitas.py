# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _

class master_fasilitas(models.Model):
    _name = 'master.fasilitas'
    _rec_name = 'fasilitas_id'

    fasilitas_id = fields.Char('Nama')
    info = fields.Text('Extra Info')
