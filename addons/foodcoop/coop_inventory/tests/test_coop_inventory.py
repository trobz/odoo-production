from odoo import fields
from odoo.tests.common import TransactionCase


class TestCoopInventory(TransactionCase):
    def setUp(self):
        super().setUp()
        self.storable_product = self.env["product.product"].create(
            {"name": "Storable Product", "type": "consu", "is_storable": True}
        )
        self.consumable_product = self.env["product.product"].create(
            {"name": "Consumable Product", "type": "consu", "is_storable": False}
        )
        self.customer = self.env["res.partner"].create(
            {"name": "Test Customer1", "customer_rank": 1}
        )
        self.purchase_order = self.env["purchase.order"].create(
            {"partner_id": self.customer.id}
        )
        self.po_line_1 = self.env["purchase.order.line"].create(
            {
                "order_id": self.purchase_order.id,
                "product_id": self.storable_product.id,
                "date_planned": fields.Datetime.now(),
                "name": "Storable",
                "product_qty": 5,
                "product_uom": self.env.ref("uom.product_uom_unit").id,
                "price_unit": 10.0,
            }
        )
        self.po_line_2 = self.env["purchase.order.line"].create(
            {
                "order_id": self.purchase_order.id,
                "product_id": self.consumable_product.id,
                "date_planned": fields.Datetime.now(),
                "name": "Consumable",
                "product_qty": 3,
                "product_uom": self.env.ref("uom.product_uom_unit").id,
                "price_unit": 5.0,
            }
        )

    def test_001_check_picking(self):
        self.purchase_order.button_confirm()
        self.assertTrue(
            self.po_line_1.move_ids, "Picking must be created for a Storable product!"
        )
        self.assertFalse(
            self.po_line_2.move_ids,
            "Picking must NOT be created for a Consumable product!",
        )
