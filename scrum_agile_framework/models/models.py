from odoo import models, fields, api
from datetime import timedelta


class Project(models.Model):
    _inherit = 'project.project'

    user_story_count = fields.Integer(compute='_compute_user_story_count')
    sprint_count = fields.Integer(compute='_compute_sprint_count')
    last_sprint_id = fields.Many2one('scrum_agile_framework.sprint', compute='_get_last_sprint', store=True)

    # RELATIONAL MODELS
    sprint_ids = fields.One2many('scrum_agile_framework.sprint', 'project_id', string='Sprints')
    user_story_ids = fields.One2many('scrum_agile_framework.user_story', 'project_id', string='Product backlog')
    team_id = fields.Many2one('scrum_agile_framework.team', string='Scrum Team')
    meeting_ids = fields.One2many('scrum_agile_framework.meeting', 'project_id', string='Meeting')

    # METHODS
    def _compute_user_story_count(self):
        user_story_data = self.env['scrum_agile_framework.user_story'].read_group(
            [('project_id', 'in', self.ids)], ['project_id'], ['project_id'])
        result = dict((data['project_id'][0], data['project_id_count']) for data in user_story_data)
        for project in self:
            project.user_story_count = result.get(project.id, 0)

    def _compute_sprint_count(self):
        sprint_data = self.env['scrum_agile_framework.sprint'].read_group(
            [('project_id', 'in', self.ids)], ['project_id'], ['project_id'])
        result = dict((data['project_id'][0], data['project_id_count']) for data in sprint_data)
        for project in self:
            project.sprint_count = result.get(project.id, 0)

    @api.depends('sprint_ids.date_start')
    def _get_last_sprint(self):
        for project in self:
            if project.sprint_ids:
                last = project.sprint_ids.sorted(key='date_start')
                project.last_sprint_id = last[-1].id
            else:
                project.last_sprint_id = False


class Sprint(models.Model):
    _name = 'scrum_agile_framework.sprint'
    _description = 'Allows defining the sprints assigned to a project'
    _order = 'date_start'

    name = fields.Char(string='Sprint', required=True)
    date_start = fields.Date('Start date', required=True, default=fields.date.today())
    date_end = fields.Date(string='End date', required=True)
    speed = fields.Integer(string='Speed')
    goal = fields.Char(string='Goal')
    conclusions = fields.Text(string='Conclusions')
    task_count = fields.Integer(compute='_compute_task_count')
    retro_well = fields.Text(string='What went well?')
    retro_improvement = fields.Text(string='What went wrong?')
    retro_improvement_action = fields.Text(string="What should we do differently next time?")
    total_estimated_hours = fields.Integer(string='Total estimated hours', compute='_get_estimated_hours',
                                           store=True)

    # RELATIONAL MODELS
    project_id = fields.Many2one('project.project', string='Project', ondelete='cascade')
    user_story_ids = fields.One2many('scrum_agile_framework.user_story', 'sprint_id', string='User stories')
    task_ids = fields.One2many('project.task', 'sprint_id', string='Tasks')
    account_analytic_ids = fields.One2many('account.analytic.line', 'sprint_id', string='Timesheet')
    # account_analytic_ids = fields.One2many('account.analytic.line', 'ids', string='Timesheet')
    burn_down_chart_ids = fields.One2many('scrum_agile_framework.burn_down_chart', 'sprint_id', string='Burndown charts')

    # METHODS
    def action_view_tasks_scrum(self):
        action = self.with_context(active_id=self.id, active_ids=self.ids) \
            .env.ref('scrum_agile_framework.action_sprint_kanban_tasks') \
            .sudo().read()[0]
        action['display_name'] = self.name
        return action

    def action_view_burn_scrum(self):
        for burn_down_chart in self.burn_down_chart_ids:
            if not burn_down_chart.timesheet_id:
                burn_down_chart.unlink()
        for sprint in self:
            sprint.sudo()._create_burndown_chart_values()
        action = self.with_context(active_id=self.id, active_ids=self.ids) \
            .env.ref('scrum_agile_framework.action_sprint_burn') \
            .sudo().read()[0]
        action['display_name'] = self.name
        return action

    @api.depends('user_story_ids.planned_hours')
    def _get_estimated_hours(self):
        for sprint in self:
            sprint.total_estimated_hours = sum(user_story.planned_hours for user_story in sprint.user_story_ids)

    def _create_burndown_chart_values(self):
        self.ensure_one()
        vals_list = []
        work_hours_data = self._get_time_day(
            self.date_start,
            self.date_end,
        )
        for task in self.task_ids:
            if task.scrum_stage == 'todo':
                vals_list.append(
                    self._timesheet_task_prepare_line_values(self.date_start, task.planned_hours))
            else:
                for timesheet in task.timesheet_ids:
                    vals_list.append(
                        self._timesheet_task_prepare_line_values(timesheet.date, timesheet.remaining_amount))

        for index, (day_date, hours_day) in enumerate(work_hours_data):
            vals_list.append(self._timesheet_prepare_line_values(day_date, hours_day))
        self.env['scrum_agile_framework.burn_down_chart'].sudo().create(vals_list)

    def _timesheet_task_prepare_line_values(self, day_date, remaining_amount):
        self.ensure_one()
        return {
            'name': 'Remaining effort',
            'date': day_date,
            'hours_day': remaining_amount,
            'sprint_id': self.id,
        }

    def _timesheet_prepare_line_values(self, day_date, hours_day):
        self.ensure_one()
        return {
            'name': 'Expected effort',
            'date': day_date,
            'hours_day': hours_day,
            'sprint_id': self.id,
        }

    def _get_time_day(self, from_datetime, to_datetime):
        hours_sum = self.total_estimated_hours
        total_days = (to_datetime - from_datetime).days
        hours_day = round((hours_sum / total_days), 4)
        work_day_list = []
        for dt in self.daterange(from_datetime, to_datetime):
            work_day_list.append((dt, hours_sum))
            hours_sum = (hours_sum - hours_day)
        return work_day_list

    @staticmethod
    def daterange(date1, date2):
        for n in range(int((date2 - date1).days) + 1):
            yield date1 + timedelta(n)

    @api.model_create_multi
    def create(self, vals_list):
        sprints = super(Sprint, self).create(vals_list)
        for sprint in sprints:
            sprint.sudo()._create_burndown_chart_values()
        return sprints


