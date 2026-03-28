# -*- coding: utf-8 -*-
# from odoo import http


# class AsaCustomKanjabung(http.Controller):
#     @http.route('/asa_custom_kanjabung/asa_custom_kanjabung/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/asa_custom_kanjabung/asa_custom_kanjabung/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('asa_custom_kanjabung.listing', {
#             'root': '/asa_custom_kanjabung/asa_custom_kanjabung',
#             'objects': http.request.env['asa_custom_kanjabung.asa_custom_kanjabung'].search([]),
#         })

#     @http.route('/asa_custom_kanjabung/asa_custom_kanjabung/objects/<model("asa_custom_kanjabung.asa_custom_kanjabung"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('asa_custom_kanjabung.object', {
#             'object': obj
#         })
