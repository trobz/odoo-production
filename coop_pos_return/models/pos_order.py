from odoo import models
from odoo.exceptions import UserError


class PoSOrder(models.Model):
    _inherit = "pos.order"

    def _refund(self):
        refund_orders = self.env["pos.order"]
        try:
            refund_orders = super()._refund()
        except UserError:
            current_session = self.env["pos.session"].search(
                [("state", "!=", "closed"), ("user_id", "=", self.env.uid)], limit=1
            )
            if not current_session:
                raise UserError(
                    self.env._(
                        "To return product(s), you need to open a session "
                        "that will be used to register the refund"
                    )
                ) from None
            for order in self:
                refund_order = order.copy(order._prepare_refund_values(current_session))
                for line in order.lines:
                    PosOrderLineLot = self.env["pos.pack.operation.lot"]
                    for pack_lot in line.pack_lot_ids:
                        PosOrderLineLot += pack_lot.copy()
                    line.copy(line._prepare_refund_data(refund_order, PosOrderLineLot))
                refund_orders |= refund_order
            refund_orders._compute_prices()
        return refund_orders

    def action_partial_refund(self):
        try:
            action = super().action_partial_refund()
        except UserError:
            current_session = self.env["pos.session"].search(
                [("state", "!=", "closed"), ("user_id", "=", self.env.uid)], limit=1
            )
            if not current_session:
                raise UserError(
                    self.env._(
                        "To return product(s), you need to open a session "
                        "that will be used to register the refund"
                    )
                ) from None
        action = self.env["ir.actions.actions"]._for_xml_id(
            "pos_order_return.action_pos_partial_return_wizard"
        )
        return action
