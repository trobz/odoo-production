from odoo.tests import common


class TestCoopDeliveryCategory(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.DeliveryCategory = cls.env["delivery.category"]
        cls.ProductTemplate = cls.env["product.template"]

    def test_delivery_category_creation(self):
        """Test that delivery category can be created"""
        category = self.DeliveryCategory.create(
            {
                "name": "Test Category",
            }
        )
        self.assertTrue(category)
        self.assertEqual(category.name, "Test Category")

    def test_delivery_category_with_products(self):
        """Test delivery category with products"""
        product = self.ProductTemplate.create(
            {
                "name": "Test Product",
                "type": "consu",
            }
        )
        category = self.DeliveryCategory.create(
            {
                "name": "Test Category",
                "product_ids": [(4, product.id)],
            }
        )
        self.assertIn(product, category.product_ids)

    def test_product_template_delivery_categ_field(self):
        """Test product template has delivery category field"""
        product = self.ProductTemplate.create(
            {
                "name": "Test Product",
                "type": "consu",
            }
        )
        self.assertTrue(hasattr(product, "delivery_categ_ids"))

    def test_computed_purchase_order_delivery_categ_field(self):
        """Test computed purchase order has delivery category field"""
        cpo = self.env["computed.purchase.order"].search([], limit=1)
        if cpo:
            self.assertTrue(hasattr(cpo, "delivery_categ_ids"))
