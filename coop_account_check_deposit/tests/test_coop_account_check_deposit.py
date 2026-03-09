# Copyright (C) 2019-Today: La Louve (https://cooplalouve.fr)
# Copyright (C) 2019-Today: Druidoo (https://www.druidoo.io)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import Command
from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestUpdateCheckHolderName(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.company = cls.company_data["company"]
        cls.user.write(
            {
                "company_ids": [Command.link(cls.company.id)],
                "company_id": cls.company.id,
            }
        )
        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})

        cls.account_receivable = cls.company_data["default_account_receivable"]
        cls.account_revenue = cls.company_data["default_account_revenue"]

        cls.received_check_account = cls.env["account.account"].create(
            {
                "code": "5112ZZ",
                "name": "Received check - (test)",
                "reconcile": True,
                "account_type": "asset_current",
                "company_ids": [Command.set([cls.company.id])],
            }
        )

        cls.check_journal = cls.env["account.journal"].create(
            {
                "name": "Received check",
                "type": "bank",
                "code": "ZZCHK",
                "company_id": cls.company.id,
                "inbound_payment_method_line_ids": [
                    (
                        0,
                        0,
                        {
                            "payment_method_id": cls.env.ref(
                                "account.account_payment_method_manual_in"
                            ).id,
                            "payment_account_id": cls.received_check_account.id,
                        },
                    )
                ],
            }
        )

        cls.check_deposit = cls.env["account.check.deposit"].create(
            {
                "company_id": cls.company.id,
                "journal_id": cls.check_journal.id,
                "bank_journal_id": cls.company_data["default_journal_bank"].id,
                "currency_id": cls.company.currency_id.id,
            }
        )

    def _create_move_line(self, partner=None, check_deposit=None):
        line_vals = [
            Command.create(
                {
                    "quantity": 1,
                    "price_unit": 100,
                    "check_deposit_id": check_deposit.id if check_deposit else False,
                }
            )
        ]
        move = self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": partner.id if partner else False,
                "company_id": self.company.id,
                "invoice_line_ids": line_vals,
            }
        )
        move_line = move.line_ids.filtered(
            lambda line: line.check_deposit_id == check_deposit
        )
        return move_line

    def test_update_check_holder_name_with_deposit_and_partner(self):
        move_line = self._create_move_line(
            partner=self.partner,
            check_deposit=self.check_deposit,
        )

        self.assertEqual(move_line.check_holder_name, self.partner.display_name)

    def test_update_check_holder_name_without_deposit_clears_holder(self):
        move_line = self._create_move_line(
            partner=self.partner,
        )
        self.assertNotEqual(move_line.check_holder_name, "Test Partner")
