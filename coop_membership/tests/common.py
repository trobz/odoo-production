from odoo import fields
from odoo.tests import common


class CoopMembershipTest(common.TransactionCase):
    """Base class - Test the Coop Membership Test."""

    def setUp(self):
        super().setUp()

        self.date_invoice = fields.Date.today()

        self.ResPartner = self.env["res.partner"]
        self.CapitalFundWizard = self.env["capital.fundraising.wizard"]
        self.ShiftTemplateRegLine = self.env["shift.template.registration.line"]

        self.ShiftTemplateTicket = self.env["shift.template.ticket"]

        # self.standard_member_1 = self.env.ref(
        #     "coop_shift.standard_member_1"
        # )
        self.standard_member_1 = self.ResPartner.create(
            {
                "name": "Test Standard Member 1",
                "email": "test_standard_member_1@example.com",
                "customer_rank": 1,
                "shift_type": "standard",
            }
        )
        self.capital_fundraising_category_A = self.env.ref(
            "capital_subscription.capital_fundraising_category_A"
        ).id
        self.payment_journal_id = self.env.ref(
            "capital_subscription.capital_journal"
        ).id
        self.payment_term_id = self.env.ref("account.account_payment_term_immediate").id

        self.shift_template_id = self.env.ref("coop_shift.standard_template_1").id
