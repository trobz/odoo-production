# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    cr.execute(
        """
        UPDATE stock_move
            SET package_qty = product_qty / product_qty_package
        WHERE product_qty_package > 0
        """
    )
    _logger.info(
        "Migrated %d res.partner barcode values to company-dependent jsonb format",
        cr.rowcount,
    )
