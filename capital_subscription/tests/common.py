from odoo import fields
from odoo.tests import common


class CapitalSubscriptionTest(common.TransactionCase):
    """Base class - Test the Capital Subscription."""

    def setUp(self):
        super().setUp()
        self.CapitalFund = self.env["capital.fundraising.wizard"]

        self.date_invoice = fields.Date.today()

        self.partner_agrolite_id = self.env.ref("base.res_partner_2").id
        self.category_id = self.env.ref(
            "capital_subscription.capital_fundraising_category_A"
        ).id
        self.share_qty = 10
        self.payment_journal_id = self.env.ref(
            "capital_subscription.capital_journal"
        ).id
        self.payment_term_id = self.env.ref("account.account_payment_term_immediate").id
