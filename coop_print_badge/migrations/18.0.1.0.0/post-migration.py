# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    """Post-migration script for Odoo 18 upgrade."""
    if not version:
        return

    # Create an environment to interact with Odoo models
    env = api.Environment(cr, SUPERUSER_ID, {})

    _logger.info("Starting post-migration data adjustments...")

    Company = env["res.company"]
    # Set reprint_change_field_ids to default value for existing companies
    trigger_field_ids = Company.get_trigger_badge_reprint_fields()
    trigger_fields = env["ir.model.fields"].search([("id", "in", trigger_field_ids)])

    # Add image_1920 to the list of fields that trigger badge reprint
    image_field = env["ir.model.fields"].search(
        [("model", "=", "res.partner"), ("name", "=", "image_1920")], limit=1
    )
    if image_field and image_field.id not in trigger_fields.ids:
        trigger_fields |= image_field

    Company.search([]).write(
        {
            "reprint_change_field_ids": [(6, 0, trigger_fields.ids)],
        }
    )
    _logger.info("Post-migration data adjustments completed.")
