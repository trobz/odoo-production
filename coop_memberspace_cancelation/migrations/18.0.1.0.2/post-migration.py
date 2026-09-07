# Copyright La Louve, Trobz
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

from odoo import SUPERUSER_ID, api
from odoo.tools.translate import xml_translate

_logger = logging.getLogger(__name__)

VIEW_KEY = "coop_memberspace_cancelation.my_next_shift_inherit"


def migrate(cr, version):
    """Propagate the ``fr_FR`` translations to website Copy-on-Write views.

    When a member edits the ``my_next_shift`` page in the website editor, Odoo
    creates a Copy-on-Write duplicate of ``my_next_shift_inherit``: same
    ``key``, ``website_id`` set, but *no* ``ir.model.data`` (no xml_id). The
    module translation loader (``_update_translations``) only reaches views it
    can resolve by xml_id, so those COW copies keep their English source terms
    and the cancellation modal intro paragraph renders in English on the
    website.

    Here we take the module's own view (the one with the xml_id, whose ``fr_FR``
    arch is already up to date at this point) as the source of truth, extract
    the ``{en_US term: fr_FR term}`` map with Odoo's own term splitter, and
    re-apply it to every view sharing the key - including the COW copies.
    """
    env = api.Environment(cr, SUPERUSER_ID, {})

    reference = env.ref(VIEW_KEY, raise_if_not_found=False)
    if not reference:
        _logger.warning("%s: reference view not found, skipping.", VIEW_KEY)
        return

    en_terms = []
    fr_terms = []
    xml_translate(
        lambda t: (en_terms.append(t), t)[1],
        reference.with_context(lang="en_US").arch_db or "",
    )
    xml_translate(
        lambda t: (fr_terms.append(t), t)[1],
        reference.with_context(lang="fr_FR").arch_db or "",
    )

    # en_US and fr_FR share the same structure, so the terms line up by order.
    term_map = {en: fr for en, fr in zip(en_terms, fr_terms, strict=False) if en != fr}
    if not term_map:
        _logger.warning("%s: no french terms found on reference view.", VIEW_KEY)
        return

    views = env["ir.ui.view"].search([("key", "=", VIEW_KEY)]) - reference
    for view in views:
        view.update_field_translations("arch_db", {"fr_FR": term_map})
        _logger.info(
            "%s: reapplied fr_FR translations to view id=%s (website_id=%s).",
            VIEW_KEY,
            view.id,
            view.website_id.id or False,
        )
