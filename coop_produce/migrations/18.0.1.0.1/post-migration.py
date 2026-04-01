# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    if not version:
        return

    # Update product_product with default_packaging based on product_template
    _logger.info("Updating product_product.default_packaging from product_template.")
    cr.execute(
        """
        UPDATE product_product pp
        SET default_packaging = pt.default_packaging
        FROM product_template pt
        WHERE pt.id = pp.product_tmpl_id
            AND pp.default_packaging IS NULL
        """
    )
    _logger.info("Updated %s product rows.", cr.rowcount)

    # Update stock_quant with default_packaging based on product_template
    _logger.info("Updating stock_quant.default_packaging from product_template.")
    cr.execute(
        """
        UPDATE stock_quant sq
        SET default_packaging = pt.default_packaging
        FROM product_product pp
        JOIN product_template pt ON pt.id = pp.product_tmpl_id
        WHERE sq.product_id = pp.id
            AND sq.default_packaging IS NULL
        """
    )
    _logger.info("Updated %s stock quant rows.", cr.rowcount)

    # Update stock_quant with packaging_qty based on quantity and default_packaging
    _logger.info(
        "Updating stock_quant.packaging_qty from quantity and default_packaging."
    )
    cr.execute(
        """
        UPDATE stock_quant sq
        SET packaging_qty = sq.quantity / sq.default_packaging
        WHERE sq.default_packaging IS NOT NULL
            AND sq.default_packaging > 0
            AND sq.packaging_qty IS NULL
        """
    )
    _logger.info("Updated %s stock quant rows.", cr.rowcount)
