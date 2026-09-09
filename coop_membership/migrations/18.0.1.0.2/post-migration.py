# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)

MODULE = "coop_membership"
TEMPLATE_NAME = "notify_mirror_children_email"
# Translated (jsonb) fields carrying the French terms shipped in i18n/fr.po.
TRANSLATED_FIELDS = ("name", "subject", "body_html")


def migrate(cr, version):
    if not version:
        return

    env = api.Environment(cr, SUPERUSER_ID, {})

    imd = env["ir.model.data"].search(
        [
            ("module", "=", MODULE),
            ("name", "=", TEMPLATE_NAME),
            ("model", "=", "mail.template"),
        ],
        limit=1,
    )
    if not imd:
        _logger.warning(
            "Template %s.%s not found, skipping translation reload",
            MODULE,
            TEMPLATE_NAME,
        )
        return

    # Drop any stored French value on this template's translated fields so the
    # fresh terms from i18n/fr.po are re-imported below, even if a stale fr_FR
    # value (e.g. holding the English source) is already present.
    for field in TRANSLATED_FIELDS:
        cr.execute(
            f"UPDATE mail_template SET {field} = {field} - 'fr_FR' "
            f"WHERE id = %s AND {field} ? 'fr_FR'",
            (imd.res_id,),
        )

    # Re-import the module's French terms; this repopulates the template with
    # the newly translated values without clobbering other customisations.
    env["ir.module.module"].search([("name", "=", MODULE)])._update_translations(
        ["fr_FR"]
    )

    _logger.info(
        "Reloaded French translations for template %s.%s", MODULE, TEMPLATE_NAME
    )
