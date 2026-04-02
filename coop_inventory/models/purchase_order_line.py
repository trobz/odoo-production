from odoo import models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    def _product_id_change(self):
        res = super()._product_id_change()
        if self.product_id and not self.product_id.is_storable:
            self.product_packaging_id = False
            self.price_policy = "uom"
        return res

    def _prepare_stock_moves(self, picking):
        self.ensure_one()
        if not self.product_id.is_storable:
            return []
        return super()._prepare_stock_moves(picking)
