from odoo.exceptions import UserError

from .common import CapitalSubscriptionTest


class TestRefund(CapitalSubscriptionTest):
    def _create_capital_invoice(self, share_qty=10):
        wiz = self.CapitalFund.create(
            {
                "date_invoice": self.date_invoice,
                "partner_id": self.partner_agrolite_id,
                "category_id": self.category_id,
                "share_qty": share_qty,
                "payment_journal_id": self.payment_journal_id,
                "confirm_payment": True,
                "payment_term_id": self.payment_term_id,
            }
        )
        invoice_dict = wiz.button_confirm()
        return self.env[invoice_dict["res_model"]].browse(invoice_dict["res_id"])

    def test_refund_moves_applies_refund_deficit_share(self):
        invoice = self._create_capital_invoice(share_qty=10)
        category = invoice.fundraising_category_id
        source_product = category.product_id
        deficit_product = self.env.ref("capital_subscription.product_deficit_share")
        deficit_account = self.env.ref(
            "capital_subscription.unpaid_capital_account_category_A"
        )
        refund_qty = 3
        deficit_amount = 2.0

        source_product.write({"deficit_share_account_id": deficit_account.id})
        category.write({"deficit_product_id": deficit_product.id})
        self.env["capital.fundraising.deficit"].create(
            {
                "fund_cate_id": category.id,
                "start_date": self.date_invoice,
                "amount_by_share": deficit_amount,
            }
        )

        reversal_wizard = (
            self.env["account.move.reversal"]
            .with_context(active_model="account.move", active_ids=invoice.ids)
            .create(
                {
                    "date": self.date_invoice,
                    "refund_quantity": refund_qty,
                    "journal_id": invoice.journal_id.id,
                }
            )
        )
        reversal_wizard.refund_moves()

        refund = reversal_wizard.new_move_ids.filtered(
            lambda move: move.move_type == "out_refund"
        )
        self.assertEqual(len(refund), 1)

        capital_lines = refund.invoice_line_ids.filtered(
            lambda line: line.product_id == source_product
        )
        self.assertEqual(len(capital_lines), 1)
        self.assertEqual(capital_lines.quantity, refund_qty)
        self.assertEqual(capital_lines.account_id, category.capital_account_id)

        deficit_lines = refund.invoice_line_ids.filtered(
            lambda line: line.product_id == deficit_product
        )
        self.assertEqual(len(deficit_lines), 1)
        self.assertEqual(deficit_lines.quantity, refund_qty)
        self.assertEqual(
            deficit_lines.account_id, source_product.deficit_share_account_id
        )
        self.assertEqual(deficit_lines.price_unit, -deficit_amount)

    def test_refund_quantity_must_be_positive_for_capital_refund(self):
        invoice = self._create_capital_invoice(share_qty=10)

        with self.assertRaises(UserError):
            self.env["account.move.reversal"].with_context(
                active_model="account.move", active_ids=invoice.ids
            ).create(
                {
                    "date": self.date_invoice,
                    "refund_quantity": 0,
                    "journal_id": invoice.journal_id.id,
                }
            )
