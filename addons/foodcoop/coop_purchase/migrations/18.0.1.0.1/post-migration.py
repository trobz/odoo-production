# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    if not version:
        return

    _logger.info(
        "Backfilling account_move_line.product_default_code "
        "from product_product.default_code."
    )
    cr.execute(
        """
        UPDATE account_move_line AS aml
           SET product_default_code = pp.default_code
          FROM product_product AS pp
         WHERE aml.product_id = pp.id
           AND aml.product_default_code IS DISTINCT FROM pp.default_code
        """
    )

    _logger.info(
        "Backfilling stock_quant.product_default_code "
        "from product_product.default_code."
    )
    cr.execute(
        """
        UPDATE stock_quant AS sq
           SET product_default_code = pp.default_code
          FROM product_product AS pp
         WHERE sq.product_id = pp.id
           AND sq.product_default_code IS DISTINCT FROM pp.default_code
        """
    )
