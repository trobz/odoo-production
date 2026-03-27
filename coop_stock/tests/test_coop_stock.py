from datetime import datetime

from odoo.tests import Form
from odoo.tests.common import TransactionCase


class CoopStockTest(TransactionCase):
    def setUp(self):
        super().setUp()

        self.categ_unit = self.env.ref("uom.product_uom_categ_unit")
        self.uom_unit = self.env["uom.uom"].search(
            [("category_id", "=", self.categ_unit.id), ("uom_type", "=", "reference")],
            limit=1,
        )
        self.stock_location = self.env.ref("stock.stock_location_stock")
        self.partner_3 = self.env.ref("base.res_partner_3")

    def test_01_stock_inventory_post_inventory(self):
        product_a = self.env["product.product"].create(
            {
                "name": "Product D",
                "is_storable": True,
                "uom_id": self.uom_unit.id,
                "uom_po_id": self.uom_unit.id,
            }
        )

        inventory_quant = self.env["stock.quant"].create(
            {
                "location_id": self.stock_location.id,
                "product_id": product_a.id,
                "inventory_quantity": 20,
            }
        )
        inventory_quant.action_apply_inventory()
        self.assertEqual(
            self.env["stock.quant"]._get_available_quantity(
                product_a, self.stock_location
            ),
            20.0,
        )

    def test_02_stock_picking(self):
        picking_form = Form(self.env["stock.picking"])
        self.picking_type = self.env.ref("stock.picking_type_out")
        self.product = self.env.ref("product.product_delivery_01")
        picking_form.partner_id = self.partner_3
        picking_form.picking_type_id = self.picking_type
        self.picking = picking_form.save()
        self.picking._onchange_picking_type()
        self.move = self.env["stock.move"].create(
            {
                "picking_id": self.picking.id,
                "product_id": self.product.id,
                "name": "Test",
                "product_uom_qty": 20,
                "product_uom": self.env.ref("uom.product_uom_unit").id,
                "location_id": self.picking.location_id.id,
                "location_dest_id": self.picking.location_dest_id.id,
            }
        )
        self.picking.copy_expected_qtys()
        self.assertEqual(
            self.move.quantity,
            self.move.product_uom_qty,
            "copy_expected_qtys should set quantity = product_uom_qty",
        )

    def test_03_inventory_move_date_from_context(self):
        """Move date must match inventory_datetime passed via context."""
        product = self.env["product.product"].create(
            {
                "name": "Product Date Test",
                "is_storable": True,
                "uom_id": self.uom_unit.id,
                "uom_po_id": self.uom_unit.id,
            }
        )
        inventory_date = datetime(2024, 1, 15, 10, 0, 0)
        quant = self.env["stock.quant"].create(
            {
                "location_id": self.stock_location.id,
                "product_id": product.id,
                "inventory_quantity": 10,
            }
        )
        quant.with_context(inventory_datetime=inventory_date).action_apply_inventory()
        move = self.env["stock.move"].search(
            [("product_id", "=", product.id), ("is_inventory", "=", True)],
            limit=1,
        )
        self.assertTrue(move, "Inventory move should have been created")
        self.assertEqual(
            move.date.replace(tzinfo=None),
            inventory_date,
            "Move date should match inventory_datetime from context",
        )

    def test_04_inventory_move_date_from_inventory_date_field(self):
        """Move date must match quant.inventory_date when no context datetime."""
        product = self.env["product.product"].create(
            {
                "name": "Product InventoryDate Test",
                "is_storable": True,
                "uom_id": self.uom_unit.id,
                "uom_po_id": self.uom_unit.id,
            }
        )
        quant = self.env["stock.quant"].create(
            {
                "location_id": self.stock_location.id,
                "product_id": product.id,
                "inventory_quantity": 5,
                "inventory_date": "2024-03-20",
            }
        )
        quant.action_apply_inventory()
        move = self.env["stock.move"].search(
            [("product_id", "=", product.id), ("is_inventory", "=", True)],
            limit=1,
        )
        self.assertTrue(move, "Inventory move should have been created")
        self.assertEqual(
            move.date.date(),
            datetime(2024, 3, 20).date(),
            "Move date should match quant.inventory_date",
        )
