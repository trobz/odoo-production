from odoo.fields import Command
from odoo.tests.common import TransactionCase


class TestProjectProject(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Project = cls.env["project.project"]
        cls.ProjectCategory = cls.env["project.category"]

    def test_get_kanban_categories_returns_color_code(self):
        categ = self.ProjectCategory.create({"name": "Categ A", "color": 1})
        project = self.Project.create(
            {"name": "Project A", "project_categ_ids": [Command.set([categ.id])]}
        )

        res = project.get_kanban_categories()
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]["id"], categ.id)
        self.assertEqual(res[0]["name"], "Categ A")
        self.assertEqual(res[0]["color"], categ.color_code)
        self.assertTrue(res[0]["color"].startswith("#"))

    def test_get_kanban_categories_color_changes_with_index(self):
        categ_0 = self.ProjectCategory.create({"name": "Categ 0", "color": 0})
        categ_1 = self.ProjectCategory.create({"name": "Categ 1", "color": 1})
        project = self.Project.create(
            {
                "name": "Project B",
                "project_categ_ids": [Command.set([categ_0.id, categ_1.id])],
            }
        )

        res = project.get_kanban_categories()
        colors = {item["id"]: item["color"] for item in res}
        self.assertNotEqual(colors[categ_0.id], colors[categ_1.id])
