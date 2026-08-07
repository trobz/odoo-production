import csv
import logging
import os

_logger = logging.getLogger(__name__)

_OLD_MODULES = ("foodcoop_data_role", "foodcoop_data_role_memberspace")
_NEW_MODULE = "foodcoop_data_role_demo"
_DEMO_NAME_PREFIXES = ("demo_user_", "role_line_group_")


def pre_init_hook(env):
    """Migrate demo XML IDs from source modules to foodcoop_data_role_demo.

    Must run before data files are loaded to prevent Odoo from creating
    duplicate users when res_users.xml is processed.
    """
    IrModelData = env["ir.model.data"]

    name_domain = ["|"] * (len(_DEMO_NAME_PREFIXES) - 1)
    for prefix in _DEMO_NAME_PREFIXES:
        name_domain.append(("name", "=like", f"{prefix}%"))

    for old_module in _OLD_MODULES:
        _logger.info("Migrating demo XML IDs from %s to %s", old_module, _NEW_MODULE)
        records = IrModelData.search([("module", "=", old_module)] + name_domain)
        if records:
            _logger.info(
                "Found %d XML ID(s) to migrate to %s", len(records), _NEW_MODULE
            )
            records.write({"module": _NEW_MODULE})
            _logger.info("XML ID migration completed for %s", old_module)
        else:
            _logger.info("No XML IDs to migrate from %s (clean install)", old_module)


def post_init_hook(env):
    """Create demo user role assignments from CSV if they don't already exist."""
    _logger.info("Starting post-init-hook: creating demo user role assignments")

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

            existing = RoleLineModel.search(
                [("role_id", "=", role), ("user_id", "=", user)], limit=1
            )

            if existing:
                _logger.debug(
                    "Role assignment already exists: user_id=%s, role_id=%s", user, role
                )
                skipped_count += 1
                continue

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
