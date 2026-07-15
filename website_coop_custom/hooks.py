import logging

_logger = logging.getLogger(__name__)


def post_init_hook(env):
    """Post-init hook to force invisible for contactus menu items."""
    _logger.info(
        "Executing post_init_hook for website_coop_custom: setting force_invisible=True for contactus menu"
    )

    env.cr.execute("""
        UPDATE website_menu
        SET force_invisible = TRUE
        WHERE url = '/contactus'
    """)

    updated_count = env.cr.rowcount
    _logger.info(
        "Updated %d website.menu records with url='/contactus' to force_invisible=True",
        updated_count,
    )
