# -*- coding: utf-8 -*-

from openerp import api, fields, models


class ProductSupplierinfo(models.Model):
    _inherit = 'product.supplierinfo'

    is_product_active = fields.Boolean(
        'Active', related="product_tmpl_id.active", store=True)
