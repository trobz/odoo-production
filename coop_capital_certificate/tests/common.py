from odoo.tests import common


class CapitalCertificateTest(common.TransactionCase):
    """Base class - Test the Capital Certificate report."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Useful models
        cls.CapitalCertificate = cls.env["capital.certificate"]
        cls.CapitalCertificateWizard = cls.env["capital.certificate.wizard"]
        cls.CapitalFund = cls.env["capital.fundraising.wizard"]
        cls.Customer1 = cls.env.ref("capital_subscription.middle_class_partner")
        cls.Customer2 = cls.env.ref("base.res_partner_2")

        cls.CapitalAccount = cls.env.ref(
            "capital_subscription.paid_capital_account_category_A"
        )
        cls.CapitalAccount.write({"reconcile": True})

        cls.Product = cls.env.ref("capital_subscription.product_fundraising_category_A")
        cls.Product.write({"property_account_income_id": cls.CapitalAccount.id})

        cls.category_id = cls.env.ref(
            "capital_subscription.capital_fundraising_category_A"
        ).id
        cls.share_qty = 10
        cls.payment_journal_id = cls.env.ref("capital_subscription.capital_journal").id
        cls.payment_journal = cls.env.ref("capital_subscription.capital_journal")
        cls.payment_term_id = cls.env.ref("account.account_payment_term_immediate").id
        cls.payment_journal.confirm_fundraising_payment = "allways"
        cls.env.ref("base.main_company").write(
            {"capital_certificate_header": "Capital Certificate Header"}
        )
