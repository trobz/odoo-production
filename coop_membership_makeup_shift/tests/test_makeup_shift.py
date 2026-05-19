from datetime import timedelta

from odoo import fields

from .common import MakeupShiftCommon


class TestCheckMakeupShift(MakeupShiftCommon):
    """Eligibility check for makeup shift registration."""

    def test_eligible_when_alert_and_negative_points(self):
        """Standard member with negative points (not up_to_date) is eligible."""
        self.assertEqual(self.partner_a.shift_type, "standard")
        self.assertNotEqual(self.partner_a.cooperative_state, "up_to_date")
        self.assertLess(self.partner_a.final_standard_point, 0)
        self.assertTrue(self.partner_a.check_makeup_shift())

    def test_not_eligible_when_up_to_date(self):
        """Up-to-date member cannot register a makeup shift."""
        self.assertEqual(self.partner_b.cooperative_state, "up_to_date")
        self.assertFalse(self.partner_b.check_makeup_shift())

    def test_not_eligible_when_points_zero(self):
        """Member with exactly 0 points is not eligible (needs < 0)."""
        # Reset partner_a to 0 by adding +1
        self.env["shift.counter.event"].create(
            {
                "partner_id": self.partner_a.id,
                "type": "standard",
                "point_qty": 1.0,
                "name": "Catch-up",
            }
        )
        self.assertEqual(self.partner_a.final_standard_point, 0.0)
        self.assertFalse(self.partner_a.check_makeup_shift())

    def test_not_eligible_when_ftop_member(self):
        """FTOP team member (in_ftop_team) is never eligible for makeup shift."""
        self.assertTrue(self.ftop_partner.in_ftop_team)
        self.assertFalse(self.ftop_partner.check_makeup_shift())


class TestRegisterMakeupShift(MakeupShiftCommon):
    """register_makeup_shift method on shift.shift."""

    def _register_as_user_a(self):
        return self.shift_makeup.with_user(self.user_a).register_makeup_shift()

    def test_success_returns_code_1(self):
        """Eligible member gets code=1 and empty message."""
        code, msg = self._register_as_user_a()
        self.assertEqual(code, 1)
        self.assertEqual(msg, "")

    def test_success_creates_registration(self):
        """Registration is created for the partner."""
        self._register_as_user_a()
        reg = self.env["shift.registration"].search(
            [
                ("partner_id", "=", self.partner_a.id),
                ("shift_id", "=", self.shift_makeup.id),
            ]
        )
        self.assertEqual(len(reg), 1)

    def test_registration_has_is_makeup_true(self):
        """Created registration has is_makeup=True."""
        self._register_as_user_a()
        reg = self.env["shift.registration"].search(
            [
                ("partner_id", "=", self.partner_a.id),
                ("shift_id", "=", self.shift_makeup.id),
            ]
        )
        self.assertTrue(reg.is_makeup)

    def test_registration_state_is_draft(self):
        """Created registration has state=draft."""
        self._register_as_user_a()
        reg = self.env["shift.registration"].search(
            [
                ("partner_id", "=", self.partner_a.id),
                ("shift_id", "=", self.shift_makeup.id),
            ]
        )
        self.assertEqual(reg.state, "draft")

    def test_registration_uses_standard_ticket(self):
        """Registration is assigned to the standard ticket."""
        self._register_as_user_a()
        reg = self.env["shift.registration"].search(
            [
                ("partner_id", "=", self.partner_a.id),
                ("shift_id", "=", self.shift_makeup.id),
            ]
        )
        self.assertEqual(reg.shift_ticket_id.shift_type, "standard")

    def test_ineligible_partner_returns_code_0(self):
        """Ineligible partner (up_to_date) gets code=0 and a warning."""
        code, msg = self.shift_makeup.with_user(self.user_b).register_makeup_shift()
        self.assertEqual(code, 0)
        self.assertIn("can't register", msg)

    def test_no_seats_returns_code_0(self):
        """Shift with no available standard seats returns code=0."""
        std_ticket = self.shift_makeup.shift_ticket_ids.filtered(
            lambda t: t.shift_type == "standard"
        )
        std_ticket.write({"seats_max": 0})
        code, msg = self._register_as_user_a()
        self.assertEqual(code, 0)
        self.assertIn("No seat", msg)

    def test_seats_decrease_after_registration(self):
        """Available seats on the standard ticket decrease by 1."""
        std_ticket = self.shift_makeup.shift_ticket_ids.filtered(
            lambda t: t.shift_type == "standard"
        )
        seats_before = std_ticket.seats_available
        self._register_as_user_a()
        self.assertEqual(std_ticket.seats_available, seats_before - 1)


