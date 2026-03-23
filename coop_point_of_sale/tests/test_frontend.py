from odoo.tests.common import tagged

from odoo.addons.point_of_sale.tests.test_frontend import TestPointOfSaleHttpCommon


@tagged("post_install", "-at_install")
class TestCoopPointOfSaleFrontend(TestPointOfSaleHttpCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cash_journal = cls.main_pos_config.payment_method_ids.filtered(
            lambda pm: pm.journal_id and pm.journal_id.type == "cash"
        ).mapped("journal_id")
        cls.main_pos_config.write(
            {
                "qty_zero_remove_line": True,
                "account_journal_ids": [(6, 0, cash_journal.ids)],
            }
        )

    def test_coop_pos_full_flow_tour(self):
        self.main_pos_config.with_user(self.pos_admin).open_ui()
        self.start_pos_tour("CoopPosFullFlowTour", "pos_admin")
