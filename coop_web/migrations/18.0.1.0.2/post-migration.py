# Copyright La Louve, Trobz
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from psycopg2 import sql

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    if not version:
        return

    cr.execute(
        sql.SQL("UPDATE res_users_settings SET persistent_classic_theme = FALSE")
    )
    _logger.info(
        "Set persistent_classic_theme to FALSE for all res_users_settings records."
    )
