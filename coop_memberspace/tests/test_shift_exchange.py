"""
Tests for shift exchange market operations.

Covers:
- add_shift_regis_to_market / remove_shift_regis_from_market
- check_exchangable (time-window guard)
- get_upcoming filter logic
- get_extra_domain_on_market domain builder
"""

from datetime import timedelta

from odoo import fields

from .common import MemberspaceCommon


class TestCheckExchangable(MemberspaceCommon):
    """Time-window guard before allowing market placement."""

    def test_exchangable_when_far_enough(self):
        """Shift starting in 7 days is exchangeable (> 24h threshold)."""
        self.assertTrue(self.reg_a.check_exchangable())

    def test_not_exchangable_when_too_close(self):
        """Shift starting in 1 hour is NOT exchangeable."""
        soon = fields.Datetime.now() + timedelta(hours=1)
        self.shift_a.write({"date_begin": soon})
        self.assertFalse(self.reg_a.check_exchangable())

    def test_not_exchangable_when_in_past(self):
        """Past shift is not exchangeable."""
        past = fields.Datetime.now() - timedelta(hours=1)
        self.shift_a.write({"date_begin": past})
        self.assertFalse(self.reg_a.check_exchangable())

    def test_custom_duration_respected(self):
        """Config param shift_exchange_duration is respected."""
        # Set threshold to 200h → shift in 7 days (168h) is NOT exchangeable
        self.env["ir.config_parameter"].sudo().set_param(
            "coop.shift.shift_exchange_duration", "200"
        )
        self.assertFalse(self.reg_a.check_exchangable())
        # Reset
        self.env["ir.config_parameter"].sudo().set_param(
            "coop.shift.shift_exchange_duration", "24"
        )


class TestAddRemoveMarket(MemberspaceCommon):
    """Market placement and removal state transitions."""

    def test_add_to_market_sets_in_progress(self):
        result = self.reg_a.add_shift_regis_to_market()
        self.assertEqual(result["code"], 1)
        self.assertEqual(self.reg_a.exchange_state, "in_progress")

    def test_add_to_market_fails_too_close(self):
        soon = fields.Datetime.now() + timedelta(hours=1)
        self.shift_a.write({"date_begin": soon})
        result = self.reg_a.add_shift_regis_to_market()
        self.assertEqual(result["code"], 0)
        self.assertIn("msg", result)

    def test_remove_from_market_resets_to_draft(self):
        self._put_reg_on_market(self.reg_a)
        self.reg_a.remove_shift_regis_from_market()
        self.assertEqual(self.reg_a.exchange_state, "draft")

    def test_remove_cancels_pending_proposals(self):
        """Removing from market cancels any in_progress proposals."""
        self._put_reg_on_market(self.reg_b)
        proposal = self.env["proposal"].create(
            {
                "src_shift_id": self.shift_a.id,
                "des_registration_id": self.reg_b.id,
                "state": "in_progress",
            }
        )
        self.reg_b.remove_shift_regis_from_market()
        self.assertEqual(proposal.state, "cancel")

    def test_remove_raises_if_already_accepted(self):
        """Cannot remove from market if an exchange was already accepted."""
        from odoo.exceptions import UserError

        self._put_reg_on_market(self.reg_b)
        self.env["proposal"].create(
            {
                "src_shift_id": self.shift_a.id,
                "des_registration_id": self.reg_b.id,
                "state": "accept",
            }
        )
        with self.assertRaises(UserError):
            self.reg_b.remove_shift_regis_from_market()

    def test_add_to_market_clears_replacing_ref(self):
        """Adding to market clears exchange_replacing_reg_id."""
        self.reg_a.write({"exchange_replacing_reg_id": self.reg_b.id})
        self.reg_a.add_shift_regis_to_market()
        self.assertFalse(self.reg_a.exchange_replacing_reg_id)


class TestGetUpcoming(MemberspaceCommon):
    """get_upcoming filters shifts correctly."""

    def test_returns_future_shifts(self):
        upcoming = self.env["shift.registration"].get_upcoming(self.partner_a)
        self.assertIn(self.reg_a, upcoming)

    def test_excludes_past_shifts(self):
        past = fields.Datetime.now() - timedelta(days=1)
        self.shift_a.write({"date_begin": past})
        upcoming = self.env["shift.registration"].get_upcoming(self.partner_a)
        self.assertNotIn(self.reg_a, upcoming)

    def test_excludes_cancelled_registrations(self):
        self.reg_a.write({"state": "cancel"})
        upcoming = self.env["shift.registration"].get_upcoming(self.partner_a)
        self.assertNotIn(self.reg_a, upcoming)

    def test_extra_args_applied(self):
        """Extra domain args narrow the result."""
        upcoming = self.env["shift.registration"].get_upcoming(
            self.partner_a,
            args=[("exchange_state", "=", "in_progress")],
        )
        self.assertNotIn(self.reg_a, upcoming)

    def test_only_partner_shifts_returned(self):
        """Only shifts of the given partner are returned."""
        upcoming = self.env["shift.registration"].get_upcoming(self.partner_a)
        partner_ids = upcoming.mapped("partner_id.id")
        self.assertTrue(all(p == self.partner_a.id for p in partner_ids))


class TestGetExtraDomainOnMarket(MemberspaceCommon):
    """get_extra_domain_on_market combines domains correctly."""

    def test_adds_in_progress_filter(self):
        domain = self.env["shift.registration"].get_extra_domain_on_market([])
        keys = [clause[0] for clause in domain if isinstance(clause, tuple)]
        self.assertIn("exchange_state", keys)

    def test_check_replacing_true_adds_filter(self):
        domain = self.env["shift.registration"].get_extra_domain_on_market(
            [], check_replacing=True
        )
        keys = [clause[0] for clause in domain if isinstance(clause, tuple)]
        self.assertIn("exchange_replacing_reg_id", keys)

    def test_check_replacing_false_omits_filter(self):
        domain = self.env["shift.registration"].get_extra_domain_on_market(
            [], check_replacing=False
        )
        keys = [clause[0] for clause in domain if isinstance(clause, tuple)]
        self.assertNotIn("exchange_replacing_reg_id", keys)

    def test_base_args_preserved(self):
        base = [("partner_id", "=", self.partner_a.id)]
        domain = self.env["shift.registration"].get_extra_domain_on_market(base)
        flat = str(domain)
        self.assertIn("partner_id", flat)
        self.assertIn("exchange_state", flat)
