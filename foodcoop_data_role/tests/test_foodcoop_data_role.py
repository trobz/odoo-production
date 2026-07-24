from odoo.tests.common import TransactionCase


class TestFoodcoopDataRole(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group_cashier = cls.env.ref("foodcoop_data_role.group_Cashier")
        cls.group_member_manager = cls.env.ref(
            "foodcoop_data_role.group_Member_Manager"
        )
        cls.group_accountant = cls.env.ref("foodcoop_data_role.group_Accountant")
        cls.group_foodcoop_admin = cls.env.ref(
            "foodcoop_data_role.group_Foodcoop_Admin"
        )
        cls.group_member_accountant_restrict = cls.env.ref(
            "foodcoop_data_role.group_member_accountant_restrict"
        )
        cls.role_cashier = cls.env.ref("foodcoop_data_role.res_users_role_Cashier")
        cls.role_member_manager = cls.env.ref(
            "foodcoop_data_role.res_users_role_Member_Manager"
        )
        cls.role_foodcoop_admin = cls.env.ref(
            "foodcoop_data_role.res_users_role_Foodcoop_Admin"
        )

    def test_group_creation(self):
        self.assertTrue(self.group_cashier.exists())
        self.assertTrue(self.group_member_manager.exists())
        self.assertTrue(self.group_accountant.exists())
        self.assertTrue(self.group_foodcoop_admin.exists())
        self.assertTrue(self.group_member_accountant_restrict.exists())

    def test_role_creation(self):
        self.assertTrue(self.role_cashier.exists())
        self.assertTrue(self.role_member_manager.exists())
        self.assertTrue(self.role_foodcoop_admin.exists())

    def test_role_implied_ids(self):
        self.assertIn(
            self.env.ref("base.group_user"),
            self.role_cashier.implied_ids,
        )
        self.assertIn(
            self.env.ref("point_of_sale.group_pos_user"),
            self.role_cashier.implied_ids,
        )

    def test_user_with_role(self):
        test_user = self.env["res.users"].create(
            {
                "name": "Test User",
                "login": "test_user_foodcoop",
                "email": "test_user_foodcoop@example.com",
            }
        )
        self.env["res.users.role.line"].create(
            {
                "user_id": test_user.id,
                "role_id": self.role_cashier.id,
            }
        )
        self.assertIn(
            self.env.ref("base.group_user"),
            test_user.groups_id,
        )

    def test_pos_session_get_views_method(self):
        pos_session_model = self.env["pos.session"]
        result = pos_session_model.get_views([[False, "form"]], {"toolbar": True})
        self.assertIn("views", result)
        self.assertIn("models", result)

    def test_account_move_get_views_method(self):
        account_move_model = self.env["account.move"]
        result = account_move_model.get_views([[False, "form"]], {"toolbar": True})
        self.assertIn("views", result)
        self.assertIn("models", result)

    def test_check_access_ui_super_groups(self):
        test_user = self.env["res.users"].create(
            {
                "name": "Test Access User",
                "login": "test_access_user_foodcoop",
                "email": "test_access_user_foodcoop@example.com",
            }
        )
        resp = {"result": "saisie_group_partner", "actionMenuItems": False}
        resp = test_user.with_user(test_user).check_access_ui_super_groups(resp)
        self.assertTrue(resp.get("actionMenuItems"))

    def test_group_restrict_category(self):
        self.assertEqual(
            self.group_member_accountant_restrict.category_id,
            self.env.ref("base.module_category_hidden"),
        )
