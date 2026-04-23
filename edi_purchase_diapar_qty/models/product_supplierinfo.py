from odoo import models


class SupplierInfo(models.Model):
    _inherit = "product.supplierinfo"

    def _get_price_field(self):
        return "base_price"
