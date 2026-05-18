"""Unit tests for coop_memberspace_cancelation."""

from datetime import timedelta
from unittest.mock import patch

from odoo import fields
from odoo.tests import tagged

from odoo.addons.coop_memberspace.tests.common import MemberspaceCommon


@tagged("post_install", "-at_install")
class TestCheckCancelable(MemberspaceCommon):
    """Tests for check_shift_regis_cancelable validation."""

    def test_open_registration_is_cancelable(self):
        self.assertTrue(self.reg_a.check_shift_regis_cancelable())

    def test_waiting_registration_is_not_cancelable(self):
        self.reg_a.write({"state": "waiting"})
        self.assertFalse(self.reg_a.check_shift_regis_cancelable())

    def test_cancelled_registration_is_not_cancelable(self):
        self.reg_a.write({"state": "cancel"})
        self.assertFalse(self.reg_a.check_shift_regis_cancelable())


@tagged("post_install", "-at_install")
class TestCancelFromMarket(MemberspaceCommon):
    """Tests for cancel_shift_regis_from_market."""

    def _cancel_with_mocked_email(self, reg):
        MailTemplate = type(self.env["mail.template"])
        with patch.object(MailTemplate, "send_mail", return_value=None):
            return reg.cancel_shift_regis_from_market()

    def test_returns_success_for_open_registration(self):
        result, msg = self._cancel_with_mocked_email(self.reg_a)
        self.assertEqual(result, 1)
        self.assertEqual(msg, "")

    def test_open_registration_state_becomes_cancel(self):
        self._cancel_with_mocked_email(self.reg_a)
        self.assertEqual(self.reg_a.state, "cancel")

    def test_returns_failure_for_waiting_registration(self):
        self.reg_a.write({"state": "waiting"})
        result, msg = self.reg_a.cancel_shift_regis_from_market()
        self.assertEqual(result, 0)

    def test_waiting_state_is_unchanged_after_failed_cancel(self):
        self.reg_a.write({"state": "waiting"})
        self.reg_a.cancel_shift_regis_from_market()
        self.assertEqual(self.reg_a.state, "waiting")

    def test_returns_failure_for_already_cancelled_registration(self):
        self.reg_a.write({"state": "cancel"})
        result, msg = self.reg_a.cancel_shift_regis_from_market()
        self.assertEqual(result, 0)

    def test_email_is_sent_on_successful_cancel(self):
        MailTemplate = type(self.env["mail.template"])
        with patch.object(MailTemplate, "send_mail", return_value=None) as mock_send:
            self.reg_a.cancel_shift_regis_from_market()
        mock_send.assert_called_once_with(self.reg_a.id)

    def test_no_email_sent_when_not_cancelable(self):
        self.reg_a.write({"state": "waiting"})
        MailTemplate = type(self.env["mail.template"])
        with patch.object(MailTemplate, "send_mail", return_value=None) as mock_send:
            self.reg_a.cancel_shift_regis_from_market()
        mock_send.assert_not_called()


@tagged("post_install", "-at_install")
class TestGetUpcoming(MemberspaceCommon):
    """Tests for get_upcoming model method."""

    def test_returns_future_registration_for_partner(self):
        upcoming = self.env["shift.registration"].get_upcoming(self.partner_a)
        self.assertIn(self.reg_a, upcoming)

    def test_excludes_other_partner_registrations(self):
        upcoming = self.env["shift.registration"].get_upcoming(self.partner_a)
        self.assertNotIn(self.reg_b, upcoming)

    def test_includes_cancelled_registrations(self):
        self.reg_a.write({"state": "cancel"})
        upcoming = self.env["shift.registration"].get_upcoming(self.partner_a)
        self.assertIn(self.reg_a, upcoming)

    def test_excludes_past_registrations(self):
        past = fields.Datetime.now() - timedelta(days=2)
        self.shift_a.write({"date_begin": past, "date_end": past + timedelta(hours=3)})
        upcoming = self.env["shift.registration"].get_upcoming(self.partner_a)
        self.assertNotIn(self.reg_a, upcoming)

    def test_additional_domain_args_are_applied(self):
        # reg_a is "open", so filtering for "cancel" should exclude it
        upcoming = self.env["shift.registration"].get_upcoming(
            self.partner_a,
            args=[("state", "=", "cancel")],
        )
        self.assertNotIn(self.reg_a, upcoming)

    def test_results_ordered_by_date_begin(self):
        # Both partner_a registrations: reg_a (shift_a, 7 days) and
        # a second registration on shift_b (14 days)
        upcoming = self.env["shift.registration"].get_upcoming(self.partner_a)
        dates = upcoming.mapped("date_begin")
        self.assertEqual(dates, sorted(dates))


