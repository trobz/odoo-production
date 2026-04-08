# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class GeneralLedgerReportCustom(models.AbstractModel):
    _inherit = "report.account_financial_report.general_ledger"

    def _group_move_lines_custom(self, move_lines):
        """Group lines by date, entry, account, taxes, partner, cost center and currency.

        This emulates the behaviour of the old group_by_move_partner method but on
        the dict-based structure used in account_financial_report for Odoo 18.
        """
        grouped = {}

        for line in move_lines:
            date = line.get("date")
            entry = line.get("entry") or line.get("move_name")
            account_code = line.get("account") or line.get("account_code")
            taxes_description = line.get("taxes_description", "")
            partner_name = line.get("partner") or line.get("partner_name", "")
            label = line.get("ref_label") or line.get("label") or ""
            analytic_distribution = line.get("analytic_distribution") or {}
            if isinstance(analytic_distribution, dict):
                cost_center = tuple(sorted(analytic_distribution.items()))
            else:
                cost_center = analytic_distribution
            matching_number = line.get("rec_name") or line.get("matching_number")
            currency_val = line.get("currency_id")
            if isinstance(currency_val, (list, tuple)) and currency_val:
                currency = currency_val[0]
            else:
                currency = currency_val

            key = (
                date,
                entry,
                account_code,
                taxes_description,
                partner_name,
                label,
                cost_center,
                matching_number,
                currency,
            )

            if key not in grouped:
                base = line.copy()
                base.update(
                    {
                        "debit": 0.0,
                        "credit": 0.0,
                        "balance": 0.0,
                    }
                )
                if "bal_curr" in base:
                    base["bal_curr"] = 0.0
                grouped[key] = base

            grouped[key]["debit"] += line.get("debit", 0.0)
            grouped[key]["credit"] += line.get("credit", 0.0)
            grouped[key]["balance"] += line.get("balance", 0.0)
            if "bal_curr" in grouped[key]:
                grouped[key]["bal_curr"] += line.get("bal_curr", 0.0)

        return list(grouped.values())

    def _create_general_ledger(
        self,
        gen_led_data,
        accounts_data,
        grouped_by,
        rec_after_date_to_ids,
        hide_account_at_0,
    ):
        general_ledger = super()._create_general_ledger(
            gen_led_data,
            accounts_data,
            grouped_by,
            rec_after_date_to_ids,
            hide_account_at_0,
        )

        for account in general_ledger:
            if "list_grouped" in account:
                for group_item in account["list_grouped"]:
                    if "move_lines" in group_item:
                        group_item["move_lines"] = self._group_move_lines_custom(
                            group_item["move_lines"]
                        )
            elif "move_lines" in account:
                account["move_lines"] = self._group_move_lines_custom(
                    account["move_lines"]
                )

        return general_ledger
