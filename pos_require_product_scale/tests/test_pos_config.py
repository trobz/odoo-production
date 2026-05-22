from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestPosRequireProductScale(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.pos_config = cls.env["pos.config"].create({"name": "Test Shop"})
        cls.product_to_weight = cls.env["product.product"].create(
            {
                "name": "Weighted Product",
                "available_in_pos": True,
                "list_price": 10.0,
                "to_weight": True,
            }
        )
        cls.product_normal = cls.env["product.product"].create(
            {
                "name": "Normal Product",
                "available_in_pos": True,
                "list_price": 5.0,
                "to_weight": False,
            }
        )

    def test_field_default_is_false(self):
        self.assertFalse(self.pos_config.require_product_scale)

    def test_field_can_be_enabled(self):
        self.pos_config.write({"require_product_scale": True})
        self.assertTrue(self.pos_config.require_product_scale)

    def test_require_product_scale_field_exists_on_model(self):
        """require_product_scale is declared on pos.config and will be sent to POS.

        pos.config._load_pos_data_fields returns [] (all fields), so any field
        declared on the model is automatically included in the session data.
        """
        self.assertIn("require_product_scale", self.env["pos.config"]._fields)

    def test_to_weight_field_loaded_for_products(self):
        """to_weight is explicitly listed in product.product POS data fields."""
        fields = self.env["product.product"]._load_pos_data_fields(self.pos_config.id)
        self.assertIn("to_weight", fields)
