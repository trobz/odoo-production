"""
Common fixtures for coop_memberspace tests.

Reuses demo data from coop_shift (shift templates, members) and adds
memberspace-specific setup: users with group_memberspace, upcoming shifts,
and configuration parameters.
"""

from datetime import timedelta

from odoo import fields
from odoo.tests import common


class MemberspaceCommon(common.TransactionCase):
    """Base class: creates two members with shifts ready for exchange."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        # ── Reuse coop_shift demo data ──────────────────────────────────────
        cls.template_standard = cls.env.ref("coop_shift.standard_template_1")
        cls.template_ftop = cls.env.ref("coop_shift.ftop_template_2")
        cls.partner_a = cls.env.ref("coop_shift.standard_member_1")
        cls.partner_b = cls.env["res.partner"].search(
            [("shift_type", "=", "standard"), ("id", "!=", cls.partner_a.id)],
            limit=1,
        )
        # Fallback: duplicate partner_a as partner_b if only one standard member
        if not cls.partner_b:
            cls.partner_b = cls.partner_a.copy({"name": "Test Member B"})

        cls.memberspace_group = cls.env.ref("coop_memberspace.group_memberspace")
        cls.portal_group = cls.env.ref("base.group_portal")

        # ── Create portal users for member A and member B ──────────────────
        cls.user_a = cls.env["res.users"].create(
            {
                "name": cls.partner_a.name + " User",
                "login": "member_a_test@test.com",
                "partner_id": cls.partner_a.id,
                "groups_id": [
                    (4, cls.memberspace_group.id),
                    (4, cls.portal_group.id),
                ],
            }
        )
        cls.user_b = cls.env["res.users"].create(
            {
                "name": cls.partner_b.name + " User",
                "login": "member_b_test@test.com",
                "partner_id": cls.partner_b.id,
                "groups_id": [
                    (4, cls.memberspace_group.id),
                    (4, cls.portal_group.id),
                ],
            }
        )

        # ── Create two upcoming shifts ──────────────────────────────────────
        future = fields.Datetime.now() + timedelta(days=7)
        future2 = fields.Datetime.now() + timedelta(days=14)

        cls.shift_a = cls.env["shift.shift"].create(
            {
                "name": cls.template_standard.name,
                "shift_template_id": cls.template_standard.id,
                "date_begin": future,
                "date_end": future + timedelta(hours=3),
                "shift_type_id": cls.env.ref("coop_shift.shift_type").id,
            }
        )
        cls.shift_b = cls.env["shift.shift"].create(
            {
                "name": cls.template_standard.name,
                "shift_template_id": cls.template_standard.id,
                "date_begin": future2,
                "date_end": future2 + timedelta(hours=3),
                "shift_type_id": cls.env.ref("coop_shift.shift_type").id,
            }
        )
        cls.shift_a.button_confirm()
        cls.shift_b.button_confirm()
        # Remove mail schedulers to prevent email sending during test setup
        cls.shift_a.shift_mail_ids.unlink()
        cls.shift_b.shift_mail_ids.unlink()

        ticket_a = cls.shift_a.shift_ticket_ids[:1]
        ticket_b = cls.shift_b.shift_ticket_ids[:1]

        # Registration of member A on shift_a, member B on shift_b
        # Bypass: template-registration check + attendance make-up check
        ShiftReg = cls.env["shift.registration"].with_context(
            creation_in_progress=True,
            ignore_checking_attendance=True,
        )
        cls.reg_a = ShiftReg.create(
            {
                "partner_id": cls.partner_a.id,
                "shift_id": cls.shift_a.id,
                "shift_ticket_id": ticket_a.id,
            }
        )
        cls.reg_b = ShiftReg.create(
            {
                "partner_id": cls.partner_b.id,
                "shift_id": cls.shift_b.id,
                "shift_ticket_id": ticket_b.id,
            }
        )

        # ── Config parameters ───────────────────────────────────────────────
        ICP = cls.env["ir.config_parameter"].sudo()
        ICP.set_param("coop.shift.shift_exchange_duration", "24")
        ICP.set_param("coop_memberspace.ftop_shift_cancellation_duration", "24")

    def _put_reg_on_market(self, registration):
        """Helper: put a registration on the exchange market."""
        registration.write(
            {
                "exchange_state": "in_progress",
                "exchange_replacing_reg_id": False,
            }
        )
