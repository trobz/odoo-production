import logging

_logger = logging.getLogger(__name__)
_logger.info("Executing post-migration script for website_coop_custom 18.0.1.0.1 ...")


def migrate(cr, version):
    """Force invisible for contactus menu items."""
    _logger.info("Setting force_invisible=True for all website.menu with url='/contactus'")
    
    cr.execute("""
        UPDATE website_menu
        SET force_invisible = TRUE
        WHERE url = '/contactus'
    """)
    
    updated_count = cr.rowcount
    _logger.info(
        "Updated %d website.menu records with url='/contactus' to force_invisible=True",
        updated_count,
    )


_logger.info("Finished post-migration script for website_coop_custom 18.0.1.0.1")
