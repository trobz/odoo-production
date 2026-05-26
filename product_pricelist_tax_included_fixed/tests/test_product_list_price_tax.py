# © 2016 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import TransactionCase


class TestProductListPriceTax(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ProductTemplate = cls.env["product.template"]
        cls.AccountTax = cls.env["account.tax"]
        cls.account_tax = cls.AccountTax.create(
            {
                "name": "Sale-Test-21%",
                "type_tax_use": "sale",
                "amount": 21.00,
            }
        )
        cls.product_template = cls.ProductTemplate.create(
            {
                "name": "Product - template - Test",
                "taxes_id": [cls.account_tax.id],
                "list_price": 1000.00,
                "list_price_tax": 1210.00,
            }
        )

    def test_create_product_tax(self):
        product_template_tax = self.ProductTemplate.create(
            {
                "name": "Product - template - Test",
                "taxes_id": [self.account_tax.id],
                "list_price_tax": 1210.00,
            }
        )
        self.assertAlmostEqual(product_template_tax.list_price, 1000.00, places=2)

    def test_create_product_without_tax(self):
        product_template_tax = self.ProductTemplate.create(
            {
                "name": "Product - template - Test",
                "taxes_id": [self.account_tax.id],
                "list_price": 1000.00,
            }
        )
        self.assertAlmostEqual(product_template_tax.list_price_tax, 1210.00, places=2)

    def test_write_product_tax(self):
        self.product_template.list_price_tax = 2240.00
        self.assertAlmostEqual(self.product_template.list_price, 1851.24, places=2)
        self.product_template.list_price = 1000.00
        self.assertAlmostEqual(self.product_template.list_price_tax, 1210.00, places=2)
