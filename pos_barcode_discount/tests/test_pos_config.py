from odoo.tests import common, tagged


@tagged("post_install", "-at_install")
class TestPosBarcodeDiscount(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env.company.write({"country_id": False})
        cls.category_parent = cls.env["product.category"].create(
            {"name": "Parent Category"}
        )
        cls.category_child = cls.env["product.category"].create(
            {"name": "Child Category", "parent_id": cls.category_parent.id}
        )
        cls.category_grandchild = cls.env["product.category"].create(
            {
                "name": "Grandchild Category",
                "parent_id": cls.category_child.id,
            }
        )
        cls.category_other = cls.env["product.category"].create(
            {"name": "Other Category"}
        )
        cls.pos_config = cls.env["pos.config"].create(
            {
                "name": "Test POS",
            }
        )

    def test_barcode_rule_created(self):
        rule = self.env["barcode.rule"].search(
            [("name", "=", "Discounted Product Categories")]
        )
        self.assertTrue(rule)
        self.assertEqual(rule.type, "discount")
        self.assertEqual(rule.encoding, "ean13")
        self.assertEqual(rule.pattern, "22{NN}........")

    def test_discount_by_category_disabled(self):
        self.assertFalse(self.pos_config.discount_by_category)
        self.assertFalse(self.pos_config.discount_category_ids)
        self.assertFalse(self.pos_config.discount_category_all_ids)

    def test_compute_all_categories_none_selected(self):
        self.assertEqual(
            len(self.pos_config.discount_category_all_ids),
            0,
        )

    def test_compute_all_categories_single_no_children(self):
        self.pos_config.write(
            {"discount_category_ids": [(6, 0, [self.category_other.id])]}
        )
        self.assertIn(
            self.category_other,
            self.pos_config.discount_category_all_ids,
        )

    def test_compute_all_categories_includes_children(self):
        self.pos_config.write(
            {"discount_category_ids": [(6, 0, [self.category_parent.id])]}
        )
        self.assertIn(self.category_parent, self.pos_config.discount_category_all_ids)
        self.assertIn(self.category_child, self.pos_config.discount_category_all_ids)
        self.assertIn(
            self.category_grandchild,
            self.pos_config.discount_category_all_ids,
        )
        self.assertNotIn(self.category_other, self.pos_config.discount_category_all_ids)

    def test_compute_all_categories_child_only(self):
        self.pos_config.write(
            {"discount_category_ids": [(6, 0, [self.category_child.id])]}
        )
        self.assertNotIn(
            self.category_parent,
            self.pos_config.discount_category_all_ids,
        )
        self.assertIn(self.category_child, self.pos_config.discount_category_all_ids)
        self.assertIn(
            self.category_grandchild,
            self.pos_config.discount_category_all_ids,
        )

    def test_res_config_settings_related(self):
        self.env["res.config.settings"].create({})
