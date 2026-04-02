# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

from odoo import fields, models


class StockQuant(models.Model):
    _inherit = "stock.quant"

    product_default_code = fields.Char(
        string="Internal Reference", related="product_id.default_code", store=True
    )
