from odoo.tests import common


class TestEmailValidation(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ResPartner = cls.env["res.partner"]

    def test_email_validation_string(self):
        """Test email validation string generation"""
        partner = self.ResPartner.create(
            {
                "name": "Test Partner",
                "email": "test@example.com",
            }
        )
        self.assertTrue(partner.email_validation_string)

    def test_check_email_validation_string(self):
        """Test email validation with correct string"""
        partner = self.ResPartner.create(
            {
                "name": "Test Partner",
                "email": "test@example.com",
            }
        )
        result = partner.check_email_validation_string(partner.email_validation_string)
        self.assertTrue(result)
        self.assertTrue(partner.is_checked_email)
        self.assertFalse(partner.show_send_email)

    def test_check_email_validation_string_wrong(self):
        """Test email validation with wrong string"""
        partner = self.ResPartner.create(
            {
                "name": "Test Partner",
                "email": "test@example.com",
            }
        )
        result = partner.check_email_validation_string("wrong_string")
        self.assertFalse(result)
        self.assertFalse(partner.is_checked_email)

    def test_recompute_hash_confirm_email(self):
        """Test recompute hash and send email"""
        partner = self.ResPartner.create(
            {
                "name": "Test Partner",
                "email": "test@example.com",
                "is_checked_email": True,
            }
        )
        old_string = partner.email_validation_string
        partner.recompute_hash_confirm_email()
        self.assertNotEqual(partner.email_validation_string, old_string)