class TestIsReplacingMakeupShift(MakeupShiftCommon):
    """_is_replacing_makeup_shift detection on shift.registration."""

    def _make_reg(self, is_makeup=False):
        ticket = self.shift_makeup.shift_ticket_ids.filtered(
            lambda t: t.shift_type == "standard"
        )[:1]
        return (
            self.env["shift.registration"]
            .with_context(
                creation_in_progress=True,
                ignore_checking_attendance=True,
            )
            .create(
                {
                    "partner_id": self.partner_a.id,
                    "shift_id": self.shift_makeup.id,
                    "shift_ticket_id": ticket.id,
                    "is_makeup": is_makeup,
                }
            )
        )

    def test_true_when_replacing_a_makeup_reg(self):
        """Returns True when exchange_state=replacing and replaced reg is makeup."""
        makeup_reg = self._make_reg(is_makeup=True)

        future2 = fields.Datetime.now() + timedelta(days=14)
        shift2 = self.env["shift.shift"].create(
            {
                "name": self.template_2.name,
                "shift_template_id": self.template_2.id,
                "date_begin": future2,
                "date_end": future2 + timedelta(hours=3),
                "shift_type_id": self.env.ref("coop_shift.shift_type").id,
            }
        )
        shift2.button_confirm()
        shift2.shift_mail_ids.unlink()

        ticket2 = shift2.shift_ticket_ids.filtered(
            lambda t: t.shift_type == "standard"
        )[:1]
        replacing_reg = (
            self.env["shift.registration"]
            .with_context(
                creation_in_progress=True,
                ignore_checking_attendance=True,
            )
            .create(
                {
                    "partner_id": self.partner_b.id,
                    "shift_id": shift2.id,
                    "shift_ticket_id": ticket2.id,
                    "exchange_state": "replacing",
                    "exchange_replaced_reg_id": makeup_reg.id,
                }
            )
        )
        self.assertTrue(replacing_reg._is_replacing_makeup_shift())

    def test_false_when_replaced_reg_is_not_makeup(self):
        """Returns False when replaced registration has is_makeup=False."""
        normal_reg = self._make_reg(is_makeup=False)

        future2 = fields.Datetime.now() + timedelta(days=14)
        shift2 = self.env["shift.shift"].create(
            {
                "name": self.template_2.name,
                "shift_template_id": self.template_2.id,
                "date_begin": future2,
                "date_end": future2 + timedelta(hours=3),
                "shift_type_id": self.env.ref("coop_shift.shift_type").id,
            }
        )
        shift2.button_confirm()
        shift2.shift_mail_ids.unlink()

        ticket2 = shift2.shift_ticket_ids.filtered(
            lambda t: t.shift_type == "standard"
        )[:1]
        replacing_reg = (
            self.env["shift.registration"]
            .with_context(
                creation_in_progress=True,
                ignore_checking_attendance=True,
            )
            .create(
                {
                    "partner_id": self.partner_b.id,
                    "shift_id": shift2.id,
                    "shift_ticket_id": ticket2.id,
                    "exchange_state": "replacing",
                    "exchange_replaced_reg_id": normal_reg.id,
                }
            )
        )
        self.assertFalse(replacing_reg._is_replacing_makeup_shift())

    def test_false_when_exchange_state_not_replacing(self):
        """Returns False when exchange_state is not 'replacing'."""
        makeup_reg = self._make_reg(is_makeup=True)
        makeup_reg.write(
            {
                "exchange_state": "draft",
                "exchange_replaced_reg_id": makeup_reg.id,
            }
        )
        self.assertFalse(makeup_reg._is_replacing_makeup_shift())

    def test_false_when_no_replaced_reg(self):
        """Returns False when exchange_replaced_reg_id is not set."""
        reg = self._make_reg(is_makeup=True)
        reg.write({"exchange_state": "replacing", "exchange_replaced_reg_id": False})
        self.assertFalse(reg._is_replacing_makeup_shift())
