# -*- coding: utf-8 -*-
# from odoo import http


# class GrtProjectTask(http.Controller):
#     @http.route('/grt_project_task/grt_project_task/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/grt_project_task/grt_project_task/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('grt_project_task.listing', {
#             'root': '/grt_project_task/grt_project_task',
#             'objects': http.request.env['grt_project_task.grt_project_task'].search([]),
#         })

#     @http.route('/grt_project_task/grt_project_task/objects/<model("grt_project_task.grt_project_task"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('grt_project_task.object', {
#             'object': obj
#         })
