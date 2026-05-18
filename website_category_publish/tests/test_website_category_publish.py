# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.tests.common import TransactionCase


class TestWebsiteCategoryPublish(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Category = cls.env["product.public.category"]

        cls.cat_parent = Category.create({"name": "Parent", "is_published": True})
        cls.cat_child1 = Category.create(
            {"name": "Child 1", "parent_id": cls.cat_parent.id, "is_published": True}
        )
        cls.cat_child2 = Category.create(
            {"name": "Child 2", "parent_id": cls.cat_parent.id, "is_published": True}
        )
        cls.cat_standalone = Category.create(
            {"name": "Standalone", "is_published": True}
        )

        cls.product_with_categ = cls.env["product.template"].create(
            {
                "name": "Product with category",
                "public_categ_ids": [(6, 0, [cls.cat_parent.id])],
            }
        )
        cls.product_no_categ = cls.env["product.template"].create(
            {"name": "Product without category"}
        )
        cls.product_multi_categ = cls.env["product.template"].create(
            {
                "name": "Product multi category",
                "public_categ_ids": [
                    (6, 0, [cls.cat_parent.id, cls.cat_standalone.id])
                ],
            }
        )

    # --- Tests: children sync ---

    def test_unpublish_parent_syncs_children(self):
        """Unpublishing a parent category syncs all published children."""
        self.cat_parent.write({"is_published": False})
        self.assertFalse(self.cat_child1.is_published)
        self.assertFalse(self.cat_child2.is_published)

    def test_publish_parent_syncs_children(self):
        """Publishing a parent category syncs all unpublished children."""
        self.cat_parent.write({"is_published": False})
        self.cat_parent.write({"is_published": True})
        self.assertTrue(self.cat_child1.is_published)
        self.assertTrue(self.cat_child2.is_published)

    def test_sync_only_different_children(self):
        """Only children with a different published state are synced."""
        self.cat_child1.write({"is_published": False})
        # cat_child1 is already unpublished, cat_child2 is still published
        self.cat_parent.write({"is_published": False})
        # both must now be unpublished
        self.assertFalse(self.cat_child1.is_published)
        self.assertFalse(self.cat_child2.is_published)

    def test_no_sync_when_field_unchanged(self):
        """write() without is_published does not sync children."""
        self.cat_child1.write({"is_published": False})
        self.cat_parent.write({"name": "Parent Renamed"})
        # cat_child1 remains unpublished since is_published was not in vals
        self.assertFalse(self.cat_child1.is_published)

    # --- Tests: is_categ_published on product ---

    def test_product_no_category_always_published(self):
        """A product with no category is always considered categ-published."""
        self.assertTrue(self.product_no_categ.is_categ_published)

    def test_product_published_category(self):
        """A product whose category is published has is_categ_published = True."""
        self.assertTrue(self.product_with_categ.is_categ_published)

    def test_product_unpublished_category(self):
        """A product whose category is unpublished has is_categ_published = False."""
        self.cat_parent.write({"is_published": False})
        self.assertFalse(self.product_with_categ.is_categ_published)

    def test_product_multi_categ_one_published(self):
        """A product with one published category out of two is categ-published."""
        self.cat_parent.write({"is_published": False})
        # cat_standalone is still published
        self.assertTrue(self.product_multi_categ.is_categ_published)

    def test_product_multi_categ_all_unpublished(self):
        """A product with all categories unpublished has is_categ_published = False."""
        self.cat_parent.write({"is_published": False})
        self.cat_standalone.write({"is_published": False})
        self.assertFalse(self.product_multi_categ.is_categ_published)