@tagged("post_install", "-at_install")
class TestButtonDoneMalusPoints(MemberspaceCommon):
    """Tests for shift.shift.button_done malus point creation.

    Each test creates its own dedicated shift to avoid conflicts with the
    class-level fixtures (reg_a uses whichever ticket comes first from
    shift_a, which may be FTOP, not standard).
    """

    # Name set by coop_memberspace_cancelation on malus events.
    # coop_membership uses "Shift Cloture" — this lets us distinguish them.
    MALUS_EVENT_NAME = "Annuler votre participation"

    def _make_shift_with_cancelled_reg(self, shift_type="standard"):
        """Return (shift, reg) — reg is already in 'cancel' state."""
        future = fields.Datetime.now() + timedelta(days=3)
        if shift_type == "standard":
            template = self.template_standard
            shift_type_ref = self.env.ref("coop_shift.shift_type")
        else:
            template = self.template_ftop
            shift_type_ref = self.env.ref("coop_shift.shift_type_ftop")

        shift = self.env["shift.shift"].create(
            {
                "name": template.name,
                "shift_template_id": template.id,
                "date_begin": future,
                "date_end": future + timedelta(hours=3),
                "shift_type_id": shift_type_ref.id,
            }
        )
        shift.button_confirm()
        shift.shift_mail_ids.unlink()

        # Explicitly pick the ticket matching the requested shift_type so we
        # are not at the mercy of ticket ordering on the template.
        ticket = shift.shift_ticket_ids.filtered(lambda t: t.shift_type == shift_type)[
            :1
        ]
        reg = (
            self.env["shift.registration"]
            .with_context(
                creation_in_progress=True,
                ignore_checking_attendance=True,
            )
            .create(
                {
                    "partner_id": self.partner_b.id,
                    "shift_id": shift.id,
                    "shift_ticket_id": ticket.id,
                }
            )
        )
        reg.write({"state": "cancel"})
        return shift, reg

    def _our_malus_events(self, partner, shift):
        """Malus events created specifically by coop_memberspace_cancelation."""
        return self.env["shift.counter.event"].search(
            [
                ("partner_id", "=", partner.id),
                ("shift_id", "=", shift.id),
                ("name", "=", self.MALUS_EVENT_NAME),
            ]
        )

    def test_cancelled_standard_reg_creates_standard_malus_event(self):
        shift, _reg = self._make_shift_with_cancelled_reg("standard")
        self.assertLessEqual(self.partner_b.final_ftop_point, 0)

        shift.button_done()

        events = self._our_malus_events(self.partner_b, shift)
        self.assertEqual(len(events), 1)
        self.assertEqual(events.point_qty, -1)
        self.assertEqual(events.type, "standard")
        self.assertFalse(events.is_manual)

    def test_cancelled_standard_reg_with_ftop_balance_creates_ftop_event(self):
        shift, _reg = self._make_shift_with_cancelled_reg("standard")
        self.env["shift.counter.event"].with_context(automatic=True).create(
            {
                "name": "Test FTOP credit",
                "type": "ftop",
                "partner_id": self.partner_b.id,
                "point_qty": 2,
            }
        )
        self.assertGreater(self.partner_b.final_ftop_point, 0)

        shift.button_done()

        events = self._our_malus_events(self.partner_b, shift)
        self.assertEqual(len(events), 1)
        self.assertEqual(events.point_qty, -1)
        self.assertEqual(events.type, "ftop")
        self.assertFalse(events.is_manual)

    def test_non_cancelled_registration_creates_no_malus_event(self):
        # Use "excused" instead of "open" so button_done() is not blocked by
        # the coop_membership attendance check (which blocks "draft"/"open").
        shift, reg = self._make_shift_with_cancelled_reg("standard")
        reg.write({"state": "excused"})

        count_before = len(self._our_malus_events(self.partner_b, shift))
        shift.button_done()
        count_after = len(self._our_malus_events(self.partner_b, shift))

        self.assertEqual(count_before, count_after)

    def test_cancelled_ftop_registration_creates_no_malus_event(self):
        # coop_membership creates "Shift Cloture" events for FTOP shifts;
        # our module must NOT create "Annuler votre participation" events.
        shift_ftop, _reg = self._make_shift_with_cancelled_reg("ftop")

        count_before = len(self._our_malus_events(self.partner_b, shift_ftop))
        shift_ftop.button_done()
        count_after = len(self._our_malus_events(self.partner_b, shift_ftop))

        self.assertEqual(count_before, count_after)

    def test_malus_event_name_is_set(self):
        shift, _reg = self._make_shift_with_cancelled_reg("standard")
        shift.button_done()

        events = self._our_malus_events(self.partner_b, shift)
        self.assertTrue(events.name)

    def test_malus_event_links_to_shift(self):
        shift, _reg = self._make_shift_with_cancelled_reg("standard")
        shift.button_done()

        events = self._our_malus_events(self.partner_b, shift)
        self.assertEqual(events.shift_id, shift)
