from odoo.tests import common


class TestAccountJournal(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.company = cls.env.company

    def test_account_journal_export_code(self):
        journal = self.env["account.journal"].create(
            {
                "name": "Test Journal",
                "code": "TJ",
                "type": "sale",
                "company_id": self.company.id,
                "export_code": "TEST",
            }
        )
        self.assertEqual(journal.export_code, "TEST")

    def test_account_journal_group_fields(self):
        field_date = self.env.ref("account.field_account_move_line__date")
        journal = self.env["account.journal"].create(
            {
                "name": "Test Journal",
                "code": "TJ",
                "type": "sale",
                "company_id": self.company.id,
                "group_fields": [(6, 0, [field_date.id])],
            }
        )
        self.assertIn(field_date, journal.group_fields)
