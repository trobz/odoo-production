# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    if not version:
        return

    env = api.Environment(cr, SUPERUSER_ID, {})

    journals = env["account.journal"].search(
        [
            ("is_payment_capital_fundraising", "=", True),
            ("default_account_id", "!=", False),
        ]
    )
    if not journals:
        _logger.info(
            "No capital fundraising payment journals with default account found."
        )
        return

    payment_method_lines = env["account.payment.method.line"].search(
        [
            ("journal_id", "in", journals.ids),
            # ("payment_type", "=", "inbound"),
        ]
    )

    updated_count = 0
    for line in payment_method_lines:
        if line.payment_account_id != line.default_account_id:
            line.payment_account_id = line.default_account_id
            updated_count += 1

    _logger.info(
        "Capital subscription: updated %s inbound payment method line(s).",
        updated_count,
    )
