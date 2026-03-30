# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo.tools.sql import column_exists

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    if not version:
        return

    # Update stock_quant with default_packaging based on product_template
    if not column_exists(cr, "stock_quant", "default_packaging"):
        _logger.info("Column stock_quant.default_packaging not found, skipping update.")
        return

    _logger.info("Updating stock_quant.default_packaging from product_template.name.")
    cr.execute(
        """
        UPDATE stock_quant sq
        SET default_packaging = pt.default_packaging
        FROM product_product pp
        JOIN product_template pt ON pt.id = pp.product_tmpl_id
        WHERE sq.product_id = pp.id
        """
    )
    _logger.info("Updated %s stock quant rows.", cr.rowcount)

    # Update stock_quant with packaging_qty based on quantity and default_packaging
    if not column_exists(cr, "stock_quant", "packaging_qty"):
        _logger.info("Column stock_quant.packaging_qty not found, skipping update.")
        return

    _logger.info(
        "Updating stock_quant.packaging_qty from quantity and default_packaging."
    )
    cr.execute(
        """
        UPDATE stock_quant sq
        SET packaging_qty = CASE
            WHEN sq.default_packaging != 0 THEN sq.quantity / sq.default_packaging
            ELSE 0.0
        END
        WHERE sq.default_packaging IS NOT NULL
        """
    )
