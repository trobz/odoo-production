# Copyright 2026 Trobz
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.tests import TransactionCase, tagged
from odoo.tools.safe_eval import safe_eval


@tagged("post_install", "-at_install")
class TestPosOrderReport(TransactionCase):
    def test_action_default_filters(self):
        action = self.env.ref("point_of_sale.action_report_pos_order_all")
        context = safe_eval(action.context)
        self.assertEqual(context.get("search_default_filter_date"), 1)
        self.assertEqual(context.get("search_default_not_cancelled"), 1)
