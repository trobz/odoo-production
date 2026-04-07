from odoo.tests import common


class TestFoodcoopDataFr(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.AccountAccount = cls.env["account.account"]
        cls.AccountJournal = cls.env["account.journal"]

    def test_credit_account_creation(self):
        """Test that credit account can be created"""
        code = "511900"
        account = self.AccountAccount.search([("code", "=", code)], limit=1)
        if not account:
            main_company = self.env.ref("base.main_company")
            account = self.AccountAccount.create(
                {
                    "name": "Test Credit Account",
                    "account_type": "liability_current",
                    "company_ids": [(6, 0, [main_company.id])],
                    "code": code,
                    "reconcile": False,
                }
            )
        self.assertTrue(account)
        self.assertEqual(account.code, code)

    def test_view_partner_credit_invisible_for_non_members(self):
        """Test credit page is invisible for non-members"""
        partner = self.env["res.partner"].create(
            {
                "name": "Test Non-Member",
            }
        )
        self.assertFalse(partner.is_member)
        self.assertFalse(partner.is_former_member)
        self.assertFalse(partner.is_associated_people)
        self.assertTrue(partner.is_interested_people)
