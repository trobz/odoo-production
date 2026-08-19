# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
import re

from psycopg2.extras import Json

_logger = logging.getLogger(__name__)

# In Odoo 18 the mail rendering eval context no longer provides ``format_tz``
# (see ``mail.mail_render_mixin._render_eval_context``); only ``format_date`` /
# ``format_datetime`` remain. Templates that still call ``format_tz(...)`` raise
# at render time, so we rewrite those calls to a plain ``strftime`` equivalent.
#
# Matches: format_tz(<expr>, ... , format=<q>fmt<q>)  where <q> is any of the
# quote forms that can appear inside a stored body_html attribute:
#   '   "   &#x27;   &#39;   &quot;
# The ``.*?`` swallows any intermediate arguments (e.g. ``tz=user.tz,``).
_QUOTE = r"(?:'|\"|&#x27;|&#39;|&quot;)"
_FORMAT_TZ_RE = re.compile(
    r"format_tz\(\s*([^,]+?)\s*,.*?format\s*=\s*(" + _QUOTE + r")(.+?)\2\s*\)",
    re.DOTALL,
)


def _replace_format_tz(expression):
    """Rewrite ``format_tz(expr, ..., format='fmt')`` calls found in a string
    into ``(expr).strftime('fmt') if (expr) else ''``.

    Operates on the raw (HTML-escaped) body so it matches regardless of whether
    the format quotes are stored literally or as entities. Returns the rewritten
    string (unchanged if nothing matched)."""

    def _sub(m):
        expr = m.group(1).strip()
        quote = m.group(2)
        fmt = m.group(3)
        return f"({expr}).strftime({quote}{fmt}{quote}) if ({expr}) else ''"

    return _FORMAT_TZ_RE.sub(_sub, expression)


def migrate(cr, version):
    if not version:
        return

    # body_html is a translated (jsonb) field. Read every stored translation
    # directly and rewrite each one; this avoids ORM translation-fallback
    # surprises and the fragility of round-tripping through an XML parser.
    cr.execute(
        "SELECT id, body_html FROM mail_template "
        "WHERE body_html::text ILIKE '%format_tz%'"
    )
    rows = cr.fetchall()

    if not rows:
        _logger.info("No mail templates with format_tz found, skipping")
        return

    for template_id, body_html in rows:
        if not body_html:
            continue

        new_body = {}
        changed = False
        for lang, html in body_html.items():
            fixed = _replace_format_tz(html) if html else html
            new_body[lang] = fixed
            if fixed != html:
                changed = True
            if fixed and "format_tz" in fixed:
                _logger.warning(
                    "mail_template id=%s (lang=%s) still contains a format_tz "
                    "call that could not be rewritten automatically; fix it "
                    "manually.",
                    template_id,
                    lang,
                )

        if changed:
            cr.execute(
                "UPDATE mail_template SET body_html = %s WHERE id = %s",
                (Json(new_body), template_id),
            )
            _logger.info("Rewrote format_tz in mail_template id=%s", template_id)
