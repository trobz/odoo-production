from odoo import models
from odoo.tools import SQL


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    def init(self):
        res = super().init()
        # Create index for better performance on stock move line queries
        self.env.cr.execute(
            SQL("""
            CREATE INDEX IF NOT EXISTS idx_sml_product_write_date
            ON stock_move_line (product_id, write_date DESC)
        """)
        )
        return res
