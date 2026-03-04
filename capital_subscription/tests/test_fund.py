from .common import CapitalSubscriptionTest


class TestFund(CapitalSubscriptionTest):
    def test_capital_fundraising_confirm_payment01(self):
        """
        Test the Capital Fundraising with Payment Confirm True ,
        it should create Invoice and Invoice Status must be Paid
        """
        wiz = self.CapitalFund.create(
            {
                "date_invoice": self.date_invoice,
                "partner_id": self.partner_agrolite_id,
                "category_id": self.category_id,
                "share_qty": self.share_qty,
                "payment_journal_id": self.payment_journal_id,
                "confirm_payment": True,
                "payment_term_id": self.payment_term_id,
            }
        )

        invoice_dict = wiz.button_confirm()
        invoice = self.env[invoice_dict["res_model"]].browse(invoice_dict["res_id"])
        self.assertEqual(invoice.is_capital_fundraising, 1)
        self.assertEqual(invoice.fundraising_category_id.id, self.category_id)
        self.assertEqual(invoice.invoice_line_ids[0].quantity, self.share_qty)
        self.assertEqual(invoice.state, "posted")
        self.assertEqual(invoice.payment_state, "paid")

    def test_capital_fundraising_confirm_payment02(self):
        """
        Test the Capital Fundraising with Payment Confirm False,
        it should create Invoice and Invoice Status must be Open
        """
        wiz = self.CapitalFund.create(
            {
                "date_invoice": self.date_invoice,
                "partner_id": self.partner_agrolite_id,
                "category_id": self.category_id,
                "share_qty": self.share_qty,
                "payment_journal_id": self.payment_journal_id,
                "confirm_payment": False,
                "payment_term_id": self.payment_term_id,
            }
        )

        invoice_dict = wiz.button_confirm()
        invoice = self.env[invoice_dict["res_model"]].browse(invoice_dict["res_id"])
        self.assertEqual(invoice.is_capital_fundraising, 1)
        self.assertEqual(invoice.fundraising_category_id.id, self.category_id)
        self.assertEqual(invoice.invoice_line_ids[0].quantity, self.share_qty)
        self.assertEqual(invoice.state, "posted")
        self.assertIn(invoice.payment_state, ["not_paid", "in_payment", "partial"])

    def test_generate_capital_entries_when_payment_confirmed(self):
        wiz = self.CapitalFund.create(
            {
                "date_invoice": self.date_invoice,
                "partner_id": self.partner_agrolite_id,
                "category_id": self.category_id,
                "share_qty": self.share_qty,
                "payment_journal_id": self.payment_journal_id,
                "confirm_payment": True,
                "payment_term_id": self.payment_term_id,
            }
        )

        invoice_dict = wiz.button_confirm()
        invoice = self.env[invoice_dict["res_model"]].browse(invoice_dict["res_id"])
        category = invoice.fundraising_category_id
        expected_total = self.share_qty * category.product_id.lst_price

        generated_entry = self.env["account.move"].search(
            [
                ("id", "!=", invoice.id),
                ("partner_id", "=", invoice.partner_id.id),
                ("journal_id", "=", invoice.journal_id.id),
                ("move_type", "=", "entry"),
                ("narration", "=", "Paid Capital"),
                ("ref", "=", invoice.name),
            ]
        )

        self.assertEqual(len(generated_entry), 1)
        self.assertEqual(generated_entry.state, "posted")

        unpaid_line = generated_entry.line_ids.filtered(
            lambda line: line.account_id
            == category.product_id.property_account_income_id
        )
        paid_line = generated_entry.line_ids.filtered(
            lambda line: line.account_id == category.capital_account_id
        )

        self.assertEqual(len(unpaid_line), 1)
        self.assertEqual(len(paid_line), 1)
        self.assertEqual(unpaid_line.debit, expected_total)
        self.assertEqual(unpaid_line.credit, 0)
        self.assertEqual(paid_line.debit, 0)
        self.assertEqual(paid_line.credit, expected_total)
        self.assertTrue(all(generated_entry.line_ids.mapped("payment_id")))

    def test_generate_capital_entries_not_created_without_payment(self):
        wiz = self.CapitalFund.create(
            {
                "date_invoice": self.date_invoice,
                "partner_id": self.partner_agrolite_id,
                "category_id": self.category_id,
                "share_qty": self.share_qty,
                "payment_journal_id": self.payment_journal_id,
                "confirm_payment": False,
                "payment_term_id": self.payment_term_id,
            }
        )

        invoice_dict = wiz.button_confirm()
        invoice = self.env[invoice_dict["res_model"]].browse(invoice_dict["res_id"])

        generated_entries = self.env["account.move"].search(
            [
                ("id", "!=", invoice.id),
                ("partner_id", "=", invoice.partner_id.id),
                ("move_type", "=", "entry"),
                ("narration", "=", "Paid Capital"),
                ("ref", "=", invoice.name),
            ]
        )

        self.assertFalse(generated_entries)
