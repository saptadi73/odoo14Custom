# -*- coding: utf-8 -*-
import json
from odoo import models, fields, api
from datetime import timedelta

class grt_project_task(models.Model):
    _inherit = 'project.task'
    _description = 'project task inherit'

    # @api.depends('project_id')
    # def _compute_stage_id(self):
    #     for task in self:
    #         if task.project_id:
    #             if task.project_id not in task.stage_id.project_ids:
    #                 task.stage_id = task.stage_find(task.project_id.id, [
    #                     ('fold', '=', False), ('is_closed', '=', False)])
    #         else:
    #             task.stage_id = False

    @api.onchange('planned_duration', 'date_start')
    def _inverse_planned_duration(self):
        for r in self:
            if r.date_start and r.planned_duration and not r.env.context.get('ignore_onchange_planned_duration', False):
                date_end_source = r.date_end
                r.date_end = r.date_start + timedelta(days=r.planned_duration)
                if r.depending_task_ids:
                    for r2 in r.depending_task_ids:
                        if r2.depending_task_id:
                            for r3 in r2.depending_task_id:
                                if r.date_end > r3.date_start:
                                    date_gap = r3.date_start - date_end_source
                                    source_planned_duration = r3.planned_duration
                                    r3.date_start = r.date_end + date_gap
                                    r3.planned_duration = source_planned_duration
