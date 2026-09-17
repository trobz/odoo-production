import logging

from lxml import etree

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)

# The two bottom cards of the `mywork_standard` view ("Echanger un service" and
# "Programmer un service ...") carry an inline `font-family` declaration from
# the website editor that makes their titles render inconsistently (the title
# with an explicit system font looks different from the one without).
# Website copies (COW) are detached from the module, so a normal `-u` won't
# touch them. Fix: remove only the inline `font-family` declarations from those
# two cards so both titles fall back to the same theme font. Their `font-size`
# is kept as-is (25px).
#
# Only these two cards are targeted (identified by their action links, not by
# their per-coop title text), so the counter cards above them are left intact.
# arch_db is a jsonb holding one arch per language; each language is handled.

_STRIP_PROPS = ("font-family",)
_CARD_LINKS = ("/standard/echange_de_services", "/standard/programmer_un_extra")


def _strip_element(el):
    decls = [d.strip() for d in el.get("style").split(";") if d.strip()]
    kept = [d for d in decls if d.split(":", 1)[0].strip().lower() not in _STRIP_PROPS]
    if len(kept) == len(decls):
        return False
    if kept:
        el.set("style", ";".join(kept))
    else:
        del el.attrib["style"]
    return True


def _strip_arch(arch, view_id):
    try:
        root = etree.fromstring(arch.encode())
    except etree.XMLSyntaxError as exc:
        _logger.error("Cannot parse arch for view id=%s: %s", view_id, exc)
        return None, 0

    changes = 0
    seen = set()
    for link in _CARD_LINKS:
        for anchor in root.xpath(f'.//a[@href="{link}"]'):
            cards = anchor.xpath(
                'ancestor::div[contains(@style,"border: 1px solid")][1]'
            )
            if not cards:
                continue
            card = cards[0]
            if id(card) in seen:
                continue
            seen.add(id(card))
            for el in card.xpath("descendant-or-self::*[@style]"):
                if _strip_element(el):
                    changes += 1

    if not changes:
        return None, 0
    return etree.tostring(root, encoding="unicode"), changes


def migrate(cr, version):
    if not version:
        return

    env = api.Environment(cr, SUPERUSER_ID, {})
    View = env["ir.ui.view"].with_context(active_test=False)

    views = View.search(
        [
            ("key", "=", "coop_memberspace.mywork_standard"),
            ("arch_db", "like", "font-family"),
        ]
    )

    if not views:
        _logger.info("No inline font-family found — nothing to migrate")
        return

    total_changes = 0
    for view in views:
        cr.execute("SELECT arch_db FROM ir_ui_view WHERE id = %s", (view.id,))
        row = cr.fetchone()
        arch_by_lang = row[0] if row else None
        if not arch_by_lang:
            continue

        view_changes = 0
        for lang, arch in arch_by_lang.items():
            if not arch:
                continue
            new_arch, changes = _strip_arch(arch, view.id)
            if changes:
                view.with_context(lang=lang).arch = new_arch
                view_changes += changes

        if view_changes:
            _logger.info(
                "View id=%s: removed font-family from %d element(s) "
                "in the two bottom cards",
                view.id,
                view_changes,
            )
            total_changes += view_changes

    _logger.info(
        "Font-family removal done — %d change(s) across %d view(s)",
        total_changes,
        len(views),
    )
