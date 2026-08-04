# ruff: noqa: E501
import logging

from lxml import etree

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)

NEW_COMPANY_INFO = """<div>
    <p class="mb-1"><strong t-out="res_company.name"/></p>
    <t t-if="res_company.street or res_company.city">
        <p class="mb-1">
            <i class="fa fa-map-marker me-2 text-muted"/>
            <span t-out="res_company.street"/><br/>
            <span t-out="res_company.zip"/> <span t-out="res_company.city"/>
            <t t-if="res_company.country_id">
                <br/><span t-out="res_company.country_id.name"/>
            </t>
        </p>
    </t>
    <t t-if="res_company.phone">
        <p class="mb-1">
            <i class="fa fa-phone me-2 text-muted"/>
            <a t-attf-href="tel:#{res_company.phone}" t-out="res_company.phone" class="text-info"/>
        </p>
    </t>
    <t t-if="res_company.email">
        <p class="mb-1">
            <i class="fa fa-envelope me-2 text-muted"/>
            <a t-attf-href="mailto:#{res_company.email}" t-out="res_company.email" class="text-info"/>
        </p>
    </t>
    <t t-if="res_company.street">
        <p class="mt-3">
            <i class="fa fa-map-marker me-2"/>
            <a target="_blank"
               t-attf-href="https://maps.google.com/?q=#{res_company.street},#{res_company.city},#{res_company.country_id.name}"
               class="text-info">
                Google Maps
            </a>
        </p>
    </t>
</div>"""


def _update_view(view):
    try:
        root = etree.fromstring(view.with_context(lang=None).arch.encode())
    except etree.XMLSyntaxError as exc:
        _logger.error("Cannot parse arch for view id=%d: %s", view.id, exc)
        return False

    nodes = root.xpath('.//*[@t-call="website.company_description"]')
    if not nodes:
        return False

    new_info = etree.fromstring(NEW_COMPANY_INFO)
    for node in nodes:
        parent = node.getparent()
        idx = list(parent).index(node)
        parent.remove(node)
        parent.insert(idx, new_info)

    view.with_context(lang=None).write(
        {"arch_db": etree.tostring(root, encoding="unicode")}
    )
    return True


def migrate(cr, version):
    if not version:
        return

    env = api.Environment(cr, SUPERUSER_ID, {})
    views = (
        env["ir.ui.view"]
        .with_context(active_test=False)
        .search([("key", "=", "website.contactus")])
    )

    for view in views:
        has_xmlid = env["ir.model.data"].search_count(
            [("model", "=", "ir.ui.view"), ("res_id", "=", view.id)]
        )
        if has_xmlid:
            _logger.info("Skipping view id=%d (managed by xmlid)", view.id)
            continue

        updated = _update_view(view)
        if not updated:
            _logger.info(
                "View id=%d: website.company_description not found, skipping", view.id
            )
            continue

        _logger.info(
            "Updated contactus view id=%d (website_id=%s)", view.id, view.website_id.id
        )

        if not view.active:
            view.write({"active": True})
            _logger.info("Activated view id=%d", view.id)
