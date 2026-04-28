# Copyright (C) Trobz
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import odoo.tests
from odoo import Command

from odoo.addons.point_of_sale.tests.common import TestPointOfSaleCommon


@odoo.tests.tagged("post_install", "-at_install")
class TestPosScrapOrder(TestPointOfSaleCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.scrap_product = cls.env["product.product"].create(
            {
                "name": "Scrap Test Product",
                "is_storable": True,
                "available_in_pos": True,
                "list_price": 10.0,
            }
        )
        cls.scrap_product_2 = cls.env["product.product"].create(
            {
                "name": "Scrap Test Product 2",
                "is_storable": True,
                "available_in_pos": True,
                "list_price": 5.0,
            }
        )

    def _open_session(self, scrap_order_option="always"):
        self.pos_config.write({"scrap_order_option": scrap_order_option})
        self.pos_config.open_ui()
        return self.pos_config.current_session_id

    def _order_data(self, session, lines):
        """Build minimal order dict as sent by POS UI to create_scrap_from_ui."""
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

    # -------------------------------------------------------------------------
    # create_scrap_from_ui
    # -------------------------------------------------------------------------

    def test_scrap_disabled_returns_error(self):
        """option 'no': no scrap created, access error message returned."""
        session = self._open_session(scrap_order_option="no")
        order = self._order_data(session, [(self.scrap_product, 2.0)])

        result = self.env["pos.order"].create_scrap_from_ui(order)

        self.assertFalse(result["scrap_ids"])
        self.assertEqual(result["msg"]["title"], "Access Error!")

    def test_scrap_onhand_with_stock_creates_done_scrap(self):
        """option 'onhand': scrap validated when stock is sufficient."""
        self._add_stock(self.scrap_product, 10)
        session = self._open_session(scrap_order_option="onhand")
        order = self._order_data(session, [(self.scrap_product, 3.0)])

        result = self.env["pos.order"].create_scrap_from_ui(order)

        self.assertEqual(len(result["scrap_ids"]), 1)
        self.assertEqual(result["msg"]["title"], "Successful!")
        scrap = self.env["stock.scrap"].browse(result["scrap_ids"][0])
        self.assertEqual(scrap.product_id, self.scrap_product)
        self.assertEqual(scrap.scrap_qty, 3.0)
        self.assertEqual(scrap.state, "done")

    def test_scrap_onhand_no_stock_returns_error(self):
        """option 'onhand': fails with out-of-stock error, no scrap committed."""
        session = self._open_session(scrap_order_option="onhand")
        order = self._order_data(session, [(self.scrap_product, 99.0)])

        result = self.env["pos.order"].create_scrap_from_ui(order)

        self.assertFalse(result["scrap_ids"])
        self.assertEqual(result["msg"]["title"], "No Enough Stock!")

    def test_scrap_force_ignores_missing_stock(self):
        """option 'force': scrap done even with zero stock via do_scrap()."""
        session = self._open_session(scrap_order_option="force")
        order = self._order_data(session, [(self.scrap_product, 50.0)])

        result = self.env["pos.order"].create_scrap_from_ui(order)

        self.assertEqual(len(result["scrap_ids"]), 1)
        self.assertEqual(result["msg"]["title"], "Successful!")
        scrap = self.env["stock.scrap"].browse(result["scrap_ids"][0])
        self.assertEqual(scrap.state, "done")

    def test_scrap_always_with_stock_validates(self):
        """option 'always': scrap validated when stock is available."""
        self._add_stock(self.scrap_product, 10)
        session = self._open_session(scrap_order_option="always")
        order = self._order_data(session, [(self.scrap_product, 2.0)])

        result = self.env["pos.order"].create_scrap_from_ui(order)

        self.assertEqual(len(result["scrap_ids"]), 1)
        scrap = self.env["stock.scrap"].browse(result["scrap_ids"][0])
        self.assertEqual(scrap.state, "done")

    def test_scrap_always_no_stock_creates_draft(self):
        """option 'always': scrap record created even with no stock (draft state)."""
        session = self._open_session(scrap_order_option="always")
        order = self._order_data(session, [(self.scrap_product, 99.0)])

        result = self.env["pos.order"].create_scrap_from_ui(order)

        self.assertEqual(len(result["scrap_ids"]), 1)
        scrap = self.env["stock.scrap"].browse(result["scrap_ids"][0])
        self.assertNotEqual(scrap.state, "done")

    def test_scrap_multiple_lines_creates_multiple_records(self):
        """Multiple order lines each produce a separate stock.scrap record."""
        self._add_stock(self.scrap_product, 10)
        self._add_stock(self.scrap_product_2, 10)
        session = self._open_session(scrap_order_option="always")
        order = self._order_data(
            session,
            [(self.scrap_product, 1.0), (self.scrap_product_2, 2.0)],
        )

        result = self.env["pos.order"].create_scrap_from_ui(order)

        self.assertEqual(len(result["scrap_ids"]), 2)
        scraps = self.env["stock.scrap"].browse(result["scrap_ids"])
        self.assertIn(self.scrap_product, scraps.mapped("product_id"))
        self.assertIn(self.scrap_product_2, scraps.mapped("product_id"))

    def test_scrap_origin_references_session(self):
        """Created scrap's origin contains the POS session name."""
        self._add_stock(self.scrap_product, 5)
        session = self._open_session(scrap_order_option="always")
        order = self._order_data(session, [(self.scrap_product, 1.0)])

        result = self.env["pos.order"].create_scrap_from_ui(order)

        scrap = self.env["stock.scrap"].browse(result["scrap_ids"][0])
        self.assertIn(session.display_name, scrap.origin)

    # -------------------------------------------------------------------------
    # get_list_for_ui
    # -------------------------------------------------------------------------

    def test_get_list_returns_pos_scraps(self):
        """get_list_for_ui returns scraps originating from POS sessions."""
        self._add_stock(self.scrap_product, 10)
        session = self._open_session(scrap_order_option="always")
        order = self._order_data(session, [(self.scrap_product, 1.0)])
        result = self.env["pos.order"].create_scrap_from_ui(order)
        scrap = self.env["stock.scrap"].browse(result["scrap_ids"][0])

        scrap_list = self.env["stock.scrap"].get_list_for_ui()
        names = [s["name"] for s in scrap_list]

        self.assertIn(scrap.name, names)

    def test_get_list_excludes_non_pos_scraps(self):
        """get_list_for_ui does not return scraps with unrelated origin."""
        non_pos_scrap = self.env["stock.scrap"].create(
            {
                "product_id": self.scrap_product.id,
                "scrap_qty": 1.0,
                "product_uom_id": self.scrap_product.uom_id.id,
                "origin": "Manual Inventory Adjustment",
            }
        )

        scrap_list = self.env["stock.scrap"].get_list_for_ui()
        names = [s["name"] for s in scrap_list]

        self.assertNotIn(non_pos_scrap.name, names)

    def test_get_list_fields(self):
        """Each entry in get_list_for_ui has all required fields."""
        self._add_stock(self.scrap_product, 5)
        session = self._open_session(scrap_order_option="always")
        order = self._order_data(session, [(self.scrap_product, 1.0)])
        self.env["pos.order"].create_scrap_from_ui(order)

        scrap_list = self.env["stock.scrap"].get_list_for_ui()
        self.assertTrue(scrap_list)
        entry = scrap_list[0]

        for field in ("name", "product_display_name", "qty_str", "date", "origin"):
            self.assertIn(field, entry, f"Missing field: {field}")

    def test_get_list_limited_to_50(self):
        """get_list_for_ui returns at most 50 records."""
        scrap_list = self.env["stock.scrap"].get_list_for_ui()
        self.assertLessEqual(len(scrap_list), 50)
