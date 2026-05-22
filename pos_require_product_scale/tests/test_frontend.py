from odoo.tests import tagged

from odoo.addons.point_of_sale.tests.test_frontend import TestPointOfSaleHttpCommon


@tagged("post_install", "-at_install")
class TestPosRequireProductScaleFrontend(TestPointOfSaleHttpCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.weighted_product = cls.env["product.product"].create(
            {
                "name": "Weighted Product",
                "available_in_pos": True,
                "list_price": 10.0,
                "taxes_id": False,
                "to_weight": True,
            }
        )
        cls.normal_product = cls.env["product.product"].create(
            {
                "name": "Normal Product",
                "available_in_pos": True,
                "list_price": 5.0,
                "taxes_id": False,
                "to_weight": False,
            }
        )

    def test_scale_popup_cancel_stays_on_product_screen(self):
        """Popup appears for to_weight product with integer qty.

        Cancelling the dialog keeps the cashier on the product screen.
        """
        self.main_pos_config.write({"require_product_scale": True})
        self.start_pos_tour("pos_require_scale_cancel_tour")

    def test_scale_popup_confirm_proceeds_to_payment(self):
        """Popup appears for to_weight product with integer qty.

        Confirming the dialog proceeds to the payment screen.
        """
        self.main_pos_config.write({"require_product_scale": True})
        self.start_pos_tour("pos_require_scale_confirm_tour")

    def test_no_popup_for_normal_product(self):
        """No popup when product does not have to_weight=True."""
        self.main_pos_config.write({"require_product_scale": True})
        self.start_pos_tour("pos_require_scale_normal_product_tour")

    def test_no_popup_when_setting_disabled(self):
        """No popup when require_product_scale is False, even for to_weight products."""
        self.main_pos_config.write({"require_product_scale": False})
        self.start_pos_tour("pos_require_scale_setting_disabled_tour")
