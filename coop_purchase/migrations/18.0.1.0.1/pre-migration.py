# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo.tools.sql import column_exists

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    if not version:
        return

    if column_exists(cr, "account_move_line", "product_default_code"):
        _logger.info(
            "Column account_move_line.product_default_code already exists, skipping."
        )
    else:
        _logger.info(
            "Creating column account_move_line.product_default_code "
            "(varchar) before upgrade."
        )
        cr.execute(
            "ALTER TABLE account_move_line ADD COLUMN product_default_code varchar"
        )

    if column_exists(cr, "stock_quant", "product_default_code"):
        _logger.info(
            "Column stock_quant.product_default_code already exists, skipping."
        )
    else:
        _logger.info(
            "Creating column stock_quant.product_default_code (varchar) before upgrade."
        )
        cr.execute("ALTER TABLE stock_quant ADD COLUMN product_default_code varchar")
