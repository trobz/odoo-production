# Copyright La Louve, Trobz
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    """Reload this module's translations against the current view arch.

    The cancellation modals in ``views/website_view.xml`` were reformatted by
    pre-commit (``<b><span class="service_name"/></b>`` got line-broken). That
    changed the source terms of the ``my_next_shift_inherit`` view, so the
    existing ``fr_FR`` translations - keyed to the old collapsed source - no
    longer matched and the modal intro paragraphs stayed in English.

    By the time this post-migration runs, the view arch has already been
    reloaded (its ``en_US`` source now matches the ``.po`` msgid), so reloading
    the module terms with ``overwrite=True`` re-applies the French translations
    to the new source terms.
    """
    env = api.Environment(cr, SUPERUSER_ID, {})
    module = env["ir.module.module"].search(
        [("name", "=", "coop_memberspace_cancelation")], limit=1
    )
    if not module:
        return
    module._update_translations(overwrite=True)
    _logger.info("coop_memberspace_cancelation: translations reloaded (overwrite).")
