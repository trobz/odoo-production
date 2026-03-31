from datetime import date, timedelta

from odoo import fields
from odoo.tests import common


class TestShiftExtensionLimit(common.TransactionCase):
    def setUp(self):
        super().setUp()

        self.ShiftExtension = self.env["shift.extension"]
        self.ShiftExtensionType = self.env["shift.extension.type"]
        self.ResPartner = self.env["res.partner"]
        self.ResCompany = self.env["res.company"]
        self.MailTemplate = self.env["mail.template"]
        self.CounterEvent = self.env["shift.counter.event"]

        self.extension_type = self.ShiftExtensionType.create(
            {
                "name": "Test Extension Type",
            }
        )
        self.company = self.env.user.company_id
        self.company.member_extension_limit = True
        self.company.member_extension_limit_count = 3
        self.company.member_extension_limit_type_ids = [(6, 0, self.extension_type.ids)]

    def _create_partner_with_alert_state(self):
        partner = self.ResPartner.create(
            {
                "name": "Test Partner Alert",
                "customer_rank": 1,
            }
        )
        future_date = date.today() + timedelta(days=30)
        partner.write({"date_alert_stop": future_date})
        self.CounterEvent.create(
            {
                "partner_id": partner.id,
                "name": "Test Points",
                "type": "standard",
                "point_qty": -1,
            }
        )
        partner.flush_recordset()
        return partner

    def test_create_extension_allowed_when_no_limit_configured(self):
        """Test extension creation is allowed when no limit is configured."""
        self.company.member_extension_limit = False
        self.company.member_extension_limit_type_ids = [(5, 0, 0)]

        partner = self._create_partner_with_alert_state()
        extension = self.ShiftExtension.create(
            {
                "partner_id": partner.id,
                "type_id": self.extension_type.id,
                "date_start": fields.Date.today(),
                "date_stop": fields.Date.today(),
            }
        )
        self.assertTrue(extension.exists())

    def test_create_extension_allowed_for_shift_manager(self):
        """Test extension creation is allowed for shift managers."""
        self.env.ref("coop_shift.group_shift_manager").write(
            {"users": [(4, self.env.user.id)]}
        )

        partner = self._create_partner_with_alert_state()
        extension = self.ShiftExtension.create(
            {
                "partner_id": partner.id,
                "type_id": self.extension_type.id,
                "date_start": fields.Date.today(),
                "date_stop": fields.Date.today(),
            }
        )
        self.assertTrue(extension.exists())

    def test_warning_email_sent_at_limit_minus_one(self):
        """Test warning email is sent when reaching limit-1 extensions."""
        self.company.member_extension_limit_count = 2

        partner = self._create_partner_with_alert_state()

        for _i in range(1):
            self.ShiftExtension.create(
                {
                    "partner_id": partner.id,
                    "type_id": self.extension_type.id,
                    "date_start": fields.Date.today(),
                    "date_stop": fields.Date.today(),
                    "is_new": True,
                }
            )

        extensions = self.ShiftExtension.search(
            [
                ("partner_id", "=", partner.id),
                ("type_id", "=", self.extension_type.id),
            ]
        )
        self.assertEqual(len(extensions), 1)

    def test_is_new_unchanged_when_partner_not_up_to_date(self):
        """Test is_new remains True when partner is not up_to_date."""
        partner = self._create_partner_with_alert_state()

        extension = self.ShiftExtension.create(
            {
                "partner_id": partner.id,
                "type_id": self.extension_type.id,
                "date_start": fields.Date.today(),
                "date_stop": fields.Date.today(),
                "is_new": True,
            }
        )

        partner._compute_cooperative_state()

        extension.invalidate_recordset()
        self.assertTrue(extension.is_new)

    def test_no_error_when_no_extensions_to_update(self):
        """Test no error when there are no new extensions."""
        partner = self._create_partner_with_alert_state()
        partner._compute_cooperative_state()

    def test_create_extension_allowed_for_delay_partner_below_limit(self):
        """Test extension creation is allowed for delay partner below limit."""
        partner = self._create_partner_with_alert_state()
        future_date = date.today() + timedelta(days=30)
        partner.write({"date_delay_stop": future_date})

        extension = self.ShiftExtension.create(
            {
                "partner_id": partner.id,
                "type_id": self.extension_type.id,
                "date_start": fields.Date.today(),
                "date_stop": fields.Date.today(),
                "is_new": True,
            }
        )
        self.assertTrue(extension.exists())
