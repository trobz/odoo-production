# Copyright (C) Trobz (<https://trobz.com/>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import odoo.tests
from odoo import Command

from odoo.addons.point_of_sale.tests.common import TestPointOfSaleCommon


@odoo.tests.tagged("post_install", "-at_install")
class TestPosScrapOrderOrigin(TestPointOfSaleCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.pos_config.write({"scrap_order_option": "always"})

        cls.product = cls.env["product.product"].create(
            {
                "name": "Scrap Origin Test Product",
                "is_storable": True,
                "available_in_pos": True,
                "list_price": 10.0,
            }
        )

        cls.reason_tag = cls.env["stock.scrap.reason.tag"].create(
            {"name": "Test Reason"}
        )

    def _open_session(self):
        self.pos_config.open_ui()
        return self.pos_config.current_session_id

    def _order_data(self, session, lines):
        return {
            "pos_session_id": session.id,
            "lines": [
                Command.create({"product_id": product.id, "qty": qty})
                for product, qty in lines
            ],
        }

    def _add_stock(self, product, qty):
        location = self.company_data["default_warehouse"].lot_stock_id
        self.env["stock.quant"].with_context(
            inventory_mode=True,
            allowed_company_ids=self.env.companies.ids,
        ).create(
            {
                "product_id": product.id,
                "inventory_quantity": qty,
                "location_id": location.id,
            }
        ).action_apply_inventory()

    def test_no_reason_tag_returns_error(self):
        """Missing scrap_reason_tag_id in default_vals returns an error."""
        session = self._open_session()
        order = self._order_data(session, [(self.product, 1.0)])

        result = self.env["pos.order"].create_scrap_from_ui(order)

        self.assertFalse(result["scrap_ids"])
        self.assertEqual(result["msg"]["title"], "Error!")
        self.assertIn("reason tag", result["msg"]["body"].lower())

    def test_with_reason_tag_creates_scrap(self):
        """Valid scrap_reason_tag_id produces a scrap with scrap_reason_tag_ids set."""
        self._add_stock(self.product, 10)
        session = self._open_session()
        order = self._order_data(session, [(self.product, 2.0)])

        result = self.env["pos.order"].create_scrap_from_ui(
            order, {"scrap_reason_tag_id": self.reason_tag.id}
        )

        self.assertEqual(len(result["scrap_ids"]), 1)
        self.assertEqual(result["msg"]["title"], "Successful!")
        scrap = self.env["stock.scrap"].browse(result["scrap_ids"][0])
        self.assertIn(self.reason_tag, scrap.scrap_reason_tag_ids)
