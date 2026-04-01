from odoo.tests import common


class TestFoodcoopModule(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ResPartner = cls.env["res.partner"]
        cls.ResUsers = cls.env["res.users"]
        cls.ResGroups = cls.env["res.groups"]

    def test_functional_admin_group_exists(self):
        """Test that functional_admin group exists"""
        group = self.env.ref(
            "foodcoop_module.functional_admin", raise_if_not_found=False
        )
        self.assertTrue(group, "Functional admin group should exist")

    def test_functional_admin_group_name(self):
        """Test functional admin group has correct name"""
        group = self.env.ref(
            "foodcoop_module.functional_admin", raise_if_not_found=False
        )
        if group:
            self.assertEqual(group.name, "Foodcoop Administration")

    def test_functional_admin_group_implied_user(self):
        """Test functional admin group has implied group"""
        group = self.env.ref(
            "foodcoop_module.functional_admin", raise_if_not_found=False
        )
        if group:
            user_group = self.env.ref("base.group_user", raise_if_not_found=False)
            if user_group:
                self.assertIn(user_group, group.implied_ids)

    def test_partner_fields_exist(self):
        """Test partner has signup fields"""
        partner = self.ResPartner.create(
            {
                "name": "Test Partner",
            }
        )
        self.assertTrue(hasattr(partner, "signup_token"))
        self.assertTrue(hasattr(partner, "signup_type"))
        self.assertTrue(hasattr(partner, "signup_expiration"))

    def test_admin_menu_exists(self):
        """Test admin menu exists"""
        menu = self.env.ref("foodcoop_module.admin_menu", raise_if_not_found=False)
        self.assertTrue(menu, "Admin menu should exist")

    def test_user_menu_exists(self):
        """Test user menu exists"""
        menu = self.env.ref("foodcoop_module.admin_user_menu", raise_if_not_found=False)
        self.assertTrue(menu, "User menu should exist")
