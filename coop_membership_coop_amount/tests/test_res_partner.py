from odoo.tests import common


class TestResPartnerCoopAmount(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Partner = cls.env["res.partner"]
        cls.AccountMove = cls.env["account.move"]
        cls.AccountMoveLine = cls.env["account.move.line"]
        cls.Category = cls.env["capital.fundraising.category"]

    def test_get_fundraising_item_domain_with_categories(self):
        """Test domain returns correct filter when categories exist"""
        partner = self.Partner.create({"name": "Test Partner"})
        domain = partner._get_fundraising_item_domain()
        self.assertIn("move_id.state", str(domain))
        self.assertIn("account_id", str(domain))

    def test_coop_amount_compute(self):
        """Test coop_amount compute method returns 0 when no journal items"""
        partner = self.Partner.create({"name": "Test Partner"})
        partner._compute_coop_amount()
        self.assertEqual(partner.coop_amount, 0)

    def test_fundraising_invoice_ids_field_exists(self):
        """Test fundraising_invoice_ids field exists on partner"""
        partner = self.Partner.create({"name": "Test Partner"})
        self.assertTrue(hasattr(partner, "fundraising_invoice_ids"))

    def test_fundraising_journal_item_ids_field_exists(self):
        """Test fundraising_journal_item_ids field exists on partner"""
        partner = self.Partner.create({"name": "Test Partner"})
        self.assertTrue(hasattr(partner, "fundraising_journal_item_ids"))

    def test_coop_amount_field_exists(self):
        """Test coop_amount field exists on partner"""
        partner = self.Partner.create({"name": "Test Partner"})
        self.assertTrue(hasattr(partner, "coop_amount"))

    def test_amount_subscription_field_exists(self):
        """Test amount_subscription field exists on partner"""
        partner = self.Partner.create({"name": "Test Partner"})
        self.assertTrue(hasattr(partner, "amount_subscription"))
