# Copyright (C) 2024-Today: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    """Remove the User-defined Defaults (ir.default) forcing sales/purchase
    taxes on new products.

    Taxes on products are entirely managed through the Fiscal Classification
    mechanism, so any ir.default on ``taxes_id`` / ``supplier_taxes_id`` takes
    precedence over the field default (see ``BaseModel.default_get``) and
    pre-fills a tax on the new product form, which we don't want.
    """
    env = api.Environment(cr, SUPERUSER_ID, {})
    defaults = env["ir.default"].search(
        [
            ("field_id.model", "=", "product.template"),
            ("field_id.name", "in", ("taxes_id", "supplier_taxes_id")),
        ]
    )
    if defaults:
        _logger.info(
            "Removing %d ir.default record(s) forcing product taxes: %s",
            len(defaults),
            defaults.mapped("field_id.name"),
        )
        defaults.unlink()
