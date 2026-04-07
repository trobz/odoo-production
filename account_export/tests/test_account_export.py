from datetime import date

from odoo import Command
from odoo.exceptions import ValidationError
from odoo.tests import common


class TestAccountExport(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        cls.company = cls.env.company
        cls.company2 = cls.env["res.company"].create(
            {
                "name": "Test Company 2",
            }
        )
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test Partner",
            }
        )
        cls.partner_property_account_receivable_software = cls.env[
            "account.account"
        ].create(
            {
                "name": "Test Receivable Software",
                "code": "411100",
                "account_type": "asset_receivable",
                "company_ids": [Command.set(cls.company.ids)],
            }
        )
        cls.partner_property_account_payable_software = cls.env[
            "account.account"
        ].create(
            {
                "name": "Test Payable Software",
                "code": "401100",
                "account_type": "liability_payable",
                "company_ids": [Command.set(cls.company.ids)],
            }
        )
        cls.partner.write(
            {
                "property_account_receivable_software": cls.partner_property_account_receivable_software.id,  # noqa: E501
                "property_account_payable_software": cls.partner_property_account_payable_software.id,  # noqa: E501
            }
        )

        cls.account_receivable = cls.env["account.account"].create(
            {
                "name": "Test Receivable",
                "code": "411000",
                "account_type": "asset_receivable",
                "company_ids": [Command.set(cls.company.ids)],
            }
        )
        cls.account_payable = cls.env["account.account"].create(
            {
                "name": "Test Payable",
                "code": "401000",
                "account_type": "liability_payable",
                "company_ids": [Command.set(cls.company.ids)],
            }
        )
        cls.account_revenue = cls.env["account.account"].create(
            {
                "name": "Test Revenue",
                "code": "701000",
                "account_type": "income",
                "company_ids": [Command.set(cls.company.ids)],
            }
        )
        cls.journal_sale = cls.env["account.journal"].create(
            {
                "name": "Test Sale Journal",
                "code": "TSJ",
                "type": "sale",
                "company_id": cls.company.id,
                "export_code": "VE",
            }
        )
        cls.journal_purchase = cls.env["account.journal"].create(
            {
                "name": "Test Purchase Journal",
                "code": "TPJ",
                "type": "purchase",
                "company_id": cls.company.id,
                "export_code": "AC",
            }
        )
        cls.journal2 = cls.env["account.journal"].create(
            {
                "name": "Test Journal 2",
                "code": "TJ2",
                "type": "sale",
                "company_id": cls.company2.id,
            }
        )
        cls.config = cls.env["account.export.config"].create(
            {
                "name": "Test Config",
                "is_default": True,
            }
        )

    def test_account_export_default_name(self):
        export = self.env["account.export"].create(
            {
                "config_id": self.config.id,
            }
        )
        expected_name = f"export{date.today().strftime('%y%m%d')}"
        self.assertEqual(export.name, expected_name)

    def test_account_export_default_config(self):
        export = self.env["account.export"].create(
            {
                "name": "Test Export",
                "config_id": self.config.id,
            }
        )
        self.assertEqual(export.config_id.id, self.config.id)

    def test_account_export_default_values(self):
        export = self.env["account.export"].create(
            {
                "name": "Test Export",
                "config_id": self.config.id,
            }
        )
        self.assertEqual(export.state, "draft")
        self.assertEqual(export.filter_move_lines, "non_exported")
        self.assertEqual(export.company_id.id, self.company.id)

    def test_account_export_multi_company_journal(self):
        with self.assertRaises(ValidationError):
            self.env["account.export"].create(
                {
                    "name": "Test Export",
                    "config_id": self.config.id,
                    "company_id": self.company.id,
                    "journal_ids": [(6, 0, [self.journal2.id])],
                }
            )

    def test_account_export_multi_company_invoice(self):
        move2 = self.env["account.move"].create(
            {
                "name": "Test Move 2",
                "move_type": "out_invoice",
                "partner_id": self.partner.id,
                "company_id": self.company2.id,
                "invoice_date": date.today(),
                "journal_id": self.journal2.id,
            }
        )
        with self.assertRaises(ValidationError):
            self.env["account.export"].create(
                {
                    "name": "Test Export",
                    "config_id": self.config.id,
                    "company_id": self.company.id,
                    "invoice_ids": [(6, 0, [move2.id])],
                }
            )
