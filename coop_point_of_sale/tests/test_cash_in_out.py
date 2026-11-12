from odoo.tests.common import tagged

from odoo.addons.point_of_sale.tests.test_frontend import TestPointOfSaleHttpCommon


@tagged("post_install", "-at_install")
class TestCoopCashInOut(TestPointOfSaleHttpCommon):
    def test_cashier_cash_in_out_tour(self):
        """Cashier (not a customer partner) with the invoicing group does a cash in."""
        self.assertFalse(self.pos_user.partner_id.customer)
        self.pos_user.write(
            {"groups_id": [(4, self.env.ref("account.group_account_invoice").id)]}
        )
        self.main_pos_config.write({"cash_control": True})
        self.main_pos_config.with_user(self.pos_user).open_ui()
        self.start_pos_tour("CoopCashInOutTour", login="pos_user")
