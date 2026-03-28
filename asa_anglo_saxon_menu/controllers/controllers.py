# -*- coding: utf-8 -*-
# from odoo import http


# class AsaAngloSaxonMenu(http.Controller):
#     @http.route('/asa_anglo_saxon_menu/asa_anglo_saxon_menu/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/asa_anglo_saxon_menu/asa_anglo_saxon_menu/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('asa_anglo_saxon_menu.listing', {
#             'root': '/asa_anglo_saxon_menu/asa_anglo_saxon_menu',
#             'objects': http.request.env['asa_anglo_saxon_menu.asa_anglo_saxon_menu'].search([]),
#         })

#     @http.route('/asa_anglo_saxon_menu/asa_anglo_saxon_menu/objects/<model("asa_anglo_saxon_menu.asa_anglo_saxon_menu"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('asa_anglo_saxon_menu.object', {
#             'object': obj
#         })
