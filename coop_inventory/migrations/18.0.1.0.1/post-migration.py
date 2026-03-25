# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo.tools.sql import column_exists

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    if not version:
        return

    if not column_exists(cr, "stock_quant", "product_name"):
        _logger.info("Column stock_quant.product_name not found, skipping update.")
        return

    _logger.info("Updating stock_quant.product_name from product_template.name.")
    cr.execute(
        """
        UPDATE stock_quant sq
        SET product_name = pt.name
        FROM product_product pp
        JOIN product_template pt ON pt.id = pp.product_tmpl_id
        WHERE sq.product_id = pp.id
        """
    )
    _logger.info("Updated %s stock quant rows.", cr.rowcount)
