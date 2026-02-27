# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
import re

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


EXPRESSION_PATTERN = re.compile(r"\$\{([^}]*)\}")


def _replace_expression(value, replacement_builder):
    def _replacement(match):
        expression = match.group(1).strip()
        return replacement_builder(expression)

    return EXPRESSION_PATTERN.sub(_replacement, value)


def _to_t_esc_expression(expression):
    escaped_expression = expression.replace('"', "&quot;")
    return f'<t t-esc="{escaped_expression}" />'


def _replace_expression_with_t_esc(html):
    return _replace_expression(html, _to_t_esc_expression)


def _replace_expression_with_jinja(value):
    return _replace_expression(value, lambda expression: f"{{{{{expression}}}}}")


def migrate_mail_template(env, template_xml_id):
    values_to_write = {}
    fr_values_to_write = {}

    template = env.ref(template_xml_id, raise_if_not_found=False)
    if not template:
        _logger.info("Template %s not found, skipping", template_xml_id)
        return

    source_body_html = template.body_html or ""
    updated_body_html = _replace_expression_with_t_esc(source_body_html)
    if updated_body_html != source_body_html:
        values_to_write["body_html"] = updated_body_html

    source_body_html_fr = template.with_context(lang="fr_FR").body_html or ""
    updated_body_html_fr = _replace_expression_with_t_esc(source_body_html_fr)
    if updated_body_html_fr != source_body_html_fr:
        fr_values_to_write["body_html"] = updated_body_html_fr

    fields_to_update = ["email_from", "email_to", "lang", "reply_to", "subject"]
    for field_name in fields_to_update:
        source_value = template[field_name] or ""
        updated_value = _replace_expression_with_jinja(source_value)
        if updated_value != source_value:
            values_to_write[field_name] = updated_value

    if not values_to_write and not fr_values_to_write:
        _logger.info("No ${...} pattern found in target fields for %s", template_xml_id)
        return

    if values_to_write:
        template.write(values_to_write)
    if fr_values_to_write:
        template.with_context(lang="fr_FR").write(fr_values_to_write)

    updated_fields = sorted(values_to_write.keys())
    if fr_values_to_write:
        updated_fields.extend(
            [f"{field}(fr_FR)" for field in sorted(fr_values_to_write)]
        )

    _logger.info(
        "Updated ${...} patterns for %s: %s",
        template_xml_id,
        ", ".join(updated_fields),
    )


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    migrate_mail_template(
        env, "coop_shift.mail_template_shift_swap_request_notification"
    )
