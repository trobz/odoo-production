from odoo.exceptions import AccessError
from odoo.tests import common

from odoo.addons.auth_signup.tests.test_auth_signup import TestAuthSignupFlow


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
        self.assertTrue(hasattr(partner, "signup_type"))

    def test_admin_menu_exists(self):
        """Test admin menu exists"""
        menu = self.env.ref("foodcoop_module.admin_menu", raise_if_not_found=False)
        self.assertTrue(menu, "Admin menu should exist")

    def test_user_menu_exists(self):
        """Test user menu exists"""
        menu = self.env.ref("foodcoop_module.admin_user_menu", raise_if_not_found=False)
        self.assertTrue(menu, "User menu should exist")


class TestAuthSignupFunctionalAdmin(TestAuthSignupFlow):
    def test_functional_admin_can_access_signup_type(self):
        group = self.env.ref(
            "foodcoop_module.functional_admin", raise_if_not_found=False
        )
        if not group:
            self.skipTest("foodcoop_module.functional_admin group not found")

        partner = self.env["res.partner"].create(
            {
                "name": "Test Partner Signup",
            }
        )

        functional_admin_user = self.env["res.users"].create(
            {
                "login": "functional_admin_access_test",
                "name": "Functional Admin Access Test",
                "email": "functional_admin_access@test.com",
                "groups_id": [(4, group.id)],
            }
        )

        partner.with_user(functional_admin_user).read(["signup_type"])

        user_without_group = self.env["res.users"].create(
            {
                "login": "regular_user_test",
                "name": "Regular User Test",
                "email": "regular_user@test.com",
            }
        )

        with self.assertRaises(Exception):  # noqa: B017
            partner.with_user(user_without_group).read(["signup_type"])


class TestResUsersRoleLinePrivilege(common.TransactionCase):
    """Tests for ResUsersRoleLine privilege escalation fix."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        cls.functional_admin_group = cls.env.ref("foodcoop_module.functional_admin")

        # functional_admin user — not sysadmin
        cls.fa_user = cls.env["res.users"].create(
            {
                "name": "Test Functional Admin User",
                "login": "test_fa_privilege@test.com",
                "groups_id": [(4, cls.functional_admin_group.id)],
            }
        )

        # Target user for role assignment
        cls.target_user = cls.env["res.users"].create(
            {
                "name": "Test Target User",
                "login": "test_target_role@test.com",
                "groups_id": [(4, cls.env.ref("base.group_user").id)],
            }
        )

        # Safe role — no functional_admin in implied_ids
        safe_group = cls.env["res.groups"].create({"name": "Test Safe Group FA"})
        cls.safe_role = cls.env["res.users.role"].create(
            {
                "name": "Test Safe Role FA",
                "group_id": safe_group.id,
            }
        )

        # Restricted role — has functional_admin in implied_ids
        restricted_group = cls.env["res.groups"].create(
            {"name": "Test Restricted Group FA"}
        )
        cls.restricted_role = cls.env["res.users.role"].create(
            {
                "name": "Test Restricted Role FA",
                "group_id": restricted_group.id,
            }
        )
        cls.restricted_role.write({"implied_ids": [(4, cls.functional_admin_group.id)]})

    def test_functional_admin_cannot_assign_restricted_role(self):
        with self.assertRaises(AccessError):
            self.env["res.users.role.line"].with_user(self.fa_user).create(
                {
                    "role_id": self.restricted_role.id,
                    "user_id": self.target_user.id,
                }
            )

    def test_functional_admin_cannot_self_escalate(self):
        """functional_admin cannot assign a restricted role to themselves."""
        with self.assertRaises(AccessError):
            self.env["res.users.role.line"].with_user(self.fa_user).create(
                {
                    "role_id": self.restricted_role.id,
                    "user_id": self.fa_user.id,
                }
            )

    def test_functional_admin_can_assign_safe_role(self):
        """functional_admin can assign roles that don't include elevated privileges."""
        line = (
            self.env["res.users.role.line"]
            .with_user(self.fa_user)
            .create(
                {
                    "role_id": self.safe_role.id,
                    "user_id": self.target_user.id,
                }
            )
        )
        self.assertTrue(line.id)

    def test_functional_admin_cannot_update_role_line_to_restricted(self):
        line = self.env["res.users.role.line"].create(
            {
                "role_id": self.safe_role.id,
                "user_id": self.target_user.id,
            }
        )
        with self.assertRaises(AccessError):
            line.with_user(self.fa_user).write({"role_id": self.restricted_role.id})

    def test_sysadmin_can_assign_restricted_role(self):
        line = self.env["res.users.role.line"].create(
            {
                "role_id": self.restricted_role.id,
                "user_id": self.target_user.id,
            }
        )
        self.assertTrue(line.id)

    def test_role_with_functional_admin_as_group_id_is_blocked(self):
        """Assigning a role whose group_id IS functional_admin is also blocked."""
        fa_direct_role = self.env["res.users.role"].create(
            {
                "name": "Test FA Direct Role",
                "group_id": self.functional_admin_group.id,
            }
        )
        with self.assertRaises(AccessError):
            self.env["res.users.role.line"].with_user(self.fa_user).create(
                {
                    "role_id": fa_direct_role.id,
                    "user_id": self.target_user.id,
                }
            )
