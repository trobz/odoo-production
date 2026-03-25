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

    # Set reprint_change_field_ids to default value for existing companies
    env["res.company"].search([]).write(
        {
            "reprint_change_field_ids": env[
                "res.company"
            ].get_trigger_badge_reprint_fields(),
        }
    )
    _logger.info("Post-migration data adjustments completed.")
