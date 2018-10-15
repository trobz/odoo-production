# -*- coding: utf-8 -*-

from openerp import fields, models


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    product_type = fields.Selection(
        related='product_id.type',
        store=True
    )
