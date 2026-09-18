# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def _get_v12_publish_column(cr):
    """Find the column holding the v12 publication status"""
    cr.execute(
        """
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = 'product_public_category'
          AND (
              column_name LIKE 'openupgrade_legacy_%is_published'
              OR column_name = 'is_published'
              OR column_name = 'website_published'
          )
        ORDER BY
            CASE
                WHEN column_name LIKE 'openupgrade_legacy_%is_published' THEN 1
                WHEN column_name = 'is_published' THEN 2
                ELSE 3
            END;
        """
    )
    rows = cr.fetchall()
    return rows[0][0] if rows else None


def migrate(cr, version):
    """Post-migration script for website_category_publish 18.0.1.0.1."""
    if not version:
        return

    _logger.info("Starting post-migration for website_category_publish %s...", version)

    source_col = _get_v12_publish_column(cr)
    _logger.info("Detected publication source column: %s", source_col)

    if source_col:
        # pylint: disable=E8103
        cr.execute(
            f"""
            UPDATE product_public_category
            SET is_published = CASE
                WHEN {source_col} IS TRUE THEN TRUE
                ELSE FALSE
            END;
            """
        )
        _logger.info(
            "Updated %d product.public.category records based on column '%s'.",
            cr.rowcount,
            source_col,
        )
    else:
        cr.execute(
            """
            UPDATE product_public_category
            SET is_published = FALSE
            WHERE is_published IS NULL;
            """
        )

    env = api.Environment(cr, SUPERUSER_ID, {})
    categories = env["product.public.category"].search([])
    for category in categories.filtered(lambda c: c.parent_id):
        if not category.parent_id.is_published and category.is_published:
            category.write({"is_published": False})

    cr.execute(
        """
        UPDATE product_template pt
        SET is_categ_published = (
            NOT EXISTS (
                SELECT 1
                FROM product_public_category_product_template_rel rel
                WHERE rel.product_template_id = pt.id
            )
            OR EXISTS (
                SELECT 1
                FROM product_public_category_product_template_rel rel
                JOIN product_public_category cat
                    ON cat.id = rel.product_public_category_id
                WHERE rel.product_template_id = pt.id
                  AND cat.is_published = TRUE
            )
        );
        """
    )
    _logger.info(
        "Recomputed is_categ_published for %d product.template records.",
        cr.rowcount,
    )

    _logger.info("Finished post-migration for website_category_publish.")
