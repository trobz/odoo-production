# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from collections import defaultdict

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)

OLD_REL_TABLE = "pos_config_stock_scrap_origin_rel"
OLD_ORIGIN_TABLE = "stock_scrap_origin"


def _table_exists(cr, table_name):
    cr.execute(
        "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = %s)",
        (table_name,),
    )
    return cr.fetchone()[0]


def migrate_scrap_origin_ids(env):
    cr = env.cr

    if not _table_exists(cr, OLD_REL_TABLE):
        _logger.info("Table %s not found, skipping", OLD_REL_TABLE)
        return
    if not _table_exists(cr, OLD_ORIGIN_TABLE):
        _logger.info("Table %s not found, skipping", OLD_ORIGIN_TABLE)
        return

    # pylint: disable=E8103
    cr.execute(
        f"""
        SELECT rel.pos_config_id, orig.name
        FROM {OLD_REL_TABLE} rel
        JOIN {OLD_ORIGIN_TABLE} orig ON orig.id = rel.stock_scrap_origin_id
        """
    )
    rows = cr.fetchall()
    if not rows:
        _logger.info("No data in %s, nothing to migrate", OLD_REL_TABLE)
        return

    _logger.info("Found %d scrap origin links to migrate", len(rows))

    # Cache all tags by name to avoid repeated DB searches
    all_tags = env["stock.scrap.reason.tag"].search([])
    tag_by_name = {t.name: t for t in all_tags}

    # Group tag names by pos_config_id
    config_tags = defaultdict(list)
    for pos_config_id, origin_name in rows:
        tag = tag_by_name.get(origin_name)
        if not tag:
            tag = env["stock.scrap.reason.tag"].create({"name": origin_name})
            tag_by_name[origin_name] = tag
            _logger.info("Created new stock.scrap.reason.tag '%s'", origin_name)
        config_tags[pos_config_id].append(tag.id)

    # Write all tags per pos.config in one operation
    for pos_config_id, tag_ids in config_tags.items():
        pos_config = env["pos.config"].browse(pos_config_id)
        if not pos_config.exists():
            continue
        pos_config.scrap_reason_tag_ids = [(6, 0, tag_ids)]
        _logger.info("pos.config '%s': linked %d tag(s)", pos_config.name, len(tag_ids))


def migrate(cr, version):
    if not version:
        return
    env = api.Environment(cr, SUPERUSER_ID, {})
    migrate_scrap_origin_ids(env)
