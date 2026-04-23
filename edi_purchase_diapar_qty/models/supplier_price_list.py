from odoo import models


class SupplierPriceList(models.Model):
    _inherit = "supplier.price.list"

    def _get_price_field(self):
        return "base_price"
