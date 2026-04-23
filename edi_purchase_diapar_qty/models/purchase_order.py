from odoo import models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def _consolidate_product_qty(self, order_line):
        if order_line.price_policy == "package":
            return order_line.product_packaging_qty
        return super()._consolidate_product_qty(order_line)
