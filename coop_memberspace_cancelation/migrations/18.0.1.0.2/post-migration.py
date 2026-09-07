# Copyright La Louve, Trobz
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

from odoo import SUPERUSER_ID, api
from odoo.tools.translate import xml_translate

_logger = logging.getLogger(__name__)

VIEW_KEY = "coop_memberspace_cancelation.my_next_shift_inherit"


def _terms(arch):
    """Return the translatable terms of ``arch`` in document order."""
    terms = []
    xml_translate(lambda term: (terms.append(term), term)[1], arch or "")
    return terms


def migrate(cr, version):
    """Propagate the ``fr_FR`` translations to website Copy-on-Write views.

    When a member edits the ``my_next_shift`` page in the website editor, Odoo
    creates a Copy-on-Write duplicate of ``my_next_shift_inherit``: same
    ``key``, ``website_id`` set, but *no* ``ir.model.data`` (no xml_id). The
    module translation loader (``_update_translations``) only reaches views it
    can resolve by xml_id, so those COW copies keep their English source terms
    and the cancellation modal intro paragraph renders in English on the
    website.

    We cannot key the translations on the module's own source terms: the
    website editor re-serialises the arch (e.g. ``<b><span/></b>`` gets its
    inner whitespace collapsed), so the COW's ``en_US`` terms no longer match
    the ``.po`` msgid. Instead we align terms *by position* - both views are
    copies of the same template, so their term lists share order - and map each
    COW's own ``en_US`` term to the matching ``fr_FR`` term from the reference
    view (the one with the xml_id, whose translation is already up to date).
    """
    env = api.Environment(cr, SUPERUSER_ID, {})

    reference = env.ref(VIEW_KEY, raise_if_not_found=False)
    if not reference:
        _logger.warning("%s: reference view not found, skipping.", VIEW_KEY)
        return

    ref_en = _terms(reference.with_context(lang="en_US").arch_db)
    ref_fr = _terms(reference.with_context(lang="fr_FR").arch_db)

    views = env["ir.ui.view"].search([("key", "=", VIEW_KEY)]) - reference
    for view in views:
        tgt_en = _terms(view.with_context(lang="en_US").arch_db)
        if len(tgt_en) != len(ref_en):
            _logger.warning(
                "%s: view id=%s has a diverged structure "
                "(%s terms vs %s), skipping.",
                VIEW_KEY,
                view.id,
                len(tgt_en),
                len(ref_en),
            )
            continue

        term_map = {
            tgt_en[i]: ref_fr[i] for i in range(len(ref_en)) if ref_en[i] != ref_fr[i]
        }
        if not term_map:
            continue

        view.update_field_translations("arch_db", {"fr_FR": term_map})
        _logger.info(
            "%s: reapplied fr_FR translations to view id=%s (website_id=%s).",
            VIEW_KEY,
            view.id,
            view.website_id.id or False,
        )
