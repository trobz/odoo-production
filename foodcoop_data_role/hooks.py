import csv
import logging
import os

_logger = logging.getLogger(__name__)


def post_init_hook(env):
    """Create user role assignments from CSV if they don't already exist."""
    _logger.info("Starting post-init-hook: creating user role assignments")

    # Path to the CSV file
    module_path = os.path.dirname(__file__)
    csv_path = os.path.join(module_path, "data", "res.users.role.line.csv")

    if not os.path.exists(csv_path):
        _logger.warning("CSV file not found: %s", csv_path)
        return

    RoleLineModel = env["res.users.role.line"]
    IrModelData = env["ir.model.data"]

    created_count = 0
    skipped_count = 0

    with open(csv_path, encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            role_xmlid = row["role_id/id"]
            user_xmlid = row["user_id/id"]

            # Resolve XML IDs to actual records
            try:
                role = IrModelData._xmlid_to_res_id(role_xmlid)
                user = IrModelData._xmlid_to_res_id(user_xmlid)
            except Exception as e:
                _logger.warning(
                    "Could not resolve XML IDs: role=%s, user=%s. Error: %s",
                    role_xmlid,
                    user_xmlid,
                    e,
                )
                continue

            if not role or not user:
                _logger.warning(
                    "Invalid XML IDs: role=%s (id=%s), user=%s (id=%s)",
                    role_xmlid,
                    role,
                    user_xmlid,
                    user,
                )
                continue

            # Check if the role assignment already exists
            existing = RoleLineModel.search(
                [("role_id", "=", role), ("user_id", "=", user)], limit=1
            )

            if existing:
                _logger.debug(
                    "Role assignment already exists: user_id=%s, role_id=%s", user, role
                )
                skipped_count += 1
                continue

            # Create the role assignment
            try:
                RoleLineModel.create(
                    {
                        "role_id": role,
                        "user_id": user,
                    }
                )
                _logger.debug(
                    "Created role assignment: user_id=%s, role_id=%s", user, role
                )
                created_count += 1
            except Exception as e:
                _logger.error(
                    "Failed to create role assignment for user_id=%s, role_id=%s: %s",
                    user,
                    role,
                    e,
                )

    _logger.info(
        "Post-init-hook completed: created %d role assignments, skipped %d existing",
        created_count,
        skipped_count,
    )
