import logging

from lxml import etree

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)

# Bootstrap 5's `.carousel-indicators li` sets `flex: 0 1 auto` which lets
# indicator thumbnail items grow beyond the 40x40 px defined in Odoo's 000.scss.
# Fix: apply inline styles directly on each `li[data-bs-slide-to]` so the size
# cannot be overridden by any external stylesheet.

_ITEM_STYLE = (
    "width: 40px; height: 40px; flex: 0 0 40px;"
    " background-size: cover; background-position: center;"
    " background-repeat: no-repeat;"
)


def _fix_indicator_items(root, view_id):
    changes = 0
    for li in root.xpath(
        './/ul[contains(@class,"carousel-indicators")]/li[@data-bs-slide-to]'
    ):
        style = li.get("style", "")
        if "width: 40px" in style:
            continue
        sep = "; " if style.rstrip(";").strip() else ""
        li.set("style", style.rstrip("; ") + sep + _ITEM_STYLE)
        changes += 1

    if changes:
        _logger.info(
            "View id=%s: fixed %d indicator item(s) to 40x40px", view_id, changes
        )
    return changes


def _update_view(view):
    try:
        root = etree.fromstring(view.arch.encode())
    except etree.XMLSyntaxError as exc:
        _logger.error("Cannot parse arch for view id=%s: %s", view.id, exc)
        return 0

    changes = _fix_indicator_items(root, view.id)

    if changes:
        view.arch = etree.tostring(root, encoding="unicode")

    return changes


def migrate(cr, version):
    if not version:
        return

    env = api.Environment(cr, SUPERUSER_ID, {})
    View = env["ir.ui.view"].with_context(active_test=False)

    views = View.search(
        [
            ("arch_db", "like", "o_slideshow"),
            ("arch_db", "like", "carousel-indicators"),
        ]
    )

    if not views:
        _logger.info("No slideshow views found — nothing to migrate")
        return

    total_changes = 0
    for view in views:
        total_changes += _update_view(view)

    _logger.info(
        "Indicator size fix done — %d change(s) across %d view(s)",
        total_changes,
        len(views),
    )
