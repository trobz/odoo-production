"""
Tests for the Python method-based table structure.

These tests verify that get_my_next_shift_headers() and
get_my_next_shift_row_data() return the correct structure,
making it safe for other modules to inherit by overriding
Python methods instead of fragile xpath expressions.
"""

from unittest.mock import patch

from .common import MemberspaceCommon


class TestTableStructure(MemberspaceCommon):
    # ── get_my_next_shift_headers ────────────────────────────────────────────

    def test_headers_returns_list(self):
        headers = self.reg_a.get_my_next_shift_headers()
        self.assertIsInstance(headers, list)
        self.assertTrue(len(headers) > 0)

    def test_headers_required_keys(self):
        """Each header must have 'key' and 'label'."""
        for header in self.reg_a.get_my_next_shift_headers():
            self.assertIn("key", header, f"Header missing 'key': {header}")
            self.assertIn("label", header, f"Header missing 'label': {header}")

    def test_headers_default_columns(self):
        """Base module must expose date, hour, exchange columns."""
        keys = [h["key"] for h in self.reg_a.get_my_next_shift_headers()]
        self.assertIn("date", keys)
        self.assertIn("hour", keys)
        self.assertIn("exchange", keys)

    def test_headers_exchange_is_last(self):
        """'exchange' column must always be last (special rendering)."""
        headers = self.reg_a.get_my_next_shift_headers()
        self.assertEqual(headers[-1]["key"], "exchange")

    def test_headers_css_class_present(self):
        """All headers should have css_class key (can be empty string)."""
        for header in self.reg_a.get_my_next_shift_headers():
            self.assertIn("css_class", header)

    # ── get_my_next_shift_row_data ───────────────────────────────────────────

    def test_row_data_returns_dict(self):
        row = self.reg_a.get_my_next_shift_row_data(self.user_a)
        self.assertIsInstance(row, dict)

    def test_row_data_has_date_and_hour(self):
        row = self.reg_a.get_my_next_shift_row_data(self.user_a)
        self.assertIn("date", row)
        self.assertIn("hour", row)

    def test_row_data_has_css_style(self):
        row = self.reg_a.get_my_next_shift_row_data(self.user_a)
        self.assertIn("css_style", row)

    def test_row_data_line_through_for_cancelled(self):
        """Cancelled registration should have strikethrough CSS."""
        self.reg_a.write({"state": "cancel"})
        row = self.reg_a.get_my_next_shift_row_data(self.user_a)
        self.assertIn("line-through", row["css_style"])
        # Restore
        self.reg_a.write({"state": "open"})

    def test_row_data_no_line_through_for_open(self):
        """Open registration should NOT have strikethrough CSS."""
        self.reg_a.write({"state": "open"})
        row = self.reg_a.get_my_next_shift_row_data(self.user_a)
        self.assertNotIn("line-through", row["css_style"])

    def test_row_data_headers_keys_match(self):
        """
        All non-exchange header keys must exist in row_data.
        This is the contract between headers and row_data that
        the template relies on.
        """
        headers = self.reg_a.get_my_next_shift_headers()
        row = self.reg_a.get_my_next_shift_row_data(self.user_a)
        for header in headers:
            if header["key"] == "exchange":
                continue  # rendered by sub-template, not in row_data
            self.assertIn(
                header["key"],
                row,
                f"Header key '{header['key']}' has no matching row_data entry",
            )

    # ── Inheritance safety ───────────────────────────────────────────────────

    def test_subclass_can_add_column_by_overriding_python_only(self):
        """
        Simulate what an inheriting module (e.g. lalouve_custom) would do:
        patch the two methods and verify the table renders correctly
        without any XML changes.

        Uses unittest.mock.patch.object to avoid Odoo 18's metamodel_setattr
        guard that rejects direct class attribute assignment in tests.
        """
        reg_model_class = type(self.reg_a)
        original_headers = reg_model_class.get_my_next_shift_headers
        original_row = reg_model_class.get_my_next_shift_row_data

        def patched_headers(self_inner):
            headers = original_headers(self_inner)
            exchange_idx = next(
                i for i, h in enumerate(headers) if h["key"] == "exchange"
            )
            headers.insert(
                exchange_idx,
                {
                    "key": "team",
                    "label": "Team",
                    "css_class": "",
                },
            )
            return headers

        def patched_row(self_inner, user):
            row = original_row(self_inner, user)
            row["team"] = "A1"
            return row

        with (
            patch.object(reg_model_class, "get_my_next_shift_headers", patched_headers),
            patch.object(reg_model_class, "get_my_next_shift_row_data", patched_row),
        ):
            headers = self.reg_a.get_my_next_shift_headers()
            row = self.reg_a.get_my_next_shift_row_data(self.user_a)

        keys = [h["key"] for h in headers]
        self.assertIn("team", keys, "Added column should be in headers")
        self.assertEqual(headers[-1]["key"], "exchange", "exchange still last")
        self.assertIn("team", row, "Added column should be in row_data")
        self.assertEqual(row["team"], "A1")
