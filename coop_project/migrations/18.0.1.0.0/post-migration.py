import logging

from odoo import SUPERUSER_ID, api

logger = logging.getLogger(__name__)


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})

    env.cr.execute("SELECT to_regclass(%s)", ("project_task_res_users_rel",))
    if env.cr.fetchone()[0]:
        env.cr.execute(
            """
            INSERT INTO project_task_user_rel (task_id, user_id)
            SELECT DISTINCT project_task_id, res_users_id
            FROM project_task_res_users_rel
            ON CONFLICT DO NOTHING
            """
        )
        logger.info("Migrated project.task assignees from assignee_ids to user_ids")
