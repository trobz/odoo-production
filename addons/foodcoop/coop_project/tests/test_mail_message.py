from odoo.tests.common import TransactionCase
from odoo.tools import html2plaintext


class TestMailMessage(TransactionCase):
    def test_task_description_without_tracking_is_body(self):
        task = self.env["project.task"].create({"name": "Task for message"})
        msg = self.env["mail.message"].create(
            {
                "body": "Body only",
                "message_type": "comment",
                "model": "project.task",
                "res_id": task.id,
            }
        )
        msg._compute_task_description()
        self.assertEqual(html2plaintext(msg.task_description).strip(), "Body only")
