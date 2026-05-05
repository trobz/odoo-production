# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import HttpCase, tagged


@tagged("post_install", "-at_install")
class TestWebsiteSaleCoopPricetag(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.website = cls.env["website"].get_current_website()

    def _create_published_product(self, name, list_price=10.0, weight=0.0, volume=0.0):
        product = self.env["product.template"].create(
            {
                "name": name,
                "list_price": list_price,
                "weight": weight,
                "volume": volume,
                "is_published": True,
                "website_id": self.website.id,
            }
        )
        return product

    def test_price_weight_shown(self):
        """Product with weight shows price/kg on the shop page."""
        product = self._create_published_product(
            "Test Weight Product", list_price=10.0, weight=0.5
        )
        # price_weight = 10.0 / 0.5 = 20.0 €/kg
        self.assertEqual(product.price_weight, 20.0)

        response = self.url_open(product.website_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("price_pricetag", response.text)
        self.assertIn("/kg", response.text)

    def test_price_volume_shown(self):
        """Product with volume shows price/L on the shop page."""
        product = self._create_published_product(
            "Test Volume Product", list_price=6.0, volume=2.0
        )
        # price_volume = 6.0 / 2.0 = 3.0 €/L
        self.assertEqual(product.price_volume, 3.0)

        response = self.url_open(product.website_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("price_pricetag", response.text)
        self.assertIn("/L", response.text)

    def test_price_weight_and_volume_shown(self):
        """Product with both weight and volume shows both prices with 'or'."""
        product = self._create_published_product(
            "Test Both Product", list_price=12.0, weight=0.5, volume=1.5
        )
        self.assertEqual(product.price_weight, 24.0)
        self.assertEqual(product.price_volume, 8.0)

        response = self.url_open(product.website_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("/kg", response.text)
        self.assertIn("/L", response.text)
        self.assertIn(" or ", response.text)

    def test_no_pricetag_without_weight_and_volume(self):
        """Product without weight or volume does not show the pricetag span."""
        product = self._create_published_product(
            "Test No Pricetag Product", list_price=10.0
        )
        self.assertEqual(product.price_weight, 0.0)
        self.assertEqual(product.price_volume, 0.0)

        response = self.url_open(product.website_url)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("price_pricetag", response.text)
