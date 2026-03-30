# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo.tools.sql import column_exists

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    if not version:
        return

    if column_exists(cr, "stock_quant", "default_packaging"):
        _logger.info("Column stock_quant.default_packaging already exists, skipping.")
        return

    _logger.info(
        "Creating column stock_quant.default_packaging (float) before upgrade."
    )
    cr.execute("ALTER TABLE stock_quant ADD COLUMN default_packaging float")

    if column_exists(cr, "stock_quant", "packaging_qty"):
        _logger.info("Column stock_quant.packaging_qty already exists, skipping.")
        return

    _logger.info("Creating column stock_quant.packaging_qty (float) before upgrade.")
    cr.execute("ALTER TABLE stock_quant ADD COLUMN packaging_qty float")

    if column_exists(cr, "stock_quant", "qty_stock"):
        _logger.info("Column stock_quant.qty_stock already exists, skipping.")
        return

    _logger.info("Creating column stock_quant.qty_stock (float) before upgrade.")
    cr.execute("ALTER TABLE stock_quant ADD COLUMN qty_stock float")
