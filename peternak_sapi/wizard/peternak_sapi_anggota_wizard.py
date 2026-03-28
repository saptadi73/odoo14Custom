# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from datetime import date, datetime
from odoo.exceptions import ValidationError

# classes under  menus of laboratry

class peternak_sapi_anggota_create(models.TransientModel):
    _name = 'peternak.sapi.anggota.create'

    def create_peternak_sapi_anggota(self):
        res_ids = []
        anggota_rqu_obj = self.env['peternak.sapi']
        browse_records = anggota_rqu_obj.browse(self._context.get('active_ids'))
        result = {}
        for browse_record in browse_records:
            if self.env['simpin_syariah.member'].search([('email', '=', browse_record.email)]):
                raise ValidationError(_("The member with email %s already exists!") % browse_record.email)

            peternak_anggota_obj = self.env['simpin_syariah.member']
            # Find the corresponding peternak record based on the peternak_name string
            peternak = self.env['peternak.sapi'].search([('peternak_name', '=', browse_record.peternak_name)])
            if not peternak:
                # Handle the case where the peternak record is not found
                continue
            res = peternak_anggota_obj.create({'name': self.env['ir.sequence'].next_by_code('simpin_syariah.member'),
                                               'name': browse_record.peternak_name or False,
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
            # Mengubah status menjadi 'anggota'
            peternak.write({'state': 'anggota'})
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
                    'flags': {'form': {'action_buttons': False, 'options': {'mode': 'edit'}}},
                }

            if res_ids:
                result['domain'] = "[('id','=',%s)]" % res_ids

            return result

    # @api.models
    # def create(self, vals):
    #     anggota_count = self.env['simpin_syariah.member'].search_count([])
    #     if anggota_count > 0:
    #         raise ValidationError(_("Anda sudah membuat anggota sebelumnya. Tidak dapat membuat anggota lagi."))
    #     return super(peternak_sapi_anggota_create, self).create(vals)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
