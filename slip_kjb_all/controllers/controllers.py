# -*- coding: utf-8 -*-
from odoo import http

# class FitsPayrollMap(http.Controller):
#     @http.route('/fits_payroll_map/fits_payroll_map/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/fits_payroll_map/fits_payroll_map/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('fits_payroll_map.listing', {
#             'root': '/fits_payroll_map/fits_payroll_map',
#             'objects': http.request.env['fits_payroll_map.fits_payroll_map'].search([]),
#         })

#     @http.route('/fits_payroll_map/fits_payroll_map/objects/<model("fits_payroll_map.fits_payroll_map"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('fits_payroll_map.object', {
#             'object': obj
#         })