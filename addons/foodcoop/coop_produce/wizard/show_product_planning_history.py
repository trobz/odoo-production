from odoo import Command, api, fields, models
from odoo.exceptions import UserError


class PlanificationProductHistory(models.TransientModel):
    _name = "planification.product.history"
    _description = "Product history planning"

    product_id = fields.Many2one("product.product", required=True)
    default_packaging = fields.Float(related="product_id.default_packaging")
    line_ids = fields.Many2many("order.week.planning.line", string="History")

    @api.model
    def default_get(self, fields):
        context = dict(self._context) or {}
        res = super().default_get(fields)
        line_ids = context.get("line_ids", [])
        product_id = context.get("product_id", False)
        res.update(
            {
                "product_id": product_id,
                "line_ids": [Command.set(line_ids)],
            }
        )
        return res

    def init_display_from_date(self, date):
        raise UserError(self.env._("Not yet implemented")) from None
