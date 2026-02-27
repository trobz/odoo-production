from odoo import models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    def _prepare_stock_moves(self, picking):
        self.ensure_one()
        if not self.product_id.is_storable:
            return []
        return super()._prepare_stock_moves(picking)
