import logging

from odoo import models, fields, _

_logger = logging.getLogger(__name__)


class Project(models.Model):
    _inherit = 'project.project'

    kw_description = fields.Html(
        string='Custom description', )

    def kw_show_description(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Project of %s') % self.name,
            'domain': [('id', '=', self.id)],
            'res_model': 'project.project',
            'res_id':  self.id,
            'view_id': False,
            'view_mode': 'form',
        }
