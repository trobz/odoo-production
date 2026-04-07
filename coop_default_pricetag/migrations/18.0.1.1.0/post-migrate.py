# Copyright (C) 2024-Today: Trobz
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    """Set default qweb_view_id for categories migrated from v12."""
    env = api.Environment(cr, SUPERUSER_ID, {})
    default_view = env.ref(
        "coop_default_pricetag.report_pricetag", raise_if_not_found=False
    )
    if not default_view:
        _logger.warning(
            "coop_default_pricetag: report_pricetag view not found, "
            "skipping default qweb_view_id migration."
        )
        return
    categories = env["product.print.category"].search([("qweb_view_id", "=", False)])
    if categories:
        categories.write({"qweb_view_id": default_view.id})
        _logger.info(
            "coop_default_pricetag: Set default qweb_view_id (%s) "
            "for %d product.print.category record(s).",
            default_view.name,
            len(categories),
        )
