# Copyright (C) 2017-Today: La Louve (<http://www.lalouve.net/>)
# Copyright (C) 2019-Today Druidoo (<info@druidoo.io>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
#          Julien Weste
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
import re

from odoo import Command, _, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class AccountBankStatementLine(models.Model):
    _inherit = "account.bank.statement.line"

    def _match_bank_expense(self):
        self.ensure_one()
        matches = False
        # In Odoo 18, 'name' on statement line (via _inherits) is the move
        # sequence number; use 'payment_ref' for the user-visible label.
        # 'note' is replaced by 'narration' on account.move.
        field_map = {"name": "payment_ref", "ref": "ref", "note": "narration"}
        for field in ["name", "ref", "note"]:
            pattern = getattr(self.journal_id, f"bank_expense_{field}_pattern", False)
            if pattern:
                val = getattr(self, field_map[field])
                if val:
                    val = val.strip()
                if re.compile(pattern).search(val or ""):
                    matches = True
                else:
                    return False
        return matches

    def _reconcile_bank_expense(self):
        count = 0
        lines = self.filtered(lambda line: not line.is_reconciled)
        _logger.info(
            "====================== Start Reconcile %s line(s) of bank expense",
            len(lines),
        )
        for line in lines:
            if line._match_bank_expense():
                count += 1
                if not line.journal_id.bank_expense_account_id:
                    raise UserError(
                        _(
                            "You need to set a Bank Expense Account in the "
                            "journal if you want to use this feature."
                        )
                    )
                # In Odoo 18, replaces the suspense line with the expense account
                # instead of calling the deprecated process_reconciliation().
                _liq_line, suspense_line, _other_lines = line._seek_for_lines()
                if not suspense_line:
                    _logger.info("No suspense line found for %s, skipping.", line)
                    continue
                account_id = line.journal_id.bank_expense_account_id.id
                line.write(
                    {
                        "checked": True,
                        "line_ids": [
                            Command.update(
                                suspense_line.id,
                                {
                                    "account_id": account_id,
                                    "name": line.payment_ref or line.name,
                                },
                            )
                        ],
                    }
                )
            else:
                _logger.info("====================== No match for line %s", line)
        _logger.info("====================== End: %s line(s) matched", count)
        return count
