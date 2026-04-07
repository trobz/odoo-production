from odoo.tests import common


class TestAccountExportConfig(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.config = cls.env["account.export.config"].create(
            {
                "name": "Test Config",
                "is_default": True,
            }
        )

    def test_account_export_config_default_field_ids(self):
        self.assertTrue(self.config.field_ids)
        expected_fields = [
            "export_code",
            "move_line_date",
            "move_number",
            "export_account_code",
            "account_move_name",
            "amount",
        ]
        field_types = [f.field_type for f in self.config.field_ids]
        for expected in expected_fields:
            self.assertIn(expected, field_types)

    def test_account_export_config_get_columns_dict(self):
        columns = self.config._get_columns_dict()
        self.assertIn("export_code", columns)
        self.assertIn("move_line_date", columns)
        self.assertIn("move_number", columns)
        self.assertIn("export_account_code", columns)
        self.assertIn("account_move_name", columns)
        self.assertIn("amount", columns)
        self.assertIn("debit", columns)
        self.assertIn("credit", columns)

    def test_account_export_config_is_default(self):
        config2 = self.env["account.export.config"].create(
            {
                "name": "Test Config 2",
                "is_default": False,
            }
        )
        self.assertTrue(self.config.is_default)
        self.assertFalse(config2.is_default)
