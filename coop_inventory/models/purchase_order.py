from odoo import models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def _create_picking(self):
        """Override to prevent creating pickings for consumable products.

        Only storable products (is_storable=True) generate a picking.
        Consumable products are intentionally excluded.

        """
        orders = self.filtered(lambda po: po.state in ("purchase", "done"))
        storable_orders = orders.filtered(
            lambda po: any(po.order_line.mapped("product_id.is_storable"))
        )
        if storable_orders:
            return super()._create_picking()
        return True
