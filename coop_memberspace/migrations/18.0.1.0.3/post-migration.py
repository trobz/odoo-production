import logging

from lxml import etree

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)

# Target: ir.ui.view with key 'coop_memberspace.homepage' that has no xml_id
# (website-specific copy customised via the website builder).
# Change: add font-size: 18px !important to the three <h3> headings inside
# the .container div ("My next service", "Coopérateurs à jour", "Current week").

VIEW_KEY = "coop_memberspace.homepage"
NEW_FONT_SIZE = "font-size: 18px !important;"


def _find_target_views(env):
    """Return all homepage views that have no xml_id (website-builder copies)."""
    View = env["ir.ui.view"].with_context(active_test=False)
    IrModelData = env["ir.model.data"]

    result = View.browse()
    for view in View.search([("key", "=", VIEW_KEY)]):
        has_xml_id = IrModelData.search(
            [("model", "=", "ir.ui.view"), ("res_id", "=", view.id)], limit=1
        )
        if not has_xml_id:
            result |= view
    return result


def _update_arch(view):
    """Add font-size: 18px !important to the three <h3> headings inside .container.
    Returns the count of h3 nodes updated."""
    try:
        root = etree.fromstring(view.arch.encode())
    except etree.XMLSyntaxError as e:
        _logger.error("Failed to parse arch for view id=%s: %s", view.id, e)
        return 0

    # Target only h3 elements inside the .container div (not .container-fluid)
    # that don't already carry a font-size rule.
    nodes = root.xpath(
        './/div[contains(@class,"container") and not(contains(@class,"container-fluid"))]'  # noqa: E501
        '//h3[not(contains(@style,"font-size"))]'
    )

    if not nodes:
        _logger.info(
            "No target <h3> without font-size found in view id=%s"
            " — already updated or structure changed.",
            view.id,
        )
        return 0

    updated = 0
    for h3 in nodes:
        old_style = h3.get("style", "")
        separator = "" if not old_style or old_style.endswith(";") else ";"
        h3.set("style", old_style + separator + NEW_FONT_SIZE)
        _logger.info(
            "Updated <h3> style in view id=%s: %r → %r",
            view.id,
            old_style,
            h3.get("style"),
        )
        updated += 1

    if updated:
        view.arch = etree.tostring(root, encoding="unicode")

    return updated


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})

    views = _find_target_views(env)
    if not views:
        _logger.warning(
            "No ir.ui.view found with key '%s' without xml_id — skipping.", VIEW_KEY
        )
        return

    total_h3 = sum(_update_arch(view) for view in views)
    _logger.info(
        "coop_memberspace homepage migration done — updated %d <h3> node(s)"
        " across %d view(s).",
        total_h3,
        len(views),
    )
