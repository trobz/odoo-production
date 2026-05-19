from odoo.tests import common

from odoo.addons.website.tools import MockRequest


class TestPageGroupVisibility(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        website = cls.env.ref("website.default_website")

        cls.test_group = cls.env["res.groups"].create(
            {"name": "Test Page Access Group"}
        )
        cls.user_in_group = cls.env["res.users"].create(
            {
                "name": "User In Group",
                "login": "test_user_in_group",
                "groups_id": [
                    (4, cls.env.ref("base.group_user").id),
                    (4, cls.test_group.id),
                ],
            }
        )
        cls.user_not_in_group = cls.env["res.users"].create(
            {
                "name": "User Not In Group",
                "login": "test_user_not_in_group",
                "groups_id": [(4, cls.env.ref("base.group_user").id)],
            }
        )
        cls.website = website

    def setUp(self):
        super().setUp()
        self.page = self.env["website.page"].create(
            {
                "url": "/test-group-visibility-page",
                "website_id": self.website.id,
                "name": "Test Group Visibility Page",
                "type": "qweb",
                "arch": "<div>Test</div>",
                "key": f"website_sale_shop_access.test_page_{self._testMethodName}",
                "is_published": True,
            }
        )

    def _compute_visible_as(self, user):
        with MockRequest(self.env(user=user)):
            self.page._compute_visible()

    def test_page_visible_without_group_restriction(self):
        self._compute_visible_as(self.user_not_in_group)
        self.assertTrue(self.page.is_visible)

    def test_page_hidden_when_user_not_in_required_group(self):
        self.page.write(
            {
                "visibility": "restricted_group",
                "groups_id": [(4, self.test_group.id)],
            }
        )
        self._compute_visible_as(self.user_not_in_group)
        self.assertFalse(self.page.is_visible)

    def test_page_visible_when_user_in_required_group(self):
        self.page.write(
            {
                "visibility": "restricted_group",
                "groups_id": [(4, self.test_group.id)],
            }
        )
        self._compute_visible_as(self.user_in_group)
        self.assertTrue(self.page.is_visible)

    def test_page_hidden_when_not_published_regardless_of_group(self):
        self.page.write(
            {
                "is_published": False,
                "visibility": "restricted_group",
                "groups_id": [(4, self.test_group.id)],
            }
        )
        self._compute_visible_as(self.user_in_group)
        self.assertFalse(self.page.is_visible)


class TestMenuGroupVisibility(common.TransactionCase):
    """Test that website.menu group_ids controls is_visible."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        website = cls.env.ref("website.default_website")

        cls.test_group = cls.env["res.groups"].create(
            {"name": "Test Menu Access Group"}
        )
        cls.user_in_group = cls.env["res.users"].create(
            {
                "name": "Menu User In Group",
                "login": "test_menu_user_in_group",
                "groups_id": [
                    (4, cls.env.ref("base.group_user").id),
                    (4, cls.test_group.id),
                ],
            }
        )
        cls.user_not_in_group = cls.env["res.users"].create(
            {
                "name": "Menu User Not In Group",
                "login": "test_menu_user_not_in_group",
                "groups_id": [(4, cls.env.ref("base.group_user").id)],
            }
        )
        cls.website = website

    def setUp(self):
        super().setUp()
        self.menu = self.env["website.menu"].create(
            {
                "name": "Test Group Menu",
                "url": "/test-group-menu",
                "website_id": self.website.id,
                "parent_id": self.website.menu_id.id,
            }
        )

    def test_menu_visible_without_group_restriction(self):
        self.assertTrue(self.menu.with_user(self.user_not_in_group).is_visible)

    def test_menu_hidden_when_user_not_in_required_group(self):
        self.menu.write({"group_ids": [(4, self.test_group.id)]})
        self.assertFalse(self.menu.with_user(self.user_not_in_group).is_visible)

    def test_menu_visible_when_user_in_required_group(self):
        self.menu.write({"group_ids": [(4, self.test_group.id)]})
        self.assertTrue(self.menu.with_user(self.user_in_group).is_visible)
