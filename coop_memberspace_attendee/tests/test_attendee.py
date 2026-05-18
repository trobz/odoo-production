"""
Tests for coop_memberspace_attendee.

Covers:
- shift.shift.get_expected_attendee(): returns member names filtered by
  registration state (draft/open/replacing included; cancel excluded).
- res.users.ftop_get_shift() override: adds seats_reserved to each shift dict
  returned by the parent.
"""

from datetime import timedelta
from unittest.mock import patch

from odoo import fields

from odoo.addons.coop_memberspace.tests.common import MemberspaceCommon

_REG_CTX = {
    "creation_in_progress": True,
    "ignore_checking_attendance": True,
}


def _create_shift(env, template, shift_type_ref, days_ahead=5):
    future = fields.Datetime.now() + timedelta(days=days_ahead)
    shift = env["shift.shift"].create(
        {
            "name": template.name,
            "shift_template_id": template.id,
            "date_begin": future,
            "date_end": future + timedelta(hours=3),
            "shift_type_id": env.ref(shift_type_ref).id,
        }
    )
    shift.button_confirm()
    shift.shift_mail_ids.unlink()
    return shift


def _register(env, shift, partner):
    ticket = shift.shift_ticket_ids[:1]
    return (
        env["shift.registration"]
        .with_context(**_REG_CTX)
        .create(
            {
                "partner_id": partner.id,
                "shift_id": shift.id,
                "shift_ticket_id": ticket.id,
            }
        )
    )


class TestGetExpectedAttendee(MemberspaceCommon):
    """shift.shift.get_expected_attendee() returns names of active registrations."""

    def _shift(self):
        return _create_shift(self.env, self.template_standard, "coop_shift.shift_type")

    def test_returns_list(self):
        self.assertIsInstance(self._shift().get_expected_attendee(), list)

    def test_empty_when_no_registrations(self):
        self.assertEqual(self._shift().get_expected_attendee(), [])

    def test_includes_open_registration(self):
        shift = self._shift()
        _register(self.env, shift, self.partner_a)
        self.assertIn(self.partner_a.name, shift.get_expected_attendee())

    def test_includes_draft_registration(self):
        shift = self._shift()
        reg = _register(self.env, shift, self.partner_a)
        reg.write({"state": "draft"})
        self.assertIn(self.partner_a.name, shift.get_expected_attendee())

    def test_includes_replacing_registration(self):
        shift = self._shift()
        reg = _register(self.env, shift, self.partner_a)
        reg.write({"state": "replacing"})
        self.assertIn(self.partner_a.name, shift.get_expected_attendee())

    def test_excludes_cancelled_registration(self):
        shift = self._shift()
        reg = _register(self.env, shift, self.partner_a)
        reg.button_reg_cancel()
        self.assertNotIn(self.partner_a.name, shift.get_expected_attendee())

    def test_multiple_active_registrations(self):
        shift = self._shift()
        _register(self.env, shift, self.partner_a)
        _register(self.env, shift, self.partner_b)
        names = shift.get_expected_attendee()
        self.assertIn(self.partner_a.name, names)
        self.assertIn(self.partner_b.name, names)
        self.assertEqual(len(names), 2)

    def test_cancelled_excluded_from_mixed_registrations(self):
        """Only the non-cancelled registration appears when one is cancelled."""
        shift = self._shift()
        _register(self.env, shift, self.partner_a)
        reg_b = _register(self.env, shift, self.partner_b)
        reg_b.button_reg_cancel()
        names = shift.get_expected_attendee()
        self.assertEqual(len(names), 1)
        self.assertIn(self.partner_a.name, names)
        self.assertNotIn(self.partner_b.name, names)


class TestFtopGetShiftSeatsReserved(MemberspaceCommon):
    """res.users.ftop_get_shift() override adds seats_reserved to each dict."""

    @classmethod
    def _parent_cls(cls):
        """Return the coop_memberspace ResUsers partial class.

        This is what super() inside the attendee override resolves to,
        so patching it lets us test the override in isolation.
        """
        import odoo.addons.coop_memberspace.models.res_users as _cm

        return _cm.ResUsers

    def _shift(self):
        return _create_shift(self.env, self.template_standard, "coop_shift.shift_type")

    def test_seats_reserved_key_present(self):
        """seats_reserved key is added to every shift dict."""
        shift = self._shift()
        with patch.object(
            self._parent_cls(), "ftop_get_shift", return_value=[{"id": shift.id}]
        ):
            result = self.env["res.users"].ftop_get_shift()
        self.assertIn("seats_reserved", result[0])

    def test_seats_reserved_matches_actual_value(self):
        """seats_reserved equals shift.seats_reserved after a registration."""
        shift = self._shift()
        _register(self.env, shift, self.partner_a)
        expected = shift.seats_reserved
        with patch.object(
            self._parent_cls(), "ftop_get_shift", return_value=[{"id": shift.id}]
        ):
            result = self.env["res.users"].ftop_get_shift()
        self.assertEqual(result[0]["seats_reserved"], expected)

    def test_seats_reserved_zero_when_no_registrations(self):
        """seats_reserved is 0 for a shift with no registrations."""
        shift = self._shift()
        with patch.object(
            self._parent_cls(), "ftop_get_shift", return_value=[{"id": shift.id}]
        ):
            result = self.env["res.users"].ftop_get_shift()
        self.assertEqual(result[0]["seats_reserved"], 0)

    def test_empty_parent_result_unchanged(self):
        """When parent returns [], the override returns [] too."""
        with patch.object(self._parent_cls(), "ftop_get_shift", return_value=[]):
            result = self.env["res.users"].ftop_get_shift()
        self.assertEqual(result, [])

    def test_parent_keys_preserved(self):
        """The override must not discard keys added by the parent."""
        shift = self._shift()
        parent_data = [{"id": shift.id, "week_name": "Week 5", "seats_avail": 3}]
        with patch.object(
            self._parent_cls(), "ftop_get_shift", return_value=parent_data
        ):
            result = self.env["res.users"].ftop_get_shift()
        self.assertIn("week_name", result[0])
        self.assertIn("seats_avail", result[0])
        self.assertIn("seats_reserved", result[0])

    def test_multiple_shifts_all_enriched(self):
        """seats_reserved is added to every shift in the list, not just the first."""
        shift_1 = _create_shift(
            self.env, self.template_standard, "coop_shift.shift_type", days_ahead=5
        )
        shift_2 = _create_shift(
            self.env, self.template_standard, "coop_shift.shift_type", days_ahead=6
        )
        _register(self.env, shift_1, self.partner_a)
        parent_data = [{"id": shift_1.id}, {"id": shift_2.id}]
        with patch.object(
            self._parent_cls(), "ftop_get_shift", return_value=parent_data
        ):
            result = self.env["res.users"].ftop_get_shift()
        self.assertIn("seats_reserved", result[0])
        self.assertIn("seats_reserved", result[1])
        self.assertEqual(result[0]["seats_reserved"], shift_1.seats_reserved)
        self.assertEqual(result[1]["seats_reserved"], shift_2.seats_reserved)