class UserStory(models.Model):
    _name = 'scrum_agile_framework.user_story'
    _description = 'Allows you to manage the user stories of a project'
    _order = 'priority desc'

    name = fields.Char(string='Name', required=True)
    priority = fields.Integer(string='Priority', required=True)
    planned_hours = fields.Float('Planned hours', compute='_compute_planned_hours_sum')
    effective_hours = fields.Float('Effective hours', compute='_compute_effective_hours_sum')
    state = fields.Char('State')
    notes = fields.Char('Notes')
    editable = fields.Boolean('User story editable', compute='_user_story_editable', store=True)

    # RELATIONAL MODELS
    project_id = fields.Many2one('project.project', string='Project', compute='_get_project_id_from_sprint',
                                 store=True, ondelete='cascade')
    sprint_id = fields.Many2one('scrum_agile_framework.sprint', string='Sprint')
    task_ids = fields.One2many('project.task', 'user_story_id', string='Tasks')

    # METHODS
    @api.depends('task_ids.planned_hours')
    def _compute_planned_hours_sum(self):
        for user_story in self:
            user_story.planned_hours = sum(task.planned_hours for task in user_story.task_ids)

    @api.depends('task_ids.timesheet_ids.unit_amount')
    # @api.depends('task_ids')
    def _compute_effective_hours_sum(self):
        for user_story in self:
            user_story.effective_hours = sum(timesheet.unit_amount for task in user_story.task_ids for timesheet in task.timesheet_ids)

    @api.depends('sprint_id.project_id')
    def _get_project_id_from_sprint(self):
        for user_story in self:
            if user_story.sprint_id:
                user_story.project_id = user_story.sprint_id.project_id

    def action_view_tasks_hu_scrum(self):
        action = self.with_context(active_id=self.id, active_ids=self.ids) \
            .env.ref('scrum_agile_framework.action_hu_kanban_tasks') \
            .sudo().read()[0]
        action['display_name'] = self.name
        return action

    @api.depends('project_id.last_sprint_id')
    def _user_story_editable(self):
        for user_story in self:
            if user_story.sprint_id:
                if user_story.sprint_id == user_story.project_id.last_sprint_id:
                    user_story.editable = True
                else:
                    user_story.editable = False
            else:
                user_story.editable = True


