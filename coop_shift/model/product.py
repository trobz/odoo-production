from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    shift_ticket_ids = fields.One2many("shift.ticket", "product_id")

    @api.onchange("type", "shift_ok")
    def onchange_shift_ok(self):
        """Redirection, inheritance mechanism hides the method on the model"""
        if self.shift_ok:
            self.type = "service"
            self.sale_ok = False
            self.purchase_ok = False
            self.service_tracking = "event"
