from odoo import models


class ProjectTask(models.Model):
    _name = 'project.task'
    _inherit = ['recurring.document', 'project.task']
