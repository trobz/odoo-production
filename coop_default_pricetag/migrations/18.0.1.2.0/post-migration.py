# -*- coding: utf-8 -*-
import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    """Fix barcode URLs in all views, replacing /report/barcode/?type= with /report/barcode/?barcode_type=."""
    if not version:
        return

    _logger.info("Fixing barcode URLs in all views")

    cr.execute(
        """
        SELECT id, arch_db
        FROM ir_ui_view
        WHERE arch_db::text LIKE %s
        """,
        ('%/report/barcode/?type=%',),
    )
    barcode_results = cr.fetchall()

    if not barcode_results:
        _logger.info("No views with barcode URLs found")
        return

    barcode_updated_count = 0
    barcode_pattern_old = '/report/barcode/?type='
    barcode_pattern_new = '/report/barcode/?barcode_type='

    for view_id, arch_db in barcode_results:
        import json
        
        if isinstance(arch_db, dict):
            arch_dict = arch_db
        elif isinstance(arch_db, str):
            try:
                arch_dict = json.loads(arch_db)
            except:
                arch_dict = {'en_US': arch_db}
        else:
            _logger.warning("Unexpected arch_db type for view %s: %s", view_id, type(arch_db))
            continue

        modified = False
        for lang_code, arch_content in arch_dict.items():
            if not isinstance(arch_content, str):
                continue
                
            if barcode_pattern_old in arch_content:
                updated_content = arch_content.replace(barcode_pattern_old, barcode_pattern_new)
                arch_dict[lang_code] = updated_content
                modified = True
                _logger.info(
                    "Found barcode URL pattern in view (id=%s, lang=%s), replacing with new parameter name",
                    view_id,
                    lang_code,
                )

        if modified:
            cr.execute(
                """
                UPDATE ir_ui_view
                SET arch_db = %s::jsonb
                WHERE id = %s
                """,
                (json.dumps(arch_dict), view_id),
            )
            barcode_updated_count += 1

    _logger.info(
        "Successfully updated %s view(s) with barcode URL fix",
        barcode_updated_count,
    )
