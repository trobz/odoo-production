# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo.tools.sql import column_exists

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    if not version:
        return

    if column_exists(cr, "stock_quant", "product_name"):
        _logger.info("Column stock_quant.product_name already exists, skipping.")
        return

    _logger.info("Creating column stock_quant.product_name (jsonb) before upgrade.")
    cr.execute("ALTER TABLE stock_quant ADD COLUMN product_name jsonb")