class Task(models.Model):
    _inherit = 'project.task'

    scrum_stage = fields.Selection(string='Stage of the scrum task', selection=[(
        'todo', 'To Do'), ('doing', 'Doing'), ('done', 'Done')], default='todo', group_expand='_expand_groups')

    # RELATIONAL MODELS
    project_id = fields.Many2one('project.project', string='Project', compute='_get_project_id', store=True,
                                 ondelete='cascade')
    sprint_id = fields.Many2one('scrum_agile_framework.sprint', string='Sprint', compute='_get_sprint_id', store=True)
    user_story_id = fields.Many2one('scrum_agile_framework.user_story', string='User Story', ondelete='cascade')

    # METHODS
    @api.depends('user_story_id.sprint_id')
    def _get_sprint_id(self):
        for task in self:
            if task.user_story_id:
                task.sprint_id = task.user_story_id.sprint_id

    @api.depends('user_story_id.project_id')
    def _get_project_id(self):
        for task in self:
            if task.user_story_id:
                task.project_id = task.user_story_id.project_id

    @api.model
    def _expand_groups(self, states, domain, order):
        return ['todo', 'doing', 'done']


class Meeting(models.Model):
    _name = 'scrum_agile_framework.meeting'
    _description = 'Allows defining routine meetings of the Scrum Team'
    _order = 'date'

    date = fields.Date('Date', required=True)
    type = fields.Selection(string='Type', selection=[(
        'plan', 'Sprint Planning'), ('review', 'Sprint Review'), ('retrospective', 'Sprint Retrospective'),
        ('daily', 'Daily Scrum')], default='daily')
    duration = fields.Char('Duration', compute='_get_duration', store=True, help='Maximum meeting duration')

    # RELATIONAL MODELS
    project_id = fields.Many2one('project.project', string='Project', ondelete='cascade')
    team_id = fields.Many2one('scrum_agile_framework.team', string='Team', ondelete='cascade', compute='_get_team')

    # METHODS
    @api.depends('type')
    def _get_duration(self):
        meeting_duration = {'daily': '15 minutes', 'review': '2 hours',
                            'retrospective': '1 hour and a half', 'plan': '4 hours'}
        for meeting in self:
            meeting.duration = meeting_duration[f'{meeting.type}']

    @api.depends('project_id')
    def _get_team(self):
        for meeting in self:
            meeting.team_id = meeting.project_id.team_id

    def name_get(self):  # odoo's own function
        result = []
        for meeting in self:
            description = f' {meeting.type} meeting of the Project: {meeting.project_id.name} '
            result.append((meeting.id, description))
        return result


class Team(models.Model):
    _name = 'scrum_agile_framework.team'
    _description = 'Allows defining the members of the Scrum Team'

    name = fields.Char(string='Scrum Team name', required=True)

    # RELATIONAL MODELS
    project_ids = fields.One2many('project.project', 'team_id', string='Project')
    meeting_ids = fields.One2many('scrum_agile_framework.meeting', 'team_id', string='Meeting')
    employee_ids = fields.Many2many('hr.employee', string='Employee')


class Employee(models.Model):
    _inherit = 'hr.employee'

    role = fields.Selection(string='role', selection=[(
        'po', 'Product Owner'), ('sm', 'Scrum Manager'), ('dt', 'Development Team')], default='dt')

    responsibility = fields.Char(string='Responsibility')

    # RELATIONAL MODELS
    team_ids = fields.Many2many('scrum_agile_framework.team', string='Team')


class AccountAnalytic(models.Model):
    _inherit = 'account.analytic.line'

    remaining_amount = fields.Float(string='Remaining hours')

    # RELATIONAL MODELS
    sprint_id = fields.Many2one('scrum_agile_framework.sprint', string='Sprint', compute='_get_sprint_id', store=True,
                                ondelete='cascade')
    burn_down_chart_ids = fields.One2many('scrum_agile_framework.burn_down_chart', 'timesheet_id',
                                          string='Burndown chart values')

    # METHODS
    @api.constrains('date')
    def _date_unique(self):
        if self.sprint_id:
            date_counts = self.search_count([('date', '=', self.date), ('id', '!=', self.id)])
            if date_counts > 0:
                raise models.ValidationError('The date must be unique,'
                                             'if you want to add an input on this timesheet, modify the existing value.'
                                             )

    @api.depends('task_id.sprint_id')
    def _get_sprint_id(self):
        for line in self:
            if line.task_id.sprint_id:
                line.sprint_id = line.task_id.sprint_id


class BurnDownChart(models.Model):
    _name = 'scrum_agile_framework.burn_down_chart'
    _description = 'This class gets all the data from the timesheet to create the Burndown chart graph'

    name = fields.Char(string='Allows to distinguish between Remaining effort and Anticipated effort ')
    date = fields.Date(string='Date', required=True)
    hours_day = fields.Float(string='The number of hours per day', required=True)

    # RELATIONAL MODELS
    sprint_id = fields.Many2one('scrum_agile_framework.sprint', string='Sprint', ondelete='cascade')
    timesheet_id = fields.Many2one('account.analytic.line', string='Timesheet', ondelete='cascade')
