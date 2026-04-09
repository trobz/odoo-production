from odoo.tests import Form, common


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

    def test_onchange_is_forbidden_manager(self):
        """Test that manager can set is_forbidden."""
        forbidden_manager = "coop_membership_forbidden.group_member_forbidden_manager"
        group = self.env.ref(forbidden_manager)
        self.env.user.groups_id |= group
        self.assertTrue(self.env.user.has_group(forbidden_manager))
        form = Form(
            self.Partner.with_user(self.env.user),
            view="coop_membership_forbidden.personal_information_inherit",
        )
        form.name = "Test Partner"
        form.email = "test@example.com"
        form.is_forbidden = True
        self.assertTrue(form.is_forbidden)
        partner = form.save()
        self.assertTrue(partner.is_forbidden)
        self.assertEqual(partner.working_state, "blocked")
        self.assertRegex(
            partner.error_message,
            "Interdit d'entrer dans le magasin. Veuillez contacter un salarié",
        )
