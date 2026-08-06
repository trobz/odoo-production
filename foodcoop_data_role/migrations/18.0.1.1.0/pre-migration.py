import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)

_DEMO_NAME_PREFIXES = ("demo_user_", "role_line_group_")


def migrate(cr, version):
    if not version:
        return

    env = api.Environment(cr, SUPERUSER_ID, {})
    """Set noupdate=True on demo user and role line XML IDs.

    Prevents Odoo from deleting or overwriting these records during upgrade,
    since they are being moved to the foodcoop_data_role_demo module.
    """
    domain = [("module", "=", "foodcoop_data_role")]
    domain += ["|"] * (len(_DEMO_NAME_PREFIXES) - 1)
    for prefix in _DEMO_NAME_PREFIXES:
        domain.append(("name", "=like", f"{prefix}%"))

    records = env["ir.model.data"].search(domain)
    if records:
        _logger.info(
            "Setting noupdate=True on %d demo XML ID(s) in foodcoop_data_role",
            len(records),
        )
        records.write({"noupdate": True})
    else:
        _logger.info("No demo XML IDs found to protect (already migrated)")
