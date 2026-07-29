import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    """Fix carousel interval in all views containing data-bs-interval="false"."""
    if not version:
        return

    _logger.info("Fixing carousel data-bs-interval in all views")

    # Find all views that contain data-bs-interval with slideshow
    cr.execute(
        """
        SELECT id, arch_db
        FROM ir_ui_view
        WHERE arch_db::text LIKE %s
        """,
        ("%slideshow_%",),
    )
    results = cr.fetchall()

    if not results:
        _logger.info("No views with slideshow found")
        return

    updated_count = 0
    patterns_to_replace = [
        ('data-bs-interval="false"', 'data-bs-interval="5000"'),
        ("data-bs-interval='false'", "data-bs-interval='5000'"),
        ("data-bs-interval=&quot;false&quot;", "data-bs-interval=&quot;5000&quot;"),
    ]

    for view_id, arch_db in results:
        # arch_db is JSONB in v18, need to process each language key
        import json

        if isinstance(arch_db, dict):
            arch_dict = arch_db
        elif isinstance(arch_db, str):
            try:
                arch_dict = json.loads(arch_db)
            except Exception as e:
                _logger.warning("Failed to parse arch_db for view %s: %s", view_id, e)
                arch_dict = {"en_US": arch_db}
        else:
            _logger.warning(
                "Unexpected arch_db type for view %s: %s", view_id, type(arch_db)
            )
            continue

        modified = False
        for lang_code, arch_content in arch_dict.items():
            if not isinstance(arch_content, str):
                continue

            updated_content = arch_content
            for old_pattern, new_pattern in patterns_to_replace:
                if old_pattern in updated_content:
                    updated_content = updated_content.replace(old_pattern, new_pattern)
                    modified = True
                    _logger.info(
                        "Found '%s' in view (id=%s, lang=%s), replacing with '%s'",
                        old_pattern,
                        view_id,
                        lang_code,
                        new_pattern,
                    )

            if modified:
                arch_dict[lang_code] = updated_content

        if modified:
            cr.execute(
                """
                UPDATE ir_ui_view
                SET arch_db = %s::jsonb
                WHERE id = %s
                """,
                (json.dumps(arch_dict), view_id),
            )
            updated_count += 1

    _logger.info(
        "Successfully updated %s view(s) with carousel interval fix",
        updated_count,
    )
