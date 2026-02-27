# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo.tools.sql import column_exists

_logger = logging.getLogger(__name__)


def _rename_done_to_mail_done(cr, table_name):
    old_field_exists = column_exists(cr, table_name, "done")
    new_field_exists = column_exists(cr, table_name, "mail_done")

    if old_field_exists and not new_field_exists:
        _logger.info("Renaming column done to mail_done on table %s", table_name)
        # pylint: disable=E8103
        cr.execute(f"ALTER TABLE {table_name} RENAME COLUMN done TO mail_done")
    elif new_field_exists:
        _logger.info(
            "Column mail_done already exists on table %s, skipping rename",
            table_name,
        )
    else:
        _logger.info(
            "Column done does not exist on table %s, skipping rename",
            table_name,
        )


def migrate(cr, version):
    _rename_done_to_mail_done(cr, "shift_mail")
