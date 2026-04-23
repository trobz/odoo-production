from odoo.tests import TransactionCase


class TestCoopMassMailingContact(TransactionCase):
    """Test automatic synchronization between mailing lists and cooperative members."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.MailingList = cls.env["mailing.list"]
        cls.MailingContact = cls.env["mailing.contact"]
        cls.ResPartner = cls.env["res.partner"]

        cls.member_list = cls.MailingList.create(
            {"name": "Member Newsletter", "is_member_contact": True}
        )
        cls.regular_list = cls.MailingList.create(
            {"name": "Regular Newsletter", "is_member_contact": False}
        )

    def _set_is_member(self, partner, value):
        self.env.flush_all()
        self.env.cr.execute(
            "UPDATE res_partner SET is_member = %s WHERE id = %s",
            [value, partner.id],
        )

    def _create_partner(self, name, email, is_member=False):
        partner = self.ResPartner.create({"name": name, "email": email})
        self._set_is_member(partner, is_member)
        return partner

    def _create_subscribed_contact(self, mailing_list, email, name="Test Contact"):
        return self.MailingContact.create(
            {
                "name": name,
                "email": email,
                "subscription_ids": [
                    (0, 0, {"list_id": mailing_list.id, "opt_out": False})
                ],
            }
        )

    def _subscription_exists(self, contact, mailing_list):
        return bool(
            self.env["mailing.subscription"].search_count(
                [("contact_id", "=", contact.id), ("list_id", "=", mailing_list.id)]
            )
        )

    # -------------------------------------------------------------------------
    # add_contacts
    # -------------------------------------------------------------------------

    def test_add_contacts_creates_contact_for_member(self):
        """add_contacts() creates a mailing.contact for a member without one."""
        self._create_partner("Alice Member", "alice.member@example.com", is_member=True)
        self.member_list.add_contacts()

        contact = self.MailingContact.search(
            [("email", "=", "alice.member@example.com")]
        )
        self.assertEqual(len(contact), 1)
        self.assertTrue(contact.is_member_contact)
        self.assertIn(self.member_list, contact.subscription_ids.mapped("list_id"))

    def test_add_contacts_skips_non_member(self):
        """add_contacts() does not create a contact for a non-member partner."""
        self._create_partner(
            "Bob NonMember", "bob.nonmember@example.com", is_member=False
        )
        self.member_list.add_contacts()
        self.assertEqual(
            self.MailingContact.search_count(
                [("email", "=", "bob.nonmember@example.com")]
            ),
            0,
        )

    def test_add_contacts_skips_existing_contact(self):
        """add_contacts() does not create a duplicate when a contact already exists."""
        partner = self._create_partner(
            "Carol Existing", "carol.existing@example.com", is_member=True
        )
        self.MailingContact.create({"name": partner.name, "email": partner.email})
        self.member_list.add_contacts()
        self.assertEqual(
            self.MailingContact.search_count([("email", "=", partner.email)]), 1
        )

    def test_add_contacts_respects_limit(self):
        """add_contacts(limit=N) processes at most N members per call."""
        partners = self.ResPartner.create(
            [
                {"name": f"LimitMember {i}", "email": f"limit.member{i}@example.com"}
                for i in range(5)
            ]
        )
        self.env.flush_all()
        self.env.cr.execute(
            "UPDATE res_partner SET is_member = TRUE WHERE id IN %s",
            [tuple(partners.ids)],
        )
        limited_list = self.MailingList.create(
            {"name": "Limited List", "is_member_contact": True}
        )
        limited_list.add_contacts(limit=2)
        count = self.env["mailing.subscription"].search_count(
            [("list_id", "=", limited_list.id)]
        )
        self.assertGreater(count, 0)
        self.assertLessEqual(count, 2)

    def test_add_contacts_subscribes_to_all_lists_in_recordset(self):
        """add_contacts() on multiple lists subscribes the contact to each list."""
        partner = self._create_partner(
            "Dave Multi", "dave.multi@example.com", is_member=True
        )
        list_a = self.MailingList.create({"name": "List A", "is_member_contact": True})
        list_b = self.MailingList.create({"name": "List B", "is_member_contact": True})
        (list_a | list_b).add_contacts()

        contact = self.MailingContact.search([("email", "=", partner.email)])
        subscribed = contact.subscription_ids.mapped("list_id")
        self.assertIn(list_a, subscribed)
        self.assertIn(list_b, subscribed)

    def test_add_contacts_on_empty_recordset_does_nothing(self):
        """add_contacts() on an empty recordset returns without error."""
        self.MailingList.browse([]).add_contacts()

    # -------------------------------------------------------------------------
    # remove_contacts
    # -------------------------------------------------------------------------

    def test_remove_contacts_removes_subscription_of_non_member(self):
        """remove_contacts() deletes subscriptions for non-members."""
        partner = self._create_partner(
            "Eve Former", "eve.former@example.com", is_member=False
        )
        contact = self._create_subscribed_contact(
            self.member_list, partner.email, partner.name
        )
        self.member_list.remove_contacts()
        self.assertFalse(self._subscription_exists(contact, self.member_list))

    def test_remove_contacts_keeps_subscription_of_active_member(self):
        """remove_contacts() does not touch subscriptions of active members."""
        partner = self._create_partner(
            "Frank Active", "frank.active@example.com", is_member=True
        )
        contact = self._create_subscribed_contact(
            self.member_list, partner.email, partner.name
        )
        self.member_list.remove_contacts()
        self.assertTrue(self._subscription_exists(contact, self.member_list))

    def test_remove_contacts_on_empty_recordset_does_nothing(self):
        """remove_contacts() on an empty recordset returns without error."""
        self.MailingList.browse([]).remove_contacts()

    def test_remove_contacts_only_targets_given_lists(self):
        """remove_contacts() only removes subscriptions in the called lists."""
        partner = self._create_partner(
            "Grace Scope", "grace.scope@example.com", is_member=False
        )
        other_list = self.MailingList.create(
            {"name": "Other List", "is_member_contact": True}
        )
        contact = self._create_subscribed_contact(
            other_list, partner.email, partner.name
        )
        self.member_list.remove_contacts()
        self.assertTrue(
            self._subscription_exists(contact, other_list),
            "Subscription in other_list must not be removed",
        )

    def test_remove_contacts_handles_same_email_multiple_partners(self):
        """Keep subscription when partners share an email and one is still a member."""
        shared_email = "shared.multi@example.com"
        p1 = self._create_partner("Shared P1", shared_email, is_member=True)
        p2 = self._create_partner("Shared P2", shared_email, is_member=False)
        self.assertNotEqual(p1, p2)
        contact = self._create_subscribed_contact(
            self.member_list, shared_email, "Shared Contact"
        )
        self.member_list.remove_contacts()
        self.assertTrue(
            self._subscription_exists(contact, self.member_list),
            "Subscription must be kept when one partner with that email is a member",
        )

    # -------------------------------------------------------------------------
    # compute_contacts
    # -------------------------------------------------------------------------

    def test_compute_contacts_adds_and_removes(self):
        """compute_contacts() adds new members and removes ex-members in one call."""
        compute_list = self.MailingList.create(
            {"name": "Compute List", "is_member_contact": True}
        )
        new_member = self._create_partner(
            "Henry New", "henry.new@example.com", is_member=True
        )
        ex_partner = self._create_partner(
            "Iris Ex", "iris.ex@example.com", is_member=False
        )
        ex_contact = self._create_subscribed_contact(
            compute_list, ex_partner.email, ex_partner.name
        )
        compute_list.compute_contacts()

        new_contact = self.MailingContact.search([("email", "=", new_member.email)])
        self.assertTrue(new_contact)
        self.assertIn(compute_list, new_contact.subscription_ids.mapped("list_id"))
        self.assertFalse(self._subscription_exists(ex_contact, compute_list))

    # -------------------------------------------------------------------------
    # cron_compute_contact
    # -------------------------------------------------------------------------

    def test_cron_only_processes_member_contact_lists(self):
        """cron_compute_contact() syncs only lists where is_member_contact=True."""
        partner = self._create_partner(
            "Jake Cron", "jake.cron@example.com", is_member=True
        )
        self.MailingList.cron_compute_contact()

        contact = self.MailingContact.search([("email", "=", partner.email)])
        self.assertTrue(contact, "Cron must create a contact for the member")
        subscribed = contact.subscription_ids.mapped("list_id")
        self.assertIn(self.member_list, subscribed)
        self.assertNotIn(self.regular_list, subscribed)

    def test_cron_skips_non_member_contact_lists(self):
        """cron_compute_contact() leaves non-member-contact lists untouched."""
        partner = self._create_partner(
            "Karen Skip", "karen.skip@example.com", is_member=True
        )
        self.MailingList.cron_compute_contact()

        contact = self.MailingContact.search([("email", "=", partner.email)])
        self.assertTrue(contact)
        self.assertFalse(
            self._subscription_exists(contact, self.regular_list),
            "regular_list must not receive cron-generated contacts",
        )
