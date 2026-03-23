from odoo import models
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def button_validate(self):
        for picking in self.filtered("pos_order_id"):
            for move_line in picking.move_line_ids:
                product = move_line.product_id
                if not product.available_in_pos:
                    raise UserError(
                        self.env._(
                            "The product %s received should have available in pos",
                            product.name,
                        )
                    )
        return super().button_validate()
