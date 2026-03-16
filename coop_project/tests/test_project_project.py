from odoo.fields import Command
from odoo.tests.common import TransactionCase


class TestProjectProject(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Project = cls.env["project.project"]
        cls.ProjectTag = cls.env["project.tags"]

    def test_get_kanban_categories_returns_color_code(self):
        tag = self.ProjectTag.create({"name": "Tag A", "color": 1})
        project = self.Project.create(
            {"name": "Project A", "tag_ids": [Command.set([tag.id])]}
        )

        res = project.get_kanban_categories()
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]["id"], tag.id)
        self.assertEqual(res[0]["name"], "Tag A")
        self.assertTrue(isinstance(res[0]["color"], str))
        self.assertTrue(res[0]["color"].startswith("#"))

    def test_get_kanban_categories_color_changes_with_index(self):
        tag_0 = self.ProjectTag.create({"name": "Tag 0", "color": 0})
        tag_1 = self.ProjectTag.create({"name": "Tag 1", "color": 1})
        project = self.Project.create(
            {
                "name": "Project B",
                "tag_ids": [Command.set([tag_0.id, tag_1.id])],
            }
        )

        res = project.get_kanban_categories()
        colors = {item["id"]: item["color"] for item in res}
        self.assertNotEqual(colors[tag_0.id], colors[tag_1.id])
