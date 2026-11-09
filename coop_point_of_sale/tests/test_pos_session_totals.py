from odoo import Command
from odoo.exceptions import UserError

from odoo.addons.point_of_sale.tests.common import TestPointOfSaleCommon


class TestPosSessionTotals(TestPointOfSaleCommon):
    """order_count / amount_untaxed / amount_total on pos.session are not stored
    (selling must not write the session row), but stay searchable, sortable and
    summable in SQL."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.pos_config.open_ui()
        cls.session_1 = cls.pos_config.current_session_id
        cls.config_2 = cls.pos_config.copy({"name": "Second POS"})
        cls.config_2.open_ui()
        cls.session_2 = cls.config_2.current_session_id
        cls.empty_config = cls.pos_config.copy({"name": "Empty POS"})
        cls.empty_config.open_ui()
        cls.session_empty = cls.empty_config.current_session_id
        cls.sessions = cls.session_1 | cls.session_2 | cls.session_empty

    def _order(self, session, total, tax=0.0):
        return self.PosOrder.create(
            {
                "company_id": self.env.company.id,
                "session_id": session.id,
                "lines": [
                    Command.create(
                        {
                            "product_id": self.product3.id,
                            "price_unit": total,
                            "qty": 1.0,
                            "price_subtotal": total - tax,
                            "price_subtotal_incl": total,
                        }
                    )
                ],
                "amount_total": total,
                "amount_tax": tax,
                "amount_paid": 0.0,
                "amount_return": 0.0,
            }
        )

    def test_fields_not_stored_but_sortable_and_summable(self):
        fields_info = self.env["pos.session"].fields_get(
            ["order_count", "amount_untaxed", "amount_total"],
            ["store", "sortable", "searchable", "aggregator"],
        )
        for fname, info in fields_info.items():
            self.assertFalse(info["store"], fname)
            self.assertTrue(info["sortable"], fname)
            self.assertTrue(info["searchable"], fname)
            self.assertEqual(info["aggregator"], "sum", fname)

    def test_selling_does_not_write_session_row(self):
        """A sale or a refund must not UPDATE the pos_session row: that row lock
        serialized every order of the session (SERIALIZATION_FAILURE + retries)."""
        self.env.flush_all()
        with self.assertLogs("odoo.sql_db", level="DEBUG") as logs:
            order = self._order(self.session_1, 100.0)
            self._order(self.session_1, -40.0)
            order.amount_total = 90.0
            self.env.flush_all()
        updates = [line for line in logs.output if 'UPDATE "pos_session"' in line]
        self.assertFalse(updates)

    def test_display_values_and_cancel(self):
        self._order(self.session_1, 120.0, tax=20.0)
        order = self._order(self.session_1, 50.0, tax=5.0)
        self.assertEqual(self.session_1.order_count, 2)
        self.assertAlmostEqual(self.session_1.amount_total, 170.0)
        self.assertAlmostEqual(self.session_1.amount_untaxed, 145.0)
        self.assertEqual(self.session_empty.order_count, 0)
        self.assertEqual(self.session_empty.amount_total, 0.0)
        # cancelled orders are excluded, and the cached value follows
        order.state = "cancel"
        self.assertEqual(self.session_1.order_count, 1)
        self.assertAlmostEqual(self.session_1.amount_total, 120.0)
        self.assertAlmostEqual(self.session_1.amount_untaxed, 100.0)

    def test_refund_counts_in_session(self):
        self._order(self.session_1, 80.0)
        self._order(self.session_1, -30.0)
        self.assertEqual(self.session_1.order_count, 2)
        self.assertAlmostEqual(self.session_1.amount_total, 50.0)

    def test_search(self):
        self._order(self.session_1, 300.0, tax=30.0)
        self._order(self.session_2, 100.0, tax=10.0)
        self._order(self.session_2, 50.0)
        Session = self.env["pos.session"]
        base = [("id", "in", self.sessions.ids)]
        self.assertEqual(
            Session.search(base + [("amount_total", ">", 200)]), self.session_1
        )
        self.assertEqual(
            Session.search(base + [("amount_total", "<=", 150)]),
            self.session_2 | self.session_empty,
        )
        self.assertEqual(
            Session.search(base + [("amount_untaxed", "=", 140)]), self.session_2
        )
        self.assertEqual(
            Session.search(base + [("order_count", ">=", 2)]), self.session_2
        )
        # "is not set" / "is set" on a number = compare with 0
        self.assertEqual(
            Session.search(base + [("order_count", "=", False)]), self.session_empty
        )
        self.assertEqual(
            Session.search(base + [("amount_total", "!=", False)]),
            self.session_1 | self.session_2,
        )
        with self.assertRaises(UserError):
            Session.search(base + [("amount_total", "in", [1, 2])])

    def test_sort(self):
        self._order(self.session_1, 10.0)
        self._order(self.session_2, 500.0)
        Session = self.env["pos.session"]
        base = [("id", "in", self.sessions.ids)]
        self.assertEqual(
            Session.search(base, order="amount_total desc").ids,
            [self.session_2.id, self.session_1.id, self.session_empty.id],
        )
        self.assertEqual(
            Session.search(base, order="order_count asc, id asc")[0], self.session_empty
        )

    def test_group_sum(self):
        self._order(self.session_1, 100.0, tax=10.0)
        self._order(self.session_2, 40.0, tax=4.0)
        cancelled = self._order(self.session_2, 999.0)
        cancelled.state = "cancel"
        groups = self.env["pos.session"].read_group(
            [("id", "in", self.sessions.ids)],
            ["amount_total:sum", "amount_untaxed:sum", "order_count:sum"],
            ["config_id"],
        )
        by_config = {g["config_id"][0]: g for g in groups}
        self.assertAlmostEqual(by_config[self.pos_config.id]["amount_total"], 100.0)
        self.assertAlmostEqual(by_config[self.config_2.id]["amount_total"], 40.0)
        self.assertAlmostEqual(by_config[self.config_2.id]["amount_untaxed"], 36.0)
        self.assertEqual(by_config[self.config_2.id]["order_count"], 1)
        self.assertEqual(by_config[self.empty_config.id]["order_count"], 0)
