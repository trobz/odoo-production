import logging
import re

from lxml import etree

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)

# Fix photo slideshow gallery pages (coop-papote-*, etc.) that were created with
# the v12 website builder and render incorrectly in v18:
#
#  - The section had `overflow: hidden; height: 545px;` which clips the thumbnail
#    strip because v18 renders the full-width image much taller than v12 did.
#  - The carousel had no max-width, so it stretches to fill the entire viewport.
#  - Carousel images lack a max-height, causing them to be very tall.
#  - Bootstrap 5 positions carousel-control arrows inside the image (left:0/right:0,
#    width:15%), covering the image edges. In v12 they were outside the image area.
#  - Bootstrap 5 and 000.scss keep carousel-indicators position:absolute bottom:0,
#    which overlaps the image when there is no fixed section/carousel height.
#
# Fixes applied:
#  1. Section style: replace the fixed height+overflow with padding-bottom so the
#     thumbnail strip is always visible.
#  2. Carousel style: add `max-width: 700px; margin: 0 auto;` to centre and
#     constrain the slideshow, matching the v12 appearance.
#  3. Carousel images: add `max-height: 480px; object-fit: contain;` so images
#     never exceed a comfortable display height.
#  4. Carousel arrows: push them outside the carousel bounds with negative
#     left/right offset so they never overlap the image.
#  5. Carousel indicators: switch to position:relative so the thumbnail strip
#     flows naturally below the image instead of overlapping it.

_INDICATORS_STYLE = (
    "position: relative; bottom: auto; left: auto;" " right: auto; margin: 4px 0 0 0;"
)


def _fix_section(root, view_id):
    changes = 0
    for section in root.xpath(
        './/section[contains(@class,"o_slideshow")]'
        '[contains(@style,"height:") or contains(@style,"height :")]'
    ):
        style = section.get("style", "")
        if "overflow" not in style and "height" not in style:
            continue
        new_style = re.sub(r"overflow\s*:\s*hidden\s*;?\s*", "", style)
        new_style = re.sub(r"height\s*:\s*\d+px\s*;?\s*", "", new_style).strip()
        if "padding-bottom" not in new_style:
            sep = " " if new_style and not new_style.endswith(";") else ""
            new_style = new_style + sep + "padding-bottom: 30px;"
        if new_style != style:
            section.set("style", new_style)
            _logger.info("View id=%s: section style %r → %r", view_id, style, new_style)
            changes += 1
    return changes


def _fix_carousel(root, view_id):
    changes = 0
    for carousel in root.xpath(
        './/div[contains(@class,"carousel") and contains(@class,"slide")]'
    ):
        style = carousel.get("style", "")
        if "max-width" in style:
            continue
        new_style = "max-width: 700px; margin: 0 auto;"
        carousel.set("style", new_style)
        _logger.info("View id=%s: carousel style %r → %r", view_id, style, new_style)
        changes += 1
    return changes


def _fix_images(root):
    changes = 0
    for img in root.xpath(
        './/div[contains(@class,"carousel-inner")]'
        '//img[contains(@class,"img-fluid")]'
    ):
        style = img.get("style", "")
        if "max-height" in style:
            continue
        new_style = (style.rstrip("; ") + "; " if style else "") + (
            "max-height: 480px; object-fit: contain; margin: 0 auto;"
        )
        img.set("style", new_style)
        changes += 1
    return changes


def _fix_arrows(root):
    changes = 0
    for a_prev in root.xpath('.//a[contains(@class,"carousel-control-prev")]'):
        if "left:" not in a_prev.get("style", ""):
            a_prev.set("style", "left: -45px; width: 40px;")
            changes += 1
    for a_next in root.xpath('.//a[contains(@class,"carousel-control-next")]'):
        if "right:" not in a_next.get("style", ""):
            a_next.set("style", "right: -45px; width: 40px;")
            changes += 1
    return changes


def _fix_indicators(root):
    changes = 0
    for ul in root.xpath('.//ul[contains(@class,"carousel-indicators")]'):
        style = ul.get("style", "")
        if "position: relative" in style:
            continue
        new_style = (style.rstrip("; ") + "; " if style else "") + _INDICATORS_STYLE
        ul.set("style", new_style)
        changes += 1
    return changes


def _update_view(view):
    """Apply all slideshow fixes to *view*.  Returns the number of changes made."""
    try:
        root = etree.fromstring(view.arch.encode())
    except etree.XMLSyntaxError as exc:
        _logger.error("Cannot parse arch for view id=%s: %s", view.id, exc)
        return 0

    changes = (
        _fix_section(root, view.id)
        + _fix_carousel(root, view.id)
        + _fix_images(root)
        + _fix_arrows(root)
        + _fix_indicators(root)
    )

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
        _logger.info("No photo slideshow views found — nothing to migrate")
        return

    total_changes = 0
    for view in views:
        n = _update_view(view)
        if n:
            _logger.info("View id=%s updated with %d change(s)", view.id, n)
        total_changes += n

    _logger.info(
        "Slideshow v18 fix done — %d change(s) across %d view(s)",
        total_changes,
        len(views),
    )
