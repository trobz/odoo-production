# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

_logger = logging.getLogger(__name__)

NEW_FOOTER_EN = (
    '<ul class="list-inline">'
    '<li class="list-inline-item">'
    'Phone: <span class="o_force_ltr">0540070300</span>'
    "</li>"
    '<li class="list-inline-item">'
    "Email: <span>contact@otsokop.org</span>"
    "</li>"
    '<li class="list-inline-item">'
    "Web: <span>http://www.otsokop.org</span>"
    "</li>"
    '<li class="list-inline-item">'
    "VAT: <span>FR52814638185</span>"
    "</li>"
    "</ul>"
    "<p>Numéro fiscal: FR52814638185 | SIRET : 81463818500037 | "
    "RCS: Bayonne | APE: 4711B</p>"
)


def migrate(cr, version):
    cr.execute(
        """
        UPDATE res_company
        SET report_footer = jsonb_set(
            report_footer,
            '{en_US}',
            to_jsonb(%s::text)
        )
        WHERE report_footer::text LIKE '%%0540070300%%'
        """,
        (NEW_FOOTER_EN,),
    )
    _logger.info(
        "Updated report_footer en_US for %d company record(s) "
        "(unescaped HTML and fixed self-closing <i> tags)",
        cr.rowcount,
    )
