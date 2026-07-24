from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _compute_payment_term_id(self):
        super()._compute_payment_term_id()
        orders = self.filtered(
            lambda o: o.website_id
            and o.website_id.payment_term_id
            and not o.partner_id.property_payment_term_id
        )
        if not orders:
            return
        for order in orders:
            order.payment_term_id = order.website_id.payment_term_id
