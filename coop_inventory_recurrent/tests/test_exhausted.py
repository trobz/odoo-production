# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import Command
from odoo.tests.common import TransactionCase


class TestExhausted(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.location = cls.env.ref("stock.stock_location_stock")
        cls.category = cls.env["product.category"].create({"name": "Test Categ"})

        # Product with stock
        cls.product_stocked = cls.env["product.product"].create(
            {
                "name": "Product With Stock",
                "type": "consu",
                "is_storable": True,
                "categ_id": cls.category.id,
            }
        )
        cls.env["stock.quant"].sudo().create(
            {
                "product_id": cls.product_stocked.id,
                "location_id": cls.location.id,
                "quantity": 10,
            }
        )

        # Product with no stock (exhausted)
        cls.product_exhausted = cls.env["product.product"].create(
            {
                "name": "Product No Stock",
                "type": "consu",
                "is_storable": True,
                "categ_id": cls.category.id,
            }
        )

        cls.categ_group = cls.env["stock.inventory.category.group"].create(
            {
                "name": "Test Group",
                "location_id": cls.location.id,
                "category_ids": [Command.set([cls.category.id])],
                "line_ids": [
                    Command.create({"category_id": cls.category.id, "copies": "1"})
                ],
            }
        )

    def _make_inventory(self, exhausted):
        return self.env["stock.inventory"].create(
            {
                "name": "Test Inventory",
                "product_selection": "category",
                "category_id": self.category.id,
                "location_ids": [Command.set([self.location.id])],
                "exhausted": exhausted,
            }
        )

    def test_exhausted_true_includes_zero_qty_products(self):
        inventory = self._make_inventory(exhausted=True)
        inventory.action_state_to_in_progress()
        product_ids = inventory.stock_quant_ids.mapped("product_id")
        self.assertIn(
            self.product_stocked,
            product_ids,
            "Product with stock must be included",
        )
        self.assertIn(
            self.product_exhausted,
            product_ids,
            "Exhausted product must be included when exhausted=True",
        )

    def test_exhausted_false_excludes_zero_qty_products(self):
        inventory = self._make_inventory(exhausted=False)
        inventory.action_state_to_in_progress()
        product_ids = inventory.stock_quant_ids.mapped("product_id")
        self.assertIn(
            self.product_stocked,
            product_ids,
            "Product with stock must be included",
        )
        self.assertNotIn(
            self.product_exhausted,
            product_ids,
            "Exhausted product must be excluded when exhausted=False",
        )

    def test_wizard_propagates_exhausted_to_inventory(self):
        for exhausted_value in (True, False):
            wizard = self.env["stock.inventory.recurrent.wizard"].create(
                {
                    "category_group_ids": [Command.set([self.categ_group.id])],
                    "exhausted": exhausted_value,
                }
            )
            wizard.action_execute()
            inventories = self.env["stock.inventory"].search(
                [
                    ("category_id", "=", self.category.id),
                    ("state", "=", "in_progress"),
                ]
            )
            self.assertTrue(inventories, "Wizard must create inventories")
            for inv in inventories:
                self.assertEqual(
                    inv.exhausted,
                    exhausted_value,
                    f"Inventory exhausted must match wizard value ({exhausted_value})",
                )
            inventories.write({"state": "cancel"})
