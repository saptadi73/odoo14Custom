# -*- coding: utf-8 -*-
from odoo import http

# class AsaAnalyticPayment(http.Controller):
#     @http.route('/asa_analytic_payment/asa_analytic_payment/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/asa_analytic_payment/asa_analytic_payment/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('asa_analytic_payment.listing', {
#             'root': '/asa_analytic_payment/asa_analytic_payment',
#             'objects': http.request.env['asa_analytic_payment.asa_analytic_payment'].search([]),
#         })

#     @http.route('/asa_analytic_payment/asa_analytic_payment/objects/<model("asa_analytic_payment.asa_analytic_payment"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('asa_analytic_payment.object', {
#             'object': obj
#         })