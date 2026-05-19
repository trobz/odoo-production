from datetime import timedelta

from odoo import fields
from odoo.tests import common


class MakeupShiftCommon(common.TransactionCase):
    """Base class for makeup shift tests.

    Setup:
    - partner_a: standard member, alert state (final_standard_point = -1)
    - partner_b: standard member, up_to_date (final_standard_point = 0)
    - shift_makeup: future shift from template_2 (≠ partner_a's template_1)
                    with a standard ticket that has seats_max=10
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        cls.template_1 = cls.env.ref("coop_shift.standard_template_1")
        cls.template_2 = cls.env.ref("coop_shift.standard_template_2")

        cls.partner_a = cls.env.ref("coop_shift.standard_member_1")
        cls.partner_b = cls.env["res.partner"].search(
            [("shift_type", "=", "standard"), ("id", "!=", cls.partner_a.id)],
            limit=1,
        )
        if not cls.partner_b:
            cls.partner_b = cls.partner_a.copy({"name": "Test Member B"})

        memberspace_group = cls.env.ref("coop_memberspace.group_memberspace")
        portal_group = cls.env.ref("base.group_portal")

        cls.user_a = cls.env["res.users"].create(
            {
                "name": cls.partner_a.name + " User",
                "login": "makeup_member_a@test.com",
                "partner_id": cls.partner_a.id,
                "groups_id": [(4, memberspace_group.id), (4, portal_group.id)],
            }
        )
        cls.user_b = cls.env["res.users"].create(
            {
                "name": cls.partner_b.name + " User",
                "login": "makeup_member_b@test.com",
                "partner_id": cls.partner_b.id,
                "groups_id": [(4, memberspace_group.id), (4, portal_group.id)],
            }
        )

        # FTOP partner for ineligibility tests.
        # Create an FTOP template registration so in_ftop_team=True.
        # _compute_shift_type in coop_membership always returns "standard" for
        # any new partner, so we use in_ftop_team (computed from template
        # registrations) as the FTOP indicator instead.
        cls.ftop_partner = cls.env["res.partner"].create({"name": "FTOP Test Member"})
        ftop_template = cls.env.ref("coop_shift.ftop_template_2")
        ftop_ticket = ftop_template.shift_ticket_ids.filtered(
            lambda t: t.shift_type == "ftop"
        )[:1]

        # _check_partner_subscription in coop_membership requires is_worker_member=True.
        # Create a proper capital subscription via wizard so owned_share > 0.
        worker_capital_cat = cls.env.ref(
            "capital_subscription.capital_fundraising_category_A"
        )
        cls.env["capital.fundraising.wizard"].create(
            {
                "date_invoice": fields.Date.today(),
                "partner_id": cls.ftop_partner.id,
                "category_id": worker_capital_cat.id,
                "share_qty": 10,
                "payment_journal_id": cls.env.ref(
                    "capital_subscription.capital_journal"
                ).id,
                "confirm_payment": False,
                "payment_term_id": cls.env.ref(
                    "account.account_payment_term_immediate"
                ).id,
            }
        ).button_confirm()

        cls.env["shift.template.registration"].create(
            {
                "shift_template_id": ftop_template.id,
                "partner_id": cls.ftop_partner.id,
                "shift_ticket_id": ftop_ticket.id,
            }
        )
        cls.ftop_partner.invalidate_recordset(["in_ftop_team", "tmpl_reg_ids"])

        # partner_a: alert state via negative counter event
        cls.counter_event_a = cls.env["shift.counter.event"].create(
            {
                "partner_id": cls.partner_a.id,
                "type": "standard",
                "point_qty": -1.0,
                "name": "Test absence",
            }
        )

        # Future shift from template_2 (≠ partner_a's template)
        future = fields.Datetime.now() + timedelta(days=7)
        cls.shift_makeup = cls.env["shift.shift"].create(
            {
                "name": cls.template_2.name,
                "shift_template_id": cls.template_2.id,
                "date_begin": future,
                "date_end": future + timedelta(hours=3),
                "shift_type_id": cls.env.ref("coop_shift.shift_type").id,
            }
        )
        cls.shift_makeup.button_confirm()
        cls.shift_makeup.shift_mail_ids.unlink()

        # Set seats_max on the standard ticket
        std_ticket = cls.shift_makeup.shift_ticket_ids.filtered(
            lambda t: t.shift_type == "standard"
        )
        std_ticket.write({"seats_max": 10})
