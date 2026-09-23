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

    views = env["ir.ui.view"].search([("key", "=", "coop_memberspace.myteam")])

    if not views:
        logger.warning("No views found with key coop_memberspace.myteam, skipping")
        return

    for view in views:
        arch = view.arch

        # Parse the arch as XML
        try:
            root = etree.fromstring(arch.encode("utf-8"))
        except etree.XMLSyntaxError as e:
            logger.error("Failed to parse view arch as XML (id=%s): %s", view.id, e)
            continue

        root_content = etree.tostring(root, encoding="unicode")
        search_text = "'/web/image/res.partner/%d/avatar_128' % member.id"
        if root_content.count(search_text) < 2:
            # Try member.image and member.public_avatar
            search_text = "member.image and member.public_avatar"
            if root_content.count(search_text) < 2:
                logger.info(
                    "Skipping: %s in template content for view id=%s, found %s.",
                    search_text,
                    view.id,
                    root_content.count(search_text),
                )
                continue

        updated = False
        for div_kanban in root.xpath("//div[@class='member_kanban_content']"):
            # Get the div's XML content to determine which variable to use
            div_kanban_content = etree.tostring(div_kanban, encoding="unicode")

            # Determine if this is for coordinator or member
            if "coordinator." in div_kanban_content:
                variable = "coordinator"
            elif "member." in div_kanban_content:
                variable = "member"
            else:
                continue

            # Find div with class member_image and replace their content
            div = div_kanban.find(".//div[@class='member_image']")
            if div is None:
                continue
            # Clear existing content
            div.clear()
            div.set("class", "member_image")

            # Create new img element with t-att-src attribute
            img = etree.SubElement(div, "img")
            # Set the t-att-src attribute with the appropriate variable
            img.set(
                "t-att-src", f"'/web/image/res.partner/%d/avatar_128' % {variable}.id"
            )

            updated = True
            logger.info(
                "Updated member_image div in template for %s (view id=%s)",
                variable,
                view.id,
            )

        if updated:
            new_arch = etree.tostring(root, encoding="unicode", pretty_print=True)
            view.arch = new_arch
            logger.info(
                "Template successfully updated with new avatar handling (view id=%s)",
                view.id,
            )
        else:
            logger.info("No member_image divs found to update (view id=%s)", view.id)
