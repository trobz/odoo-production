from odoo.tools import SQL


def migrate(cr, _version):
    cr.execute(SQL("""
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_sml_product_write_date
        ON stock_move_line (product_id, write_date DESC)
    """))
