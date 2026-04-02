# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models
from odoo.osv import expression


class PurchaseBillUnion(models.Model):
    _inherit = "purchase.bill.union"

    @api.model
    def _search_display_name(self, operator, value):
        if value:
            domain = [
                "|",
                ("name", operator, value),
                ("reference", operator, value),
            ]
            return expression.AND([super()._search_display_name(operator, ""), domain])
        return super()._search_display_name(operator, value)
