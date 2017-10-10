# -*- coding: utf-8 -*-

from openerp import fields, models
import openerp.addons.decimal_precision as dp


class ProductProduct(models.Model):
    _inherit = 'product.product'

    volume = fields.Float(digits=dp.get_precision('Volume'))
