from datetime import timedelta
from odoo import api, fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    priority = fields.Selection([
        ('0', 'No Priority'),
        ('1', 'Low'),
        ('2', 'Normal'),
        ('3', 'High Priority'),
        ], default='2')

    show_dealine_in_calendar = fields.Boolean(
        string="Show deadline on common calendar")
    calendar_event_id = fields.Many2one(
        comodel_name="calendar.event"
    )
    create_user_id = fields.Many2one(
        comodel_name="res.users",
        string="Created By",
        required=True,
        default=lambda self: self.env.uid
    )
    user_id = fields.Many2one(default=False)
    comment_ids = fields.Many2many(
        'mail.message',
        compute="_compute_comment_ids"
    )
    show_comment_type = fields.Selection([
        ('comment', 'Comment Only'),
        ('all', 'All'),
    ], default="comment")
    estimated_cost = fields.Float()
    ticket_description = fields.Html()
    ticket_number = fields.Char()
    project_categ_ids = fields.Many2many(
        'project.category', string='Categories',
        related="project_id.project_categ_ids")
    project_categ_id = fields.Many2one(
        'project.category', string='Category')
    project_category_name = fields.Char(
        related='project_categ_id.name', store=True)
    color = fields.Integer(related="project_categ_id.color", store=True)

    @api.multi
    def _compute_comment_ids(self):
        for task in self:
            args = [
                ('model', '=', 'project.task'),
                ('res_id', '=', task.id),
                ('body', '!=', False),
            ]
            if self.show_comment_type == 'comment':
                args += [
                    ('message_type', '=', 'comment'),
                    ('subtype_id', '=',
                        self.env.ref('lalouve_custom.mt_task_comment').id)
                ]
            comment_ids = self.env['mail.message'].search(args)
            task.comment_ids = comment_ids

    @api.multi
    def sync_calendar_event(self):
        for task in self:
            if not (task.show_dealine_in_calendar and task.date_deadline):
                if task.calendar_event_id:
                    task.calendar_event_id.unlink()
                continue
            partner_ids = [task.create_user_id.partner_id.id]
            if task.user_id.partner_id.id not in partner_ids:
                partner_ids.append(task.user_id.partner_id.id)
            hours = int(self.env[
                'ir.config_parameter'].sudo().get_param(
                'project.task.calendar.hours', '10'
            ))
            start_date = fields.Date.to_string(task.date_deadline) + \
                ' {hours}:00:00'.format(
                    hours=hours
                )
            start_date = self.env['ir.fields.converter']._str_to_datetime(
                None, None, start_date)[0]
            start_date = fields.Datetime.from_string(start_date)
            end_date = start_date + timedelta(hours=1)
            vals = {
                'name': task.name,
                'description': task.description,
                'partner_ids': [(6, 0, partner_ids)],
                'start': start_date,
                'stop': end_date,
                'from_task': True,
                'duration': 1
            }
            event = task.calendar_event_id
            if not event:
                event = self.env['calendar.event'].create(vals)
                task.calendar_event_id = event
            else:
                event.write(vals)

    @api.multi
    def notify_assignee(self):
        for task in self:
            if not task.user_id:
                continue
            mail_template = self.env.ref('lalouve_custom.email_notify_assignee')
            if mail_template:
                mail_template.send_mail(task.id)

    @api.model
    def create(self, vals):
        task = super(ProjectTask, self.with_context(
            mail_auto_subscribe_no_notify=1)).create(vals)
        task.sync_calendar_event()
        task.notify_assignee()
        return task

    @api.multi
    def write(self, vals):
        res = super(ProjectTask, self.with_context(
            mail_auto_subscribe_no_notify=1)).write(vals)
        self.sync_calendar_event()
        if vals.get('user_id'):
            self.notify_assignee()
        return res

    @api.multi
    def unlink(self):
        events = self.mapped('calendar_event_id')
        res = super(ProjectTask, self).unlink()
        if events:
            events.unlink()
        return res

    @api.multi
    def btn_add_comment(self):
        self.ensure_one()
        view = self.env.ref('lalouve_custom.view_task_comment_form')
        act_vals = {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.message',
            'type': 'ir.actions.act_window',
            'target': 'new',
            "views": [(view.id, "form")],
            'view_id': view.id,
            'context': {
                'default_model': 'project.task',
                'default_res_id': self.id,
                'default_needaction_partner_ids':
                    [(6, 0, [self.user_id.partner_id.id, self.create_user_id.partner_id.id])],
                'default_author_id': self.env.user.partner_id.id,
                'default_message_type': 'comment',
                'default_subtype_id':
                    self.env.ref('lalouve_custom.mt_task_comment').id
            }
        }
        return act_vals

    @api.multi
    def btn_show_comment_only(self):
        self.ensure_one()
        self.sudo().write({'show_comment_type': 'comment'})

    @api.multi
    def btn_show_comment_history(self):
        self.ensure_one()
        self.sudo().write({'show_comment_type': 'all'})

