# Copyright 2019 Eficent Business and IT Consulting Services, S.L.
# Copyright 2019 Aleph Objects, Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockQuant(models.Model):
    _inherit = "stock.quant"

    product_name = fields.Char(
        compute="_compute_product_name",
        store=True,
        translate=True,
    )
    package_qty = fields.Float(compute="_compute_package_qty")

    @api.depends("product_id", "product_id.name")
    def _compute_product_name(self):
        langs = self.env["res.lang"].search([("active", "=", True)]).mapped("code")
        for quant in self:
            for lang in langs:
                quant.with_context(
                    lang=lang
                ).product_name = quant.product_id.with_context(lang=lang).name

    @api.depends("product_id")
    def _compute_package_qty(self):
        for quant in self:
            seller = quant.product_id._select_seller(quantity=1)
            quant.package_qty = seller.package_qty or 1.0
