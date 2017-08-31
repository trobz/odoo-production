# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

from openerp import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    scale_logo_code = fields.Char(compute="_compute_product_scale_logo_code",
                                  string="Scale Logo Code", store=True)

    @api.depends("label_ids")
    def _compute_product_scale_logo_code(self):
        '''
        @Function to compute the value for logo code
        '''
        for product in self:
            product.scale_logo_code = product.label_ids and \
                product.label_ids[0].scale_logo_code or '1'
