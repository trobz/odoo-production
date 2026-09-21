# Copyright La Louve, Trobz
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
"""Tweaks for the ``website_sale_checkout_skip_payment`` checkout flow.

This migration is hosted in ``coop_web`` (installed on every coop) rather than
in the OCA module, whose version we must not bump.

It does two things:

1. Deactivate the ``website_sale.extra_info`` checkout step for *every* coop
   (a generic ``website_sale`` view, unrelated to the skip-payment feature).
2. Refresh the French translations of the checkout-skip-payment content, guarded
   so it only runs where ``website_sale_checkout_skip_payment`` is installed:
   reload the module PO terms (view terms / field labels) and rewrite the two
   ``translate=True`` message fields on ``website`` rows, but only where the
   French value still holds the old English text (never clobber a real
   customization).
"""

import logging
import re

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)

SOURCE_MODULE = "website_sale_checkout_skip_payment"
# Custom wrapper present only on some coops; its ``i18n/fr.po`` ships the second
# "Confirm" button term of the ``navigation_buttons`` view.
DEFAULT_MODULE = "website_sale_checkout_skip_payment_default"
FR_LANG = "fr_FR"

# English source -> new French text, per translated field on ``website``.
FIELD_TRANSLATIONS = {
    "website_sale_checkout_skip_message": {
        "en": "Our team will check your order and send you payment "
        "information soon.",
        "fr": "Notre équipe va vérifier votre commande et va vous envoyer "
        "les informations de paiement.",
    },
    "website_sale_checkout_payment_skip_message": {
        "en": "The payment step will be skipped. You can confirm the order.",
        "fr": "L’étape de paiement sera ignorée. Vous pouvez confirmer " "la commande.",
    },
}

_TAG_RE = re.compile(r"<[^>]+>")


def _normalize(value):
    """Strip HTML tags and surrounding whitespace for a lenient comparison."""
    if not value:
        return ""
    return _TAG_RE.sub("", value).strip()


def migrate(cr, version):
    if not version:
        return

    env = api.Environment(cr, SUPERUSER_ID, {})

    # 1) Deactivate the 'Extra Info' checkout step for every coop (this is a
    # generic website_sale view, unrelated to the skip-payment feature).
    extra_info = env.ref("website_sale.extra_info", raise_if_not_found=False)
    if extra_info and extra_info.active:
        extra_info.write({"active": False})
        _logger.info("Deactivated 'Extra Info' checkout step (website_sale.extra_info)")
    else:
        _logger.info("'Extra Info' checkout step already inactive - skipping")

    # Guard: the translation refresh below only concerns coops that actually run
    # the checkout-skip-payment feature (coop_web itself is installed everywhere).
    source = env["ir.module.module"].search(
        [("name", "=", SOURCE_MODULE), ("state", "=", "installed")]
    )
    if not source:
        _logger.info("%s not installed; skipping translation refresh.", SOURCE_MODULE)
        return

    # 2) French translations.
    if not env["res.lang"].search_count([("code", "=", FR_LANG)]):
        _logger.info("%s not installed; nothing more to update.", FR_LANG)
        return

    # Reload the source module PO terms, plus the custom wrapper's terms where it
    # is installed (only some coops have it).
    modules = source | env["ir.module.module"].search(
        [("name", "=", DEFAULT_MODULE), ("state", "=", "installed")]
    )
    modules._update_translations(filter_lang=[FR_LANG], overwrite=True)
    _logger.info(
        "French translations reloaded (overwrite) for: %s.",
        ", ".join(modules.mapped("name")),
    )

    # Rewrite the two translated message fields on existing website records,
    # only where French still holds the old English text.
    websites = env["website"].with_context(active_test=False).search([])
    for field_name, terms in FIELD_TRANSLATIONS.items():
        en_norm = _normalize(terms["en"])
        for website in websites:
            current = website.with_context(lang=FR_LANG)[field_name]
            if _normalize(current) == en_norm:
                # Write in the French context (like the UI does) so it works for
                # both Text (translate=True) and Html (callable-translate) fields.
                website.with_context(lang=FR_LANG).write({field_name: terms["fr"]})
                _logger.info(
                    "website id=%s: %s translated to %s.",
                    website.id,
                    field_name,
                    FR_LANG,
                )
