from odoo import Command

from .common import CoopAccountTestCommon


class CoopAccountTest(CoopAccountTestCommon):
    def test_coop_custom_account01(self):
        """
        Test the Coop Custom Account should merge the same invoice lines
        and make the required changes in memo when make the payment with
        selected operation type.
        """
        invoice_line_data = [
            Command.create(
                {
                    "product_id": self.product5.id,
                    "quantity": 10.0,
                    "account_id": self.account.id,
                    "name": "product test 5",
                    "price_unit": 100.00,
                }
            ),
            Command.create(
                {
                    "product_id": self.product5.id,
                    "quantity": 10.0,
                    "account_id": self.account.id,
                    "name": "product test 5",
                    "price_unit": 100.00,
                }
            ),
        ]
        move = self.AccountMove.create(
            {
                "name": "Test Customer Invoice",
                "date": "2019-01-01",
                # "journal_id": self.journal.id,
                "partner_id": self.partner3.id,
                "move_type": "in_invoice",
                "invoice_line_ids": invoice_line_data,
            }
        )
        # Merge duplicate invoice line
        move.merge_move_lines()
        self.assertEqual(
            len(move.invoice_line_ids), 1, "The invoice lines should be merged."
        )
