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

    # Recompute working state for all partners
    env["res.partner"].search([])._compute_working_state()

    # Recompute for all shift leaves
    ShiftLeave = env["shift.leave"]

    ShiftLeave._compute_forced_member_status()
    ShiftLeave._onchange_type_id()
    ShiftLeave._onchange_start_date()
    ShiftLeave._onchange_stop_date()

    _logger.info("Post-migration data adjustments completed.")
