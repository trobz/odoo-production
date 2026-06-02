# Copyright (C) 2019-Today: Druidoo (<https://www.druidoo.io>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestBarcodeRuleTransform(TransactionCase):
    """Tests for the transform_expr field added to barcode.rule."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.nomenclature = cls.env.ref("barcodes.default_barcode_nomenclature")

    def _create_rule(self, name, transform_expr=None):
        vals = {
            "name": name,
            "barcode_nomenclature_id": self.nomenclature.id,
            "type": "price",
            "pattern": "22.....{NNNDD}",
            "encoding": "ean13",
        }
        if transform_expr is not None:
            vals["transform_expr"] = transform_expr
        return self.env["barcode.rule"].create(vals)

    def test_field_defaults_to_empty(self):
        """transform_expr is empty by default."""
        rule = self._create_rule("Rule Without Transform")
        self.assertFalse(rule.transform_expr)

    def test_field_stores_expression(self):
        """transform_expr stores a simple arithmetic expression."""
        rule = self._create_rule("Simple Transform", "value * 0.15")
        self.assertEqual(rule.transform_expr, "value * 0.15")

    def test_field_stores_division_expression(self):
        """transform_expr stores a division expression."""
        rule = self._create_rule("Division Transform", "value / 0.85")
        self.assertEqual(rule.transform_expr, "value / 0.85")

    def test_field_stores_expression_with_code_variable(self):
        """transform_expr can reference the 'code' variable."""
        rule = self._create_rule("Code Variable", "float(code[:5]) / 100")
        self.assertEqual(rule.transform_expr, "float(code[:5]) / 100")

    def test_field_stores_expression_with_barcode_variable(self):
        """transform_expr can reference the 'barcode' variable."""
        rule = self._create_rule("Barcode Variable", "float(barcode[2:7]) * 1.20")
        self.assertEqual(rule.transform_expr, "float(barcode[2:7]) * 1.20")

    def test_field_stores_round_expression(self):
        """transform_expr accepts function-style expressions."""
        rule = self._create_rule("Round Transform", "round(value * 0.15, 2)")
        self.assertEqual(rule.transform_expr, "round(value * 0.15, 2)")

    def test_field_can_be_updated(self):
        """transform_expr can be changed after creation."""
        rule = self._create_rule("Updatable Rule", "value * 0.15")
        rule.write({"transform_expr": "value * 0.20"})
        self.assertEqual(rule.transform_expr, "value * 0.20")

    def test_field_can_be_cleared(self):
        """transform_expr can be cleared (set to empty)."""
        rule = self._create_rule("Clearable Rule", "value * 0.15")
        rule.write({"transform_expr": False})
        self.assertFalse(rule.transform_expr)

    def test_field_is_searchable_with_value(self):
        """Searching by transform_expr value returns matching rules."""
        rule = self._create_rule("Searchable Rule", "value * 0.42")
        found = self.env["barcode.rule"].search(
            [("transform_expr", "=", "value * 0.42")]
        )
        self.assertIn(rule, found)

    def test_field_is_searchable_when_empty(self):
        """Can search for rules where transform_expr is not set."""
        rule = self._create_rule("No Transform")
        found = self.env["barcode.rule"].search([("transform_expr", "=", False)])
        self.assertIn(rule, found)

    def test_rule_with_transform_coexists_with_rule_without(self):
        """Rules with and without transform_expr can coexist in the same nomenclature"""
        rule_with = self._create_rule("With Transform", "value * 0.15")
        rule_without = self._create_rule("Without Transform")
        self.assertTrue(rule_with.transform_expr)
        self.assertFalse(rule_without.transform_expr)

    def test_demo_data_rule_is_configured(self):
        """Demo rule has the expected transform_expr, type, encoding, and pattern."""
        rule = self.env.ref(
            "pos_barcode_rule_transform.rule_price_transform",
            raise_if_not_found=False,
        )
        if not rule:
            self.skipTest("Demo data not loaded")
        self.assertEqual(rule.transform_expr, "value * 0.15")
        self.assertEqual(rule.type, "price")
        self.assertEqual(rule.encoding, "ean13")
        self.assertEqual(rule.pattern, "22.....{NNNDD}")

    def test_demo_data_product_has_barcode(self):
        """Demo product has the expected barcode linked to the transform rule."""
        product = self.env.ref(
            "pos_barcode_rule_transform.product_price_transform_barcode",
            raise_if_not_found=False,
        )
        if not product:
            self.skipTest("Demo data not loaded")
        self.assertEqual(product.barcode, "2212345044547")
