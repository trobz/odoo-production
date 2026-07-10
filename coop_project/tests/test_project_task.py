from odoo import Command, fields
from odoo.tests.common import TransactionCase


class TestProjectTask(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Project = cls.env["project.project"]
        cls.Task = cls.env["project.task"]
        cls.CalendarEvent = cls.env["calendar.event"]
        cls.Users = cls.env["res.users"]

        cls.project = cls.Project.create({"name": "Test Project"})
        cls.user_1 = cls.Users.create(
            {
                "name": "User 1",
                "login": "user1_coop_project_test",
                "email": "user1@example.com",
                "groups_id": [Command.set([cls.env.ref("base.group_user").id])],
            }
        )
        cls.user_2 = cls.Users.create(
            {
                "name": "User 2",
                "login": "user2_coop_project_test",
                "email": "user2@example.com",
                "groups_id": [Command.set([cls.env.ref("base.group_user").id])],
            }
        )

    def test_sync_calendar_event_create_update_unlink(self):
        task = self.Task.create(
            {
                "name": "Task With Deadline",
                "project_id": self.project.id,
                "show_dealine_in_calendar": True,
                "date_deadline": fields.Date.today(),
                "user_ids": [Command.set([self.user_1.id])],
            }
        )
        self.assertTrue(task.calendar_event_id, "Calendar event should be created")
        self.assertTrue(task.calendar_event_id.from_task)
        self.assertEqual(task.calendar_event_id.name, task.name)

        task.write({"name": "Renamed"})
        self.assertEqual(task.calendar_event_id.name, "Renamed")

        event_id = task.calendar_event_id.id
        task.write({"show_dealine_in_calendar": False})
        self.assertFalse(task.calendar_event_id)
        self.assertFalse(self.CalendarEvent.browse(event_id).exists())

    def test_notify_assignee_adds_followers(self):
        task = self.Task.create(
            {
                "name": "Task Notify",
                "project_id": self.project.id,
                "user_ids": [Command.set([self.user_1.id, self.user_2.id])],
            }
        )
        follower_partners = task.message_partner_ids
        self.assertIn(self.user_1.partner_id, follower_partners)
        self.assertIn(self.user_2.partner_id, follower_partners)

    def test_compute_comment_ids_filters_subtype(self):
        task = self.Task.create(
            {
                "name": "Task Comments",
                "project_id": self.project.id,
            }
        )
        subtype = self.env.ref("coop_project.mt_task_comment")
        msg_comment = self.env["mail.message"].create(
            {
                "model": "project.task",
                "res_id": task.id,
                "body": "Hello",
                "message_type": "comment",
                "subtype_id": subtype.id,
            }
        )
        msg_note = self.env["mail.message"].create(
            {
                "model": "project.task",
                "res_id": task.id,
                "body": "Note",
                "message_type": "notification",
            }
        )

        task.write({"show_comment_type": "comment"})
        task._compute_comment_ids()
        self.assertIn(msg_comment, task.comment_ids)
        self.assertNotIn(msg_note, task.comment_ids)

        task.write({"show_comment_type": "all"})
        task._compute_comment_ids()
        self.assertIn(msg_comment, task.comment_ids)
        self.assertIn(msg_note, task.comment_ids)

    def test_project_categ_id_drives_name_and_color(self):
        categ = self.env["project.category"].create({"name": "Urgent", "color": 2})
        task = self.Task.create(
            {
                "name": "Task With Category",
                "project_id": self.project.id,
                "project_categ_id": categ.id,
            }
        )
        self.assertEqual(task.project_category_name, "Urgent")
        self.assertEqual(task.color, 2)
