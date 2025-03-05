# -*- coding: utf-8 -*-

from odoo import api, fields, models


class PosConfig(models.Model):
    _inherit = 'pos.config'

    discount_by_category = fields.Boolean(
        string="Apply Discount on Product Categories",
        default=False
    )
    discount_category_ids = fields.Many2many(
        "product.category",
        help="If no category is set, apply discount for all",
        string="Discounted product categories",
    )
    discount_category_all_ids = fields.Many2many(
        "product.category",
        relation="pos_config_discount_category_all_rel",
        compute="_compute_discount_category_all_ids",
        store=True,
    )
    @api.depends('discount_category_ids')
    def _compute_discount_category_all_ids(self):
        for record in self:
            categories = self.env['product.category']
            if record.discount_category_ids:
                categories = self.env['product.category'].search([
                    ('id', 'child_of', record.discount_category_ids.ids)
                ])
            record.discount_category_all_ids = categories
