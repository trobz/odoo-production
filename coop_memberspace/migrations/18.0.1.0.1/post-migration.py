import logging

from lxml import etree

from odoo import SUPERUSER_ID, api

logger = logging.getLogger(__name__)


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    update_myteam_template(env)


def update_myteam_template(env):
    """Update coop_memberspace.myteam template to use new avatar handling."""
    logger.info("Updating coop_memberspace.myteam template with new avatar handling")

    view = env.ref("coop_memberspace.myteam", raise_if_not_found=False)
    if not view:
        logger.warning("View coop_memberspace.myteam not found, skipping")
        return

    arch = view.arch

    # Check if old pattern exists
    if "member.image" not in arch:
        logger.info("Old pattern (member.image) not found, skipping update")
        return

    # Parse the arch as XML
    try:
        root = etree.fromstring(arch.encode("utf-8"))
    except etree.XMLSyntaxError as e:
        logger.error("Failed to parse view arch as XML: %s", e)
        return

    # Find all member_image divs and replace their content
    updated = False
    for div in root.xpath("//div[@class='member_image']"):
        # Get the div's XML content to determine which variable to use
        div_content = etree.tostring(div, encoding="unicode")

        # Determine if this is for coordinator or member
        if "coordinator.image" in div_content:
            variable = "coordinator"
        elif "member.image" in div_content:
            variable = "member"
        else:
            continue

        # Clear existing content
        div.clear()
        div.set("class", "member_image")

        # Create new img element with t-att-src attribute
        img = etree.SubElement(div, "img")
        # Set the t-att-src attribute with the appropriate variable
        img.set("t-att-src", f"'/web/image/res.partner/%d/avatar_128' % {variable}.id")

        updated = True
        logger.info("Updated member_image div in template for %s", variable)

    if updated:
        new_arch = etree.tostring(root, encoding="unicode", pretty_print=True)
        view.arch = new_arch
        logger.info("Template successfully updated with new avatar handling")
    else:
        logger.info("No member_image divs found to update")
