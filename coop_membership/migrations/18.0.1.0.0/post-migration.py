# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    """Post-migration script for Odoo 18 upgrade."""
    if not version:
        return

    # Create an environment to interact with Odoo models
    env = api.Environment(cr, SUPERUSER_ID, {})

    _logger.info("Starting post-migration data adjustments...")
    # migrate_mail_template(env, "coop_membership.welcome_email")
    # migrate_mail_template(env, "coop_membership.unsubscribe_email")
    # migrate_mail_template(env, "coop_membership.coop_abcd_leave_email")
    # migrate_mail_template(env, "coop_membership.coop_ftop_leave_email")
    # migrate_mail_template(env, "coop_membership.register_confirm_email")
    # migrate_mail_template(env, "coop_membership.coop_ftop_members_reminder_email")
    # migrate_mail_template(env, "coop_membership.reminder_end_leave_email")
    # migrate_mail_template(env, "coop_membership.confirm_leave_non_define_email")
    # migrate_mail_template(env, "coop_membership.change_team_abcd_email")
    # migrate_mail_template(env, "coop_membership.change_team_ftop_email")
    # migrate_mail_template(env, "coop_membership.registration_reminder_meeting_email")
    # migrate_mail_template(env, "coop_membership.abandoned_message_leave_email")
    # migrate_mail_template(
    #     env, "coop_membership.cancellation_message_absence_leave_email"
    # )
    # migrate_mail_template(
    #     env, "coop_membership.confirmation_message_absence_leave_email"
    # )
    # migrate_mail_template(env, "coop_membership.reminder_message_absence_leave_email")
    # migrate_mail_template(env, "coop_membership.confirmation_anticipated_leave_email")
    # migrate_mail_template(env, "coop_membership.notify_mirror_children_email")
    # migrate_mail_template(env, "coop_membership.notify_un_subscription_ftpop_email")

    # Set discovery_meeting_event_stage_ids to default value for existing companies
    env["res.company"].search([]).write(
        {
            "discovery_meeting_event_stage_ids": env[
                "res.company"
            ].get_default_discovery_meeting_event_stages(),
        }
    )
    _logger.info("Post-migration data adjustments completed.")
