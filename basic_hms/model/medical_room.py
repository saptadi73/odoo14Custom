# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _

class master_room(models.Model):
    _name = 'master.room'
    _rec_name = 'room_id'

    room_id = fields.Char('Nama Ruangan')
    code_room = fields.Char('Kode Ruangan')
    fasilitas_ids = fields.Many2many('master.fasilitas', string='Fasilitas')
    info = fields.Text('Extra Info')
    class_room = fields.Selection([('c1', 'Class 1'), ('c2', 'Class 2'), ('c3', 'Class 3')], string="Kelas Ruangan")
