"""
Tests for FTOP shift cancellation.

Covers:
- check_cancellable_ftop_shift (time-window guard)
- check_cancel_ftop_shift (returns confirmation data)
- do_cancel_ftop_shift (state transition + email)
"""

from datetime import timedelta
from unittest.mock import patch

from odoo import fields

from .common import MemberspaceCommon

_REG_CTX = {"creation_in_progress": True, "ignore_checking_attendance": True}


class TestCheckCancellableFtop(MemberspaceCommon):
    def _ftop_reg(self, hours_until_shift):
        """Create a FTOP registration with shift starting in N hours."""
        future = fields.Datetime.now() + timedelta(hours=hours_until_shift)
        shift = self.env["shift.shift"].create(
            {
                "name": self.template_ftop.name,
                "shift_template_id": self.template_ftop.id,
                "date_begin": future,
                "date_end": future + timedelta(hours=3),
                "shift_type_id": self.env.ref("coop_shift.shift_type_ftop").id,
            }
        )
        shift.button_confirm()
        shift.shift_mail_ids.unlink()
        ticket = shift.shift_ticket_ids[:1]
        return (
            self.env["shift.registration"]
            .with_context(**_REG_CTX)
            .create(
                {
                    "partner_id": self.partner_a.id,
                    "shift_id": shift.id,
                    "shift_ticket_id": ticket.id,
                }
            )
        )

    def test_cancellable_when_far_enough(self):
        reg = self._ftop_reg(hours_until_shift=48)
        self.assertTrue(reg.check_cancellable_ftop_shift())

    def test_not_cancellable_when_too_close(self):
        reg = self._ftop_reg(hours_until_shift=1)
        self.assertFalse(reg.check_cancellable_ftop_shift())

    def test_custom_duration_respected(self):
        """Config param ftop_shift_cancellation_duration is respected."""
        self.env["ir.config_parameter"].sudo().set_param(
            "coop_memberspace.ftop_shift_cancellation_duration", "50"
        )
        reg = self._ftop_reg(hours_until_shift=48)
        # 48h < 50h threshold → not cancellable
        self.assertFalse(reg.check_cancellable_ftop_shift())
        # Reset
        self.env["ir.config_parameter"].sudo().set_param(
            "coop_memberspace.ftop_shift_cancellation_duration", "24"
        )


class TestCheckCancelFtopShift(MemberspaceCommon):
    def _make_cancellable_ftop_reg(self):
        future = fields.Datetime.now() + timedelta(days=3)
        shift = self.env["shift.shift"].create(
            {
                "name": self.template_ftop.name,
                "shift_template_id": self.template_ftop.id,
                "date_begin": future,
                "date_end": future + timedelta(hours=3),
                "shift_type_id": self.env.ref("coop_shift.shift_type_ftop").id,
            }
        )
        shift.button_confirm()
        shift.shift_mail_ids.unlink()
        ticket = shift.shift_ticket_ids[:1]
        return (
            self.env["shift.registration"]
            .with_context(**_REG_CTX)
            .create(
                {
                    "partner_id": self.partner_a.id,
                    "shift_id": shift.id,
                    "shift_ticket_id": ticket.id,
                }
            )
        )

    def test_returns_code_1_when_cancellable(self):
        reg = self._make_cancellable_ftop_reg()
        result = reg.check_cancel_ftop_shift()
        self.assertEqual(result["code"], 1)

    def test_returns_confirmation_data_when_cancellable(self):
        reg = self._make_cancellable_ftop_reg()
        result = reg.check_cancel_ftop_shift()
        self.assertIn("data", result)
        self.assertIn("msg", result["data"])
        self.assertIn("confirm_msg", result["data"])
        self.assertIn("confirm_btn_label", result["data"])

    def test_returns_code_0_when_too_close(self):
        soon = fields.Datetime.now() + timedelta(hours=1)
        shift = self.env["shift.shift"].create(
            {
                "name": self.template_ftop.name,
                "shift_template_id": self.template_ftop.id,
                "date_begin": soon,
                "date_end": soon + timedelta(hours=3),
                "shift_type_id": self.env.ref("coop_shift.shift_type_ftop").id,
            }
        )
        shift.button_confirm()
        shift.shift_mail_ids.unlink()
        ticket = shift.shift_ticket_ids[:1]
        reg = (
            self.env["shift.registration"]
            .with_context(**_REG_CTX)
            .create(
                {
                    "partner_id": self.partner_a.id,
                    "shift_id": shift.id,
                    "shift_ticket_id": ticket.id,
                }
            )
        )
        result = reg.check_cancel_ftop_shift()
        self.assertEqual(result["code"], 0)
        self.assertIn("msg", result)

    def test_do_cancel_changes_state_to_cancel(self):
        reg = self._make_cancellable_ftop_reg()
        with patch.object(
            type(self.env["mail.template"]),
            "send_mail",
            return_value=True,
        ):
            reg.do_cancel_ftop_shift()
        self.assertEqual(reg.state, "cancel")

    def test_do_cancel_skips_uncancellable(self):
        """do_cancel_ftop_shift silently skips shifts that are too close."""
        soon = fields.Datetime.now() + timedelta(hours=1)
        shift = self.env["shift.shift"].create(
            {
                "name": self.template_ftop.name,
                "shift_template_id": self.template_ftop.id,
                "date_begin": soon,
                "date_end": soon + timedelta(hours=3),
                "shift_type_id": self.env.ref("coop_shift.shift_type_ftop").id,
            }
        )
        shift.button_confirm()
        shift.shift_mail_ids.unlink()
        ticket = shift.shift_ticket_ids[:1]
        reg = (
            self.env["shift.registration"]
            .with_context(**_REG_CTX)
            .create(
                {
                    "partner_id": self.partner_a.id,
                    "shift_id": shift.id,
                    "shift_ticket_id": ticket.id,
                }
            )
        )
        original_state = reg.state
        with patch.object(
            type(self.env["mail.template"]),
            "send_mail",
            return_value=True,
        ):
            reg.do_cancel_ftop_shift()
        # State should NOT change since check_cancellable returned False
        self.assertEqual(reg.state, original_state)
