from odoo import Command, fields

from odoo.addons.point_of_sale.tests.common import TestPointOfSaleCommon


class TestCoopPointOfSale(TestPointOfSaleCommon):
    def test_coop_pos_order(self):
        self.pos_config.open_ui()
        pos_session = self.pos_config.current_session_id
        order = self.PosOrder.create(
            {
                "company_id": self.env.company.id,
                "partner_id": self.partner1.id,
                "pricelist_id": self.partner1.property_product_pricelist.id,
                "date_order": fields.Date.from_string("2015-12-28"),
                "session_id": pos_session.id,
                "lines": [
                    Command.create(
                        {
                            "name": "OL/0001",
                            "product_id": self.product3.id,
                            "price_unit": 450,
                            "discount": 5.0,
                            "qty": 2.0,
                            "tax_ids": [Command.set(self.product3.taxes_id.ids)],
                            "price_subtotal": 450 * (1 - 5 / 100.0) * 2,
                            "price_subtotal_incl": 450 * (1 - 5 / 100.0) * 2,
                        },
                    ),
                    Command.create(
                        {
                            "name": "OL/0002",
                            "product_id": self.product4.id,
                            "price_unit": 300,
                            "discount": 5.0,
                            "qty": 3.0,
                            "tax_ids": [Command.set(self.product4.taxes_id.ids)],
                            "price_subtotal": 300 * (1 - 5 / 100.0) * 3,
                            "price_subtotal_incl": 300 * (1 - 5 / 100.0) * 3,
                        },
                    ),
                ],
                "amount_total": 1710.0,
                "amount_tax": 0.0,
                "amount_paid": 1710.0,
                "amount_return": 0.0,
            }
        )
        self.assertEqual(
            order.week_name, "A", "POS order week number should be in paid A."
        )
        self.assertEqual(
            order.week_day, "Mon", "POS order week day should be in paid Tue."
        )
        self.assertEqual(order.cycle, "AMon", "POS order cycle should be in paid AMon.")
