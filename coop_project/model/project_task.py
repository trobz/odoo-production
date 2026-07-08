from datetime import timedelta

from odoo import Command, api, fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    priority = fields.Selection(
        selection_add=[
            ("2", "Normal"),
            ("3", "High Priority"),
        ],
        ondelete={"2": "set default", "3": "set default"},
    )

    show_dealine_in_calendar = fields.Boolean(string="Show deadline on common calendar")
    calendar_event_id = fields.Many2one(comodel_name="calendar.event")
    create_user_id = fields.Many2one(
        comodel_name="res.users",
        string="Created By",
        required=True,
        default=lambda self: self.env.uid,
    )
    user_ids = fields.Many2many(string="Assigned to", tracking=True)
    comment_ids = fields.Many2many("mail.message", compute="_compute_comment_ids")
    show_comment_type = fields.Selection(
        [
            ("comment", "Comment Only"),
            ("all", "All"),
        ],
        default="comment",
    )
    estimated_cost = fields.Float()
    ticket_description = fields.Html()
    ticket_number = fields.Char()
    project_categ_ids = fields.Many2many(
        "project.category",
        string="Categories",
        related="project_id.project_categ_ids",
    )
    project_categ_id = fields.Many2one("project.category", string="Category")
    project_category_name = fields.Char(related="project_categ_id.name", store=True)
    color = fields.Integer(related="project_categ_id.color", store=True)

    def _track_subtype(self, init_values):
        self.ensure_one()
        if "kanban_state_label" in init_values and self.kanban_state == "blocked":
            return self.env.ref("project.mt_task_blocked")
        elif "kanban_state_label" in init_values and self.kanban_state == "done":
            return self.env.ref("project.mt_task_ready")
        elif "stage_id" in init_values:
            if len(init_values.keys()) > 1:
                return self.env.ref("project.mt_task_new")
            else:
                return self.env.ref("project.mt_task_stage")
        return super()._track_subtype(init_values)

    def get_partner_assignee_ids(self):
        partner_ids = self.mapped("user_ids.partner_id.id")
        if not partner_ids:
            return ""
        res = ",".join(str(i) for i in partner_ids)
        return res

    def get_partner_assignee_names(self):
        partner_names = self.mapped("user_ids.partner_id.name")
        return ", ".join(partner_names)

    def get_lang(self):
        self.ensure_one()
        lang = False
        if self.user_ids and self.user_ids[0].lang:
            lang = self.user_ids[0].lang
        elif self.create_user_id and self.create_user_id.lang:
            lang = self.create_user_id.lang
        if not lang:
            lang = self.env.user.lang
        if not lang:
            lang = "en_US"
        return lang

    def _compute_comment_ids(self):
        for task in self:
            args = [
                ("model", "=", "project.task"),
                ("res_id", "=", task.id),
                ("body", "!=", False),
            ]
            if task.show_comment_type == "comment":
                args += [
                    ("message_type", "=", "comment"),
                    (
                        "subtype_id",
                        "=",
                        self.env.ref("coop_project.mt_task_comment").id,
                    ),
                ]
            comment_ids = self.env["mail.message"].search(args)
            task.comment_ids = comment_ids

    def sync_calendar_event(self):
        for task in self:
            if not (task.show_dealine_in_calendar and task.date_deadline):
                if task.calendar_event_id:
                    task.calendar_event_id.unlink()
                continue
            partner_ids = task.mapped("user_ids.partner_id.id")
            if task.create_user_id.partner_id.id not in partner_ids:
                partner_ids.append(task.create_user_id.partner_id.id)
            hours = int(
                self.env["ir.config_parameter"]
                .sudo()
                .get_param("project.task.calendar.hours", "10")
            )
            start_date = fields.Date.to_string(task.date_deadline) + f" {hours}:00:00"
            start_date = self.env["ir.fields.converter"]._str_to_datetime(
                None, None, start_date
            )[0]
            start_date = fields.Datetime.from_string(start_date)
            end_date = start_date + timedelta(hours=1)
            vals = {
                "name": task.name,
                "description": task.description,
                "partner_ids": [Command.set(partner_ids)],
                "start": start_date,
                "stop": end_date,
                "from_task": True,
                "duration": 1,
            }
            event = task.calendar_event_id
            if not event:
                event = self.env["calendar.event"].create(vals)
                task.calendar_event_id = event
            else:
                event.write(vals)

    def notify_assignee(self):
        for task in self:
            if not task.user_ids:
                continue
            # Add to followers
            message_partner_ids = task.message_partner_ids
            partners = task.mapped("user_ids.partner_id")
            to_add = partners - message_partner_ids
            if to_add:
                task.message_subscribe(partner_ids=to_add.ids)

            mail_template = self.env.ref("coop_project.email_notify_assignee")
            if mail_template:
                mail_template.send_mail(task.id)

    @api.model_create_multi
    def create(self, vals):
        task = super(
            ProjectTask, self.with_context(mail_auto_subscribe_no_notify=1)
        ).create(vals)
        task.sync_calendar_event()
        task.notify_assignee()
        return task

    def write(self, vals_list):
        res = super(
            ProjectTask, self.with_context(mail_auto_subscribe_no_notify=1)
        ).write(vals_list)
        self.sync_calendar_event()
        if vals_list.get("user_ids"):
            self.notify_assignee()
        return res

    def unlink(self):
        events = self.mapped("calendar_event_id")
        res = super().unlink()
        if events:
            events.unlink()
        return res

    def btn_add_comment(self):
        self.ensure_one()
        view = self.env.ref("coop_project.view_task_comment_form")
        partner_ids = self.mapped("user_ids.partner_id.id")
        if self.create_user_id.partner_id.id not in partner_ids:
            partner_ids.append(self.create_user_id.partner_id.id)
        act_vals = {
            "view_mode": "form",
            "res_model": "mail.message",
            "type": "ir.actions.act_window",
            "target": "new",
            "views": [(view.id, "form")],
            "view_id": view.id,
            "context": {
                "default_model": "project.task",
                "default_res_id": self.id,
                "default_partner_ids": [Command.set(partner_ids)],
                "default_author_id": self.env.user.partner_id.id,
                "default_message_type": "comment",
                "default_subtype_id": self.env.ref("coop_project.mt_task_comment").id,
            },
        }
        return act_vals

    def btn_show_comment_only(self):
        self.ensure_one()
        self.sudo().write({"show_comment_type": "comment"})

    def btn_show_comment_history(self):
        self.ensure_one()
        self.sudo().write({"show_comment_type": "all"})
