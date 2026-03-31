from datetime import datetime

from odoo.tests import common


class TestGrossMarginXlsx(common.TransactionCase):
    """Base class - Test Gross Margin XLSX Report."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Wizard = cls.env["gross.margin.xlsx.wizard"]
        cls.Category = cls.env["product.category"]
        cls.Product = cls.env["product.product"]

        cls.category = cls.Category.create(
            {
                "name": "Test Category",
            }
        )
        cls.product = cls.Product.create(
            {
                "name": "Test Product",
                "type": "consu",
                "categ_id": cls.category.id,
                "list_price": 100.0,
                "standard_price": 60.0,
            }
        )

    def test_wizard_creation(self):
        wizard = self.Wizard.create(
            {
                "from_date": datetime(2024, 1, 1, 0, 0, 0),
                "to_date": datetime(2024, 12, 31, 23, 59, 59),
                "category_ids": [self.category.id],
            }
        )
        self.assertEqual(wizard.from_date, datetime(2024, 1, 1, 0, 0, 0))
        self.assertEqual(wizard.to_date, datetime(2024, 12, 31, 23, 59, 59))
        self.assertIn(self.category, wizard.category_ids)

    def test_get_datas(self):
        wizard = self.Wizard.create(
            {
                "from_date": datetime(2024, 1, 1, 0, 0, 0),
                "to_date": datetime(2024, 12, 31, 23, 59, 59),
                "category_ids": [self.category.id],
            }
        )
        datas = wizard.get_datas()
        self.assertIsInstance(datas, list)
        self.assertEqual(len(datas), 1)
        self.assertEqual(datas[0]["category"], self.category.name)

    def test_get_datas_empty_category(self):
        empty_category = self.Category.create(
            {
                "name": "Empty Category",
            }
        )
        wizard = self.Wizard.create(
            {
                "from_date": datetime(2024, 1, 1, 0, 0, 0),
                "to_date": datetime(2024, 12, 31, 23, 59, 59),
                "category_ids": [empty_category.id],
            }
        )
        datas = wizard.get_datas()
        self.assertIsInstance(datas, list)
        self.assertEqual(len(datas), 1)
        self.assertEqual(datas[0]["pre_tax_net_sales"], 0.0)
        self.assertEqual(datas[0]["gross_margin"], 0.0)

    def test_export_report(self):
        wizard = self.Wizard.create(
            {
                "from_date": datetime(2024, 1, 1, 0, 0, 0),
                "to_date": datetime(2024, 12, 31, 23, 59, 59),
                "category_ids": [self.category.id],
            }
        )
        result = wizard.export_report()
        self.assertIn("type", result)
        self.assertEqual(result["type"], "ir.actions.report")
        self.assertIn("report_name", result)
        self.assertEqual(result["report_name"], "report_gross_margin_xlsx")
