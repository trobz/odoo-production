from odoo.exceptions import UserError

from .common import CapitalSubscriptionTest


class TestAccountMoveConstraints(CapitalSubscriptionTest):
    def _prepare_invoice_vals(
        self,
        *,
        product,
        quantity,
        is_capital_fundraising=False,
        category=False,
    ):
        invoice_obj = self.env["account.move"]
        vals = invoice_obj.default_get(invoice_obj._fields.keys())
        vals.update(
            {
                "move_type": "out_invoice",
                "invoice_date": self.date_invoice,
                "partner_id": self.partner_agrolite_id,
                "journal_id": self.env.ref(
                    "capital_subscription.sale_capital_journal"
                ).id,
                "invoice_payment_term_id": self.payment_term_id,
                "is_capital_fundraising": is_capital_fundraising,
                "fundraising_category_id": category and category.id or False,
                "invoice_line_ids": [
                    [
                        0,
                        0,
                        {
                            "product_id": product.id,
                            "name": product.name,
                            "quantity": quantity,
                            "price_unit": product.lst_price,
                            "product_uom_id": product.uom_id.id,
                            "account_id": product.property_account_income_id.id,
                        },
                    ]
                ],
            }
        )
        return vals

    def test_check_capital_fundraising_requires_category(self):
        category = self.env["capital.fundraising.category"].browse(self.category_id)
        with self.assertRaises(UserError):
            self.env["account.move"].create(
                self._prepare_invoice_vals(
                    product=category.product_id,
                    quantity=10,
                    is_capital_fundraising=True,
                    category=False,
                )
            )

    def test_check_capital_fundraising_forbids_capital_product_on_non_capital_invoice(
        self,
    ):
        category = self.env["capital.fundraising.category"].browse(self.category_id)
        with self.assertRaises(UserError):
            self.env["account.move"].create(
                self._prepare_invoice_vals(
                    product=category.product_id,
                    quantity=10,
                    is_capital_fundraising=False,
                    category=False,
                )
            )

    def test_check_capital_fundraising_enforces_minimum_qty_on_post(self):
        category = self.env["capital.fundraising.category"].browse(self.category_id)
        invoice = self.env["account.move"].create(
            self._prepare_invoice_vals(
                product=category.product_id,
                quantity=1,
                is_capital_fundraising=True,
                category=category,
            )
        )

        with self.assertRaises(UserError):
            invoice.action_post()
