import logging

from lxml import etree

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def _update_view(view):
    try:
        root = etree.fromstring(view.with_context(lang=None).arch.encode())
    except etree.XMLSyntaxError as exc:
        _logger.error("Cannot parse arch for view id=%d: %s", view.id, exc)
        return False

    h3_nodes = root.xpath(".//h3")
    if not h3_nodes:
        return False

    changed = False
    for h3 in h3_nodes:
        style = h3.get("style", "")
        if "font-size: 24px !important" in style:
            continue
        normalized = style.rstrip()
        if normalized and not normalized.endswith(";"):
            normalized += ";"
        new_style = (
            normalized + " " if normalized else ""
        ) + "font-size: 24px !important;"
        h3.set("style", new_style.strip())
        changed = True

    if not changed:
        return False

    view.with_context(lang=None).write(
        {"arch_db": etree.tostring(root, encoding="unicode")}
    )
    return True


def migrate(cr, version):
    if not version:
        return

    env = api.Environment(cr, SUPERUSER_ID, {})
    views = (
        env["ir.ui.view"]
        .with_context(active_test=False)
        .search([("key", "=", "coop_memberspace.mywork")])
    )

    for view in views:
        updated = _update_view(view)
        if updated:
            _logger.info(
                "Updated mywork view id=%d: added font-size: 24px !important to h3",
                view.id,
            )
        else:
            _logger.info(
                "View id=%d: no h3 found or already up to date, skipping", view.id
            )
