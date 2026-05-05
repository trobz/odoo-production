from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestWebsiteSalePaymentTerm(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.website = cls.env.ref("website.default_website")

        cls.term_website = cls.env["account.payment.term"].create(
            {
                "name": "Test Website Term",
                "company_id": cls.env.company.id,
            }
        )
        cls.term_partner = cls.env["account.payment.term"].create(
            {
                "name": "Test Partner Term",
                "company_id": cls.env.company.id,
            }
        )

        cls.partner_no_term = cls.env["res.partner"].create(
            {
                "name": "Partner No Term",
            }
        )
        cls.partner_with_term = cls.env["res.partner"].create(
            {
                "name": "Partner With Term",
                "property_payment_term_id": cls.term_partner.id,
            }
        )

        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "sale_ok": True,
                "type": "consu",
            }
        )

    def _create_website_order(self, partner, website=None):
        return self.env["sale.order"].create(
            {
                "partner_id": partner.id,
                "website_id": (website or self.website).id,
            }
        )

    def _create_backend_order(self, partner):
        return self.env["sale.order"].create(
            {
                "partner_id": partner.id,
            }
        )

    # -------------------------------------------------------------------------
    # Test case 1: website order, partner without term → website term applied
    # -------------------------------------------------------------------------

    def test_website_order_no_partner_term_uses_website_term(self):
        self.website.payment_term_id = self.term_website
        order = self._create_website_order(self.partner_no_term)
        self.assertEqual(
            order.payment_term_id,
            self.term_website,
            "Website term should be applied when partner has no term",
        )

    # -------------------------------------------------------------------------
    # Test case 2: website order, partner has own term → partner term wins
    # -------------------------------------------------------------------------

    def test_website_order_partner_term_takes_priority(self):
        self.website.payment_term_id = self.term_website
        order = self._create_website_order(self.partner_with_term)
        self.assertEqual(
            order.payment_term_id,
            self.term_partner,
            "Partner term should take priority over website term",
        )

    # -------------------------------------------------------------------------
    # Test case 3: website order, website has no term → fallback to website_sale
    # -------------------------------------------------------------------------

    def test_website_order_no_website_term_falls_back_to_default(self):
        self.website.payment_term_id = False
        order = self._create_website_order(self.partner_no_term)
        # website_sale fallback sets a term (immediate or first company term)
        self.assertTrue(
            order.payment_term_id,
            "A payment term should still be set by website_sale fallback",
        )
        self.assertNotEqual(
            order.payment_term_id,
            self.term_website,
            "Website term should not be applied when not configured",
        )

    # -------------------------------------------------------------------------
    # Test case 4: non-website order → module does not interfere
    # -------------------------------------------------------------------------

    def test_backend_order_without_website_not_affected(self):
        self.website.payment_term_id = self.term_website
        order = self._create_backend_order(self.partner_no_term)
        self.assertFalse(
            order.website_id,
            "Backend order should have no website_id",
        )
        self.assertNotEqual(
            order.payment_term_id,
            self.term_website,
            "Website term should not be applied to non-website orders",
        )

    # -------------------------------------------------------------------------
    # Test case 5: backend staff changes partner on existing website order
    #              (mirrors onchange_partner_id behavior from Odoo 12)
    # -------------------------------------------------------------------------

    def test_partner_change_on_website_order_recomputes_term(self):
        self.website.payment_term_id = self.term_website

        # Start with a partner that has their own term
        order = self._create_website_order(self.partner_with_term)
        self.assertEqual(order.payment_term_id, self.term_partner)

        # Staff changes partner to one without a term
        order.partner_id = self.partner_no_term
        order._compute_payment_term_id()
        self.assertEqual(
            order.payment_term_id,
            self.term_website,
            "Website term should be applied after switching to partner without term",
        )

    # -------------------------------------------------------------------------
    # Test case 6: website field on website model exists and is configurable
    # -------------------------------------------------------------------------

    def test_website_payment_term_field_exists(self):
        self.website.payment_term_id = self.term_website
        self.assertEqual(self.website.payment_term_id, self.term_website)

        self.website.payment_term_id = False
        self.assertFalse(self.website.payment_term_id)
