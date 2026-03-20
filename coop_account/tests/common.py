from odoo.tests import common


class CoopAccountTestCommon(common.TransactionCase):
    """Base class - Test the Coop Custom Account in invoice."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Useful models
        cls.AccountMove = cls.env["account.move"]
        cls.Account = cls.env["account.account"]
        cls.account = cls.Account.search(
            [("account_type", "=", "asset_cash")],
            limit=1,
        )
        cls.partner3 = cls.env.ref("base.res_partner_3")
        cls.journal = cls.env["account.journal"].search(
            [("type", "=", "sale")],
            limit=1,
        )
        cls.journal.write({"export_wrong_reconciliation": True})
        cls.product5 = cls.env.ref("product.product_product_5")
