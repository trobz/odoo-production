# Copyright La Louve, Trobz
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
"""Apply the updated French translations of ``website_sale_checkout_skip_payment``.

The French terms already live in the source (OCA) module's PO file
(``website_sale_checkout_skip_payment/i18n/fr.po``), but the database will not
pick them up on its own:

* View terms and field labels/help (e.g. the ``Confirm`` button in the
  ``navigation_buttons`` view) only refresh when the module's translations are
  re-imported with ``overwrite=True``.
* ``website_sale_checkout_skip_message`` and
  ``website_sale_checkout_payment_skip_message`` are ``translate=True`` *record*
  data on ``website`` rows. Their French value was frozen when each row was
  created, so a module translation reload does not touch them - they must be
  rewritten per record.

This migration is hosted in the custom ``_default`` wrapper because we must not
bump the OCA module's own version.
"""

import logging
import re

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)

SOURCE_MODULE = "website_sale_checkout_skip_payment"
# Our own module ships an ``i18n/fr.po`` that translates the second "Confirm"
# button term of ``website_sale_checkout_skip_payment.navigation_buttons``
# (its msgstr is empty in the OCA module, and we must not edit that module).
OWN_MODULE = "website_sale_checkout_skip_payment_default"
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

    if not env["res.lang"].search_count([("code", "=", FR_LANG)]):
        _logger.info("%s not installed; nothing to update.", FR_LANG)
        return

    # 1) Reload French translations so view terms and field metadata match the
    #    PO files: the OCA module for the existing terms (e.g. the first
    #    "Confirm" -> "Confirmer"), and our own module for the second "Confirm"
    #    button term whose translation ships in this module's ``i18n/fr.po``.
    modules = env["ir.module.module"].search(
        [("name", "in", [SOURCE_MODULE, OWN_MODULE])]
    )
    if not modules:
        _logger.warning("%s not found; skipping translation reload.", SOURCE_MODULE)
        return
    modules._update_translations(filter_lang=[FR_LANG], overwrite=True)
    _logger.info(
        "French translations reloaded (overwrite) for: %s.",
        ", ".join(modules.mapped("name")),
    )

    # 2) Rewrite the two translated message fields on existing website records,
    #    only where French still holds the old English text (never clobber a
    #    genuine customization).
    websites = env["website"].with_context(active_test=False).search([])
    for field_name, terms in FIELD_TRANSLATIONS.items():
        en_norm = _normalize(terms["en"])
        for website in websites:
            current = website.with_context(lang=FR_LANG)[field_name]
            if _normalize(current) == en_norm:
                # Write in the French context (like the UI does) so it works
                # for both ``translate=True`` (Text) and callable-translate
                # (Html) fields; ``update_field_translations`` expects a
                # different payload shape per field type.
                website.with_context(lang=FR_LANG).write({field_name: terms["fr"]})
                _logger.info(
                    "website id=%s: %s translated to %s.",
                    website.id,
                    field_name,
                    FR_LANG,
                )
