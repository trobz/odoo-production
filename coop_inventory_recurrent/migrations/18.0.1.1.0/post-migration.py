# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    if not version:
        return

    env = api.Environment(cr, SUPERUSER_ID, {})
    location = env.ref("stock.stock_location_stock", raise_if_not_found=False)
    if not location:
        _logger.info(
            "Default stock location not found, skipping category group update."
        )
        return

    category_groups = env["stock.inventory.category.group"].search(
        [("location_id", "=", False)]
    )
    if not category_groups:
        _logger.info("No inventory category group requires a default location.")
        return

    category_groups.write({"location_id": location.id})
    _logger.info(
        "Assigned %s as default location for %s inventory category group(s).",
        location.display_name,
        len(category_groups),
    )
