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

    env.cr.execute("SELECT to_regclass(%s)", ("project_category",))
    if not env.cr.fetchone()[0]:
        return

    env.cr.execute("SELECT to_regclass(%s)", ("project_project_category_rel",))
    rel_table_exists = bool(env.cr.fetchone()[0])

    env.cr.execute(
        """
        INSERT INTO project_tags (name, color)
        SELECT pc.name, pc.color
        FROM project_category pc
        ON CONFLICT (name) DO NOTHING
        """
    )

    if rel_table_exists:
        env.cr.execute(
            """
            INSERT INTO project_project_project_tags_rel (
                project_project_id,
                project_tags_id
            )
            SELECT DISTINCT rel.project_id, pt.id
            FROM project_project_category_rel rel
            JOIN project_category pc ON pc.id = rel.category_id
            JOIN project_tags pt ON pt.name = pc.name
            ON CONFLICT DO NOTHING
            """
        )

    logger.info("Migrated project.category to project.tags")
