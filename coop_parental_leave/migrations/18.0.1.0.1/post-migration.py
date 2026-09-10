# Copyright (C) 2024 - Today
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging
import re

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)

# XML id of the email template whose translations contain the broken expression
TEMPLATE_XML_ID = "coop_parental_leave.reminder_birth_certificate_leave_email"

# Correct expression: "expected_birthdate" is a Date field, so it renders as a
# datetime.date object. It must be formatted with strftime (not parsed with
# strptime, which expects a string). The deadline is 4 weeks (28 days) after
# the expected birth date.
CORRECT_EXPR = (
    "(object.expected_birthdate + datetime.timedelta(days=28))" ".strftime('%Y-%m-%d')"
)

# Matches any t-out attribute whose expression uses strptime on the
# expected_birthdate field, e.g.:
#   t-out="datetime.datetime.strptime(object.expected_birthdate, '%Y-%m-%d')"
BROKEN_RE = re.compile(r't-out="[^"]*strptime[^"]*object\.expected_birthdate[^"]*"')
REPLACEMENT = f't-out="{CORRECT_EXPR}"'


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    template = env.ref(TEMPLATE_XML_ID, raise_if_not_found=False)
    if not template:
        _logger.warning(
            "Template %s not found, skipping strptime fix.", TEMPLATE_XML_ID
        )
        return

    # The broken expression lives in the (manually overridden) translations of
    # body_html, not in the English source. Fix every installed language while
    # preserving the client's custom content.
    langs = env["res.lang"].search([("active", "=", True)]).mapped("code")
    for lang in langs:
        body = template.with_context(lang=lang).body_html
        if not body or "strptime" not in body:
            continue
        new_body = BROKEN_RE.sub(REPLACEMENT, body)
        if new_body != body:
            template.with_context(lang=lang).write({"body_html": new_body})
            _logger.info(
                "Fixed strptime expression in template %s for lang %s.",
                TEMPLATE_XML_ID,
                lang,
            )
