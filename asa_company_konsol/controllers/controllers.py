# -*- coding: utf-8 -*-
# from odoo import http


# class AsaCompanyKonsol(http.Controller):
#     @http.route('/asa_company_konsol/asa_company_konsol/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/asa_company_konsol/asa_company_konsol/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('asa_company_konsol.listing', {
#             'root': '/asa_company_konsol/asa_company_konsol',
#             'objects': http.request.env['asa_company_konsol.asa_company_konsol'].search([]),
#         })

#     @http.route('/asa_company_konsol/asa_company_konsol/objects/<model("asa_company_konsol.asa_company_konsol"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('asa_company_konsol.object', {
#             'object': obj
#         })
