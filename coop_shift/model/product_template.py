from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    shift_ok = fields.Boolean(
        "Shift Subscription",
        help="""Determine if a product needs to create
        automatically a shift registration at the confirmation of a sales
        order line.""",
    )
    shift_type_id = fields.Many2one(
        "shift.type",
        string="Type of Shift",
        help="""Select shift type so when
        we use this product in sales order lines, it will filter shifts of
        this type only.""",
    )

    @api.onchange("type", "shift_ok")
    def onchange_shift_ok(self):
        if self.shift_ok:
            self.type = "service"
            self.sale_ok = False
            self.purchase_ok = False
            self.service_tracking = "event"
