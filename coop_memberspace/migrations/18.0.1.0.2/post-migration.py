import logging

from lxml import etree

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)

# Target: ir.ui.view with key 'coop_memberspace.homepage' that has no xml_id
# (website-specific copy customised via the website builder).
# Change: add font-size:24px; to the <h3> inside the member_status div.

VIEW_KEY = "coop_memberspace.homepage"
OLD_H3_STYLE = "margin-bottom: 0px;margin-top: 0px;"
NEW_H3_STYLE = "margin-bottom: 0px;margin-top: 0px;font-size:24px;"


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
    """Add font-size:24px; to the <h3> inside the member_status div.
    Returns True if the arch was updated, False if skipped."""
    try:
        root = etree.fromstring(view.arch.encode())
    except etree.XMLSyntaxError as e:
        _logger.error("Failed to parse arch for view id=%s: %s", view.id, e)
        return False

    nodes = root.xpath(
        './/div[@contenteditable="false" and @t-att-class="member_status[2]"]/h3'
    )
    if not nodes:
        _logger.warning(
            "Target <h3> not found in view id=%s — already updated or structure changed.",  # noqa: E501
            view.id,
        )
        return False

    h3 = nodes[0]
    current_style = h3.get("style", "")

    if "font-size" in current_style:
        _logger.info("font-size already set on <h3> in view id=%s — skipping.", view.id)
        return False

    h3.set("style", current_style.rstrip(";") + ";font-size:24px;")
    view.arch = etree.tostring(root, encoding="unicode")

    _logger.info(
        "Updated <h3> style in view id=%s: '%s' → '%s'",
        view.id,
        current_style,
        h3.get("style"),
    )
    return True


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})

    views = _find_target_views(env)
    if not views:
        _logger.warning(
            "No ir.ui.view found with key '%s' without xml_id — skipping.", VIEW_KEY
        )
        return

    updated = sum(_update_arch(view) for view in views)
    _logger.info(
        "coop_memberspace homepage migration done — updated: %d / %d views.",
        updated,
        len(views),
    )
