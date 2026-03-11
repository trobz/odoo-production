from odoo import api, fields, models
from odoo.exceptions import UserError


class AccountMoveReversal(models.TransientModel):
    _inherit = "account.move.reversal"

    refund_quantity = fields.Integer(
        string="Quantity Of Shares To Refund",
        required=False,
    )
    is_capital_fundraising = fields.Boolean(
        string="Is Capital Fundraising",
        related="move_ids.is_capital_fundraising",
    )

    @api.constrains("refund_quantity")
    def _check_refund_quantity_is_positive(self):
        if self.is_capital_fundraising and self.refund_quantity <= 0:
            raise UserError(
                self.env._("Error! The refund quantity must be greater than 0.")
            )
        return True

    def refund_moves(self):
        res = super().refund_moves()
        refunds = self.new_move_ids.filtered(
            lambda move: move.move_type == "out_refund" and move.fundraising_category_id
        )
        if refunds:
            refunds.apply_refund_deficit_share(self.refund_quantity)
        return res
