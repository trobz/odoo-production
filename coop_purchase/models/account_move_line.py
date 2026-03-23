from odoo import api, fields, models


class AccountInvoiceLine(models.Model):
    _inherit = "account.move.line"

    base_price = fields.Monetary(
        currency_field="currency_id",
    )
    product_default_code = fields.Char(
        string="Internal Reference", related="product_id.default_code", store=True
    )

    @api.onchange("product_id")
    def _onchange_product_id(self):
        if (
            self.move_id
            and self.move_id.move_type in ("in_invoice", "in_refund")
            and self.product_id
        ):
            suppliers = self.product_id.seller_ids.filtered(
                lambda x: x.partner_id == self.partner_id
            )
            if suppliers:
                self.discount = suppliers[0].discount
                self.base_price = suppliers[0].base_price
                self.price_unit = suppliers[0].price
        return
