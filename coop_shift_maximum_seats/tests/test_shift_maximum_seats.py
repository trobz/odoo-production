# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.tests import common


class TestShiftMaxAvailableSeats(common.TransactionCase):
    """Unit tests for the Maximum Available Seats policy."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        cls.company = cls.env.user.company_id
        cls.product_standard = cls.env.ref("coop_shift.product_product_shift_standard")
        cls.product_ftop = cls.env.ref("coop_shift.product_product_shift_ftop")
        cls.partner = cls.env.ref("coop_shift.standard_member_1")
        cls.template = cls.env.ref("coop_shift.standard_template_1")

    # ── helpers ──────────────────────────────────────────────────────────────

    def _make_shift(self, seats_max=10, mode="manual"):
        """Create a confirmed shift via wizard (respects name computed field).

        The shift gets one standard ticket from the template; a second FTOP
        ticket is added manually so two-ticket distribution tests are possible.
        """
        wiz = self.env["create.shifts.wizard"].create(
            {
                "date_from": fields.Date.today(),
                "date_to": fields.Date.today(),
                "template_ids": [(6, 0, [self.template.id])],
            }
        )
        wiz.create_shifts()
        shift = self.env["shift.shift"].search(
            [("shift_template_id", "=", self.template.id), ("state", "=", "draft")],
            order="id desc",
            limit=1,
        )
        # Add a second ticket so multi-ticket distribution is observable
        self.env["shift.ticket"].create(
            {
                "name": "FTOP",
                "shift_id": shift.id,
                "product_id": self.product_ftop.id,
                "seats_max": seats_max,
            }
        )
        shift.write(
            {
                "shift_max_available_seats": mode,
                "seats_availability": "limited",
                "seats_max": seats_max,
            }
        )
        shift.button_confirm()
        shift.shift_mail_ids.unlink()
        return shift

    def _make_registration(self, shift, ticket, partner=None):
        return (
            self.env["shift.registration"]
            .with_context(
                creation_in_progress=True,
                ignore_checking_attendance=True,
            )
            .create(
                {
                    "partner_id": (partner or self.partner).id,
                    "shift_id": shift.id,
                    "shift_ticket_id": ticket.id,
                }
            )
        )

    def _ticket(self, shift, shift_type):
        return shift.shift_ticket_ids.filtered(lambda t: t.shift_type == shift_type)[:1]

    # ── company policy ────────────────────────────────────────────────────────

    def test_company_default_is_manual(self):
        """Company defaults to manual mode."""
        self.assertEqual(self.company.shift_max_available_seats, "manual")

    def test_company_switch_to_auto_updates_existing_shifts(self):
        """Switching company to auto propagates to existing open shifts."""
        shift = self._make_shift(mode="manual")
        self.company.shift_max_available_seats = "auto"
        self.assertEqual(shift.shift_max_available_seats, "auto")
        self.assertEqual(shift.seats_availability, "limited")

    def test_company_switch_back_to_manual_updates_shifts(self):
        """Switching company back to manual propagates to existing shifts."""
        self.company.shift_max_available_seats = "auto"
        shift = self._make_shift(mode="auto")
        self.company.shift_max_available_seats = "manual"
        self.assertEqual(shift.shift_max_available_seats, "manual")

    def test_company_switch_to_auto_updates_existing_templates(self):
        """Switching company to auto propagates to existing templates."""
        self.template.shift_max_available_seats = "manual"
        self.company.shift_max_available_seats = "auto"
        self.assertEqual(self.template.shift_max_available_seats, "auto")
        self.assertEqual(self.template.seats_availability, "limited")

    # ── default_get ───────────────────────────────────────────────────────────

    def test_default_get_shift_manual_mode(self):
        """In manual mode, new shift defaults to unlimited availability."""
        self.company.write({"shift_max_available_seats": "manual"})
        defaults = self.env["shift.shift"].default_get(
            ["shift_max_available_seats", "seats_availability"]
        )
        self.assertEqual(defaults.get("shift_max_available_seats"), "manual")
        self.assertEqual(defaults.get("seats_availability"), "unlimited")

    def test_default_get_shift_auto_mode(self):
        """In auto mode, new shift defaults to limited availability."""
        self.company.write({"shift_max_available_seats": "auto"})
        defaults = self.env["shift.shift"].default_get(
            ["shift_max_available_seats", "seats_availability"]
        )
        self.assertEqual(defaults.get("shift_max_available_seats"), "auto")
        self.assertEqual(defaults.get("seats_availability"), "limited")

    def test_default_get_template_manual_mode(self):
        """In manual mode, new template defaults to unlimited availability."""
        self.company.write({"shift_max_available_seats": "manual"})
        defaults = self.env["shift.template"].default_get(
            ["shift_max_available_seats", "seats_availability"]
        )
        self.assertEqual(defaults.get("shift_max_available_seats"), "manual")
        self.assertEqual(defaults.get("seats_availability"), "unlimited")

    def test_default_get_template_auto_mode(self):
        """In auto mode, new template defaults to limited availability."""
        self.company.write({"shift_max_available_seats": "auto"})
        defaults = self.env["shift.template"].default_get(
            ["shift_max_available_seats", "seats_availability"]
        )
        self.assertEqual(defaults.get("shift_max_available_seats"), "auto")
        self.assertEqual(defaults.get("seats_availability"), "limited")

    # ── ticket seats_max calculation ──────────────────────────────────────────

    def test_auto_mode_initial_ticket_seats_max_equals_shift_seats_max(self):
        """Without registrations in auto mode, ticket.seats_max == shift.seats_max."""
        shift = self._make_shift(seats_max=10, mode="auto")
        shift._update_ticket_seats_max()
        for ticket in shift.shift_ticket_ids:
            self.assertEqual(ticket.seats_max, 10)

    def test_auto_mode_changing_seats_max_propagates_to_tickets(self):
        """Changing shift.seats_max in auto mode updates all ticket seats_max."""
        shift = self._make_shift(seats_max=10, mode="auto")
        shift.seats_max = 20
        for ticket in shift.shift_ticket_ids:
            self.assertEqual(ticket.seats_max, 20)

    def test_manual_mode_changing_seats_max_does_not_touch_tickets(self):
        "In manual mode, changing shift.seats_max leaves ticket seats_max unchanged."
        shift = self._make_shift(seats_max=10, mode="manual")
        ticket = self._ticket(shift, "standard")
        ticket.seats_max = 5
        shift.seats_max = 20
        self.assertEqual(ticket.seats_max, 5)

    # ── registration hooks ────────────────────────────────────────────────────

    def test_auto_mode_registration_create_recalculates_ticket_seats_max(self):
        """Creating a registration in auto mode recalculates ticket.seats_max.

        Formula: ticket.seats_max = shift.seats_max - total_reserved + own_reserved
        With 1 registration on standard (total_reserved=1):
          standard: 10 - 1 + 1 = 10
          ftop:     10 - 1 + 0 = 9
        """
        shift = self._make_shift(seats_max=10, mode="auto")
        ticket_std = self._ticket(shift, "standard")
        ticket_ftop = self._ticket(shift, "ftop")

        self._make_registration(shift, ticket_std)

        self.assertEqual(ticket_std.seats_max, 10)
        self.assertEqual(ticket_ftop.seats_max, 9)

    def test_auto_mode_registration_unlink_restores_ticket_seats_max(self):
        """Deleting a registration in auto mode restores ticket.seats_max."""
        shift = self._make_shift(seats_max=10, mode="auto")
        ticket_std = self._ticket(shift, "standard")
        ticket_ftop = self._ticket(shift, "ftop")

        reg = self._make_registration(shift, ticket_std)
        reg.unlink()

        self.assertEqual(ticket_std.seats_max, 10)
        self.assertEqual(ticket_ftop.seats_max, 10)

    def test_auto_mode_multiple_registrations_split_capacity(self):
        """Multiple registrations reduce each ticket's remaining capacity.

        2 registrations on standard, 1 on ftop (total_reserved=3):
          standard: 10 - 3 + 2 = 9
          ftop:     10 - 3 + 1 = 8
        """
        shift = self._make_shift(seats_max=10, mode="auto")
        ticket_std = self._ticket(shift, "standard")
        ticket_ftop = self._ticket(shift, "ftop")

        partner_2, partner_3 = self.env["res.partner"].create(
            [
                {"name": "Test Member 2", "shift_type": "standard"},
                {"name": "Test Member 3", "shift_type": "ftop"},
            ]
        )
        self._make_registration(shift, ticket_std)
        self._make_registration(shift, ticket_std, partner=partner_2)
        self._make_registration(shift, ticket_ftop, partner=partner_3)

        self.assertEqual(ticket_std.seats_max, 9)
        self.assertEqual(ticket_ftop.seats_max, 8)

    def test_manual_mode_registration_does_not_change_ticket_seats_max(self):
        """In manual mode, creating a registration leaves ticket.seats_max unchanged."""
        shift = self._make_shift(seats_max=10, mode="manual")
        ticket = self._ticket(shift, "standard")
        ticket.seats_max = 7

        self._make_registration(shift, ticket)

        self.assertEqual(ticket.seats_max, 7)

    # ── shift.template.ticket._check_propagated_seats ─────────────────────────

    def test_template_ticket_check_propagated_seats_always_false_in_auto_mode(self):
        """In auto mode, _check_propagated_seats always returns False."""
        self.template.shift_max_available_seats = "auto"
        for ticket in self.template.shift_ticket_ids:
            self.assertFalse(ticket._check_propagated_seats())

    def test_template_ticket_check_propagated_seats_manual_mode_returns_bool(self):
        """In manual mode, _check_propagated_seats delegates to parent logic."""
        self.template.shift_max_available_seats = "manual"
        for ticket in self.template.shift_ticket_ids:
            self.assertIsInstance(ticket._check_propagated_seats(), bool)

    # ── related fields ────────────────────────────────────────────────────────

    def test_shift_ticket_reflects_shift_mode(self):
        """shift.ticket.shift_max_available_seats mirrors shift.shift mode."""
        shift = self._make_shift(mode="auto")
        for ticket in shift.shift_ticket_ids:
            self.assertEqual(ticket.shift_max_available_seats, "auto")

    def test_shift_ticket_mode_updates_when_shift_mode_changes(self):
        """Changing shift mode is reflected on tickets via related field."""
        shift = self._make_shift(mode="manual")
        for ticket in shift.shift_ticket_ids:
            self.assertEqual(ticket.shift_max_available_seats, "manual")
        shift.shift_max_available_seats = "auto"
        for ticket in shift.shift_ticket_ids:
            self.assertEqual(ticket.shift_max_available_seats, "auto")

    def test_template_ticket_reflects_template_mode(self):
        """shift.template.ticket.shift_max_available_seats mirrors template mode."""
        self.template.shift_max_available_seats = "auto"
        for ticket in self.template.shift_ticket_ids:
            self.assertEqual(ticket.shift_max_available_seats, "auto")
