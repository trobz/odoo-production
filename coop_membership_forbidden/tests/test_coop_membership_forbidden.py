from odoo.tests import common


class TestCoopMembershipForbidden(common.TransactionCase):
    """Test for Coop Membership Forbidden module."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Partner = cls.env["res.partner"]

    def test_is_forbidden_field_exists(self):
        """Test that is_forbidden field exists on partner."""
        partner = self.Partner.create(
            {
                "name": "Test Partner",
                "email": "test@example.com",
            }
        )
        self.assertTrue(hasattr(partner, "is_forbidden"))

    def test_forbidden_member_working_state(self):
        """Test that forbidden member has blocked working state."""
        partner = self.Partner.create(
            {
                "name": "Test Forbidden Member",
                "email": "test_forbidden@example.com",
                "is_forbidden": True,
            }
        )
        self.assertEqual(partner.working_state, "blocked")

    def test_non_forbidden_member_working_state(self):
        """Test that non-forbidden member does not have blocked working state."""
        partner = self.Partner.create(
            {
                "name": "Test Normal Member",
                "email": "test_normal@example.com",
                "is_forbidden": False,
            }
        )
        self.assertNotEqual(partner.working_state, "blocked")

    def test_onchange_is_forbidden_regular_user(self):
        """Test that regular user cannot set is_forbidden."""
        partner = self.Partner.create(
            {
                "name": "Test Partner",
                "email": "test@example.com",
            }
        )
        partner.is_forbidden = True
        partner._onchange_is_forbidden()
        self.assertFalse(partner.is_forbidden)

    def test_onchange_is_forbidden_manager(self):
        """Test that manager can set is_forbidden."""
        group = self.env.ref("coop_membership_forbidden.group_member_forbidden_manager")
        self.env.user.groups_id |= group
        partner = self.Partner.create(
            {
                "name": "Test Partner Manager",
                "email": "test_manager@example.com",
            }
        )
        partner.is_forbidden = True
        partner._onchange_is_forbidden()
        self.assertTrue(partner.is_forbidden)
