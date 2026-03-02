from datetime import date, timedelta

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests import common

from ..date_tools import conflict_period


class TestCoopShift(common.TransactionCase):
    def setUp(self):
        super().setUp()

        self.ShiftWizard = self.env["create.shifts.wizard"]
        self.Shift = self.env["shift.shift"]
        self.ShiftRegistration = self.env["shift.registration"]
        self.ShiftTemplateRegistration = self.env["shift.template.registration"]
        self.ShiftTicket = self.env["shift.ticket"]
        self.ShiftTemplateTicket = self.env["shift.template.ticket"]
        self.ResPartner = self.env["res.partner"]

        # Standard Template
        self.shift_template1 = self.env.ref("coop_shift.standard_template_1")

        self.shift_template2 = self.env.ref("coop_shift.standard_template_2")

        self.ftop_template_2 = self.env.ref("coop_shift.ftop_template_2")

        self.standard_member_1 = self.env.ref("coop_shift.standard_member_1")

        self.ftop_member_1 = self.env.ref("coop_shift.ftop_member")

        self.date_from = fields.Date.today()
        self.date_to = fields.Date.today() + timedelta(days=1)

        self.shift_type_id = self.env.ref("coop_shift.shift_type")

        self.shift_type_ftop_id = self.env.ref("coop_shift.shift_type_ftop")

        self.product_product_shift_standard = self.env.ref(
            "coop_shift.product_product_shift_standard"
        )

        self.product_product_shift_ftop = self.env.ref(
            "coop_shift.product_product_shift_ftop"
        )

        self.shift_template_ticket_id = self.env.ref(
            "coop_shift.template_ticket_1_standard"
        )

    def test_standard_member_event_registration(self):
        """Test the it should create Shift Type"""

        wiz = self.ShiftWizard.create(
            {
                "date_from": self.date_from,
                "date_to": self.date_to,
                "template_ids": [(6, 0, self.shift_template1.ids)],
            }
        )

        wiz.create_shifts()

        shifts = self.Shift.search(
            [
                ("shift_template_id", "=", self.shift_template1.id),
                ("state", "=", "draft"),
            ]
        )

        self.assertTrue(bool(shifts), "Shift: not created")
        self.assertEqual(
            shifts[0].shift_type_id,
            self.shift_type_id,
            "shift type: incorrect shift type",
        )

        # confirm shift
        shifts.button_confirm()
        self.assertEqual(
            shifts[0].state, "confirm", "Shift: confirmation of shift failed"
        )

        # Standard member registrations for this shift
        shift_ticket_id = self.ShiftTicket.search(
            [
                ("shift_id", "=", shifts[0].id),
                ("product_id", "=", self.product_product_shift_standard.id),
            ],
            limit=1,
        )
        self.assertEqual(len(shift_ticket_id), 1, "Shift Ticket: not created")

        test_std_reg1 = self.ShiftRegistration.create(
            {
                "partner_id": self.standard_member_1.id,
                "shift_ticket_id": shift_ticket_id.id,
                "shift_id": shifts[0].id,
            }
        )

        self.assertEqual(
            test_std_reg1.shift_type, "standard", "Shift Type :is not standard failed"
        )
        self.assertEqual(
            test_std_reg1.state, "open", "Shift: confirmation of registration failed"
        )

    def test_ftop_member_event_registration(self):
        """Test the it should create Shift Type"""

        wiz = self.ShiftWizard.create(
            {
                "date_from": self.date_from,
                "date_to": self.date_to,
                "template_ids": [(6, 0, self.ftop_template_2.ids)],
            }
        )

        wiz.create_shifts()

        shifts = self.Shift.search(
            [
                ("shift_template_id", "=", self.ftop_template_2.id),
                ("state", "=", "draft"),
            ]
        )

        self.assertTrue(bool(shifts), "Shift: not created")
        self.assertEqual(
            shifts[0].shift_type_id,
            self.shift_type_ftop_id,
            "shift type: incorrect shift type",
        )

        # confirm shift
        shifts.button_confirm()
        self.assertEqual(
            shifts[0].state, "confirm", "Shift: confirmation of shift failed"
        )

        # Standard member registrations for this shift
        shift_ticket_id = self.ShiftTicket.search(
            [
                ("shift_id", "=", shifts[0].id),
                ("product_id", "=", self.product_product_shift_ftop.id),
            ],
            limit=1,
        )
        self.assertEqual(len(shift_ticket_id), 1, "Shift Ticket: not created")

        test_std_reg2 = self.ShiftRegistration.create(
            {
                "partner_id": self.ftop_member_1.id,
                "shift_ticket_id": shift_ticket_id.id,
                "shift_id": shifts[0].id,
            }
        )

        self.assertEqual(
            test_std_reg2.shift_type, "ftop", "Shift Type :is not standard failed"
        )

        self.assertEqual(
            test_std_reg2.state, "open", "Shift: confirmation of registration failed"
        )

    def test_overlapping_registration(self):
        shift_template_ticket_id_2 = self.ShiftTemplateTicket.create(
            {
                "name": "Standard  2",
                "product_id": self.product_product_shift_standard.id,
                "shift_template_id": self.shift_template2.id,
            }
        )
        self.ShiftTemplateRegistration.create(
            {
                "partner_id": self.standard_member_1.id,
                "shift_ticket_id": self.shift_template_ticket_id.id,
                "shift_template_id": self.shift_template1.id,
            }
        )
        with self.assertRaises(ValidationError):
            self.ShiftTemplateRegistration.create(
                {
                    "partner_id": self.standard_member_1.id,
                    "shift_ticket_id": shift_template_ticket_id_2.id,
                    "shift_template_id": self.shift_template2.id,
                }
            )

    def test_conflict_period(self):
        self.assertEqual(
            conflict_period(
                date(2020, 1, 1),
                date(2020, 2, 1),
                date(2020, 1, 15),
                date(2020, 1, 20),
            ).get("conflict"),
            True,
        )
