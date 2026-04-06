from odoo import api, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.model
    def update_product_default_code(self, table_name, limit=10000):
        """
        ALTER TABLE stock_move ADD COLUMN product_default_code CHAR
        ALTER TABLE pos_order_line ADD COLUMN product_default_code CHAR
        """
        sql = """
            WITH raw_rows AS (
                SELECT pp.default_code,
                    tb.id
                FROM product_product pp
                    JOIN {table_name} tb ON tb.product_id = pp.id
                WHERE pp.default_code NOTNULL AND tb.product_default_code ISNULL
                LIMIT {limit}
            )
            UPDATE {table_name} d
            SET product_default_code = raw_rows.default_code
            FROM raw_rows
            WHERE d.id = raw_rows.id
        """.format(
            table_name=table_name, limit=limit
        )
        self._cr.execute(sql)
