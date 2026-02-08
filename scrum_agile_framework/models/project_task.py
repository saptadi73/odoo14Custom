from odoo import models, fields, api
from odoo.exceptions import UserError
class projectTask(models.Model):
    _inherit = 'project.task'


    def write(self, values):

        # isadmin = self.env.uid
        # isasign = self.user_id.id

        # if isasign :
        #     if isadmin != isasign:
        #         raise UserError('Only User Assign can change the Staging, Please check it again!')

        if self.activity_ids:
               raise UserError('All Activity must be Done, Please check it again!')

        res = super(projectTask, self).write(values)
        return res


    # @api.depends('stage_id', 'kanban_state')
    # def _compute_kanban_state_label(self):
    #     for task in self:
    #         if task.kanban_state == 'normal':
    #             # isadmin = self.env.uid
    #             # isasign = self.user_id.id

    #             # if isasign :
    #             #     if isadmin != isasign:
    #             #         raise UserError('Only User Assign can change the Staging, Please check it again!')

    #             if self.activity_ids:
    #                 raise UserError('All Activity must be Done, Please check it again!')

    #             task.kanban_state_label = task.legend_normal
                
    #         elif task.kanban_state == 'blocked':
    #             task.kanban_state_label = task.legend_blocked
    #         else:
    #             task.kanban_state_label = task.legend_done
