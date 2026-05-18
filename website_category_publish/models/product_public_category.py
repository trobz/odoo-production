# Copyright 2020 Tecnativa - Alexandre Díaz
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models


class ProductPublicCategory(models.Model):
    _name = "product.public.category"
    _inherit = ["product.public.category", "website.published.mixin"]

    def write(self, vals):
        res = super().write(vals)
        if "is_published" in vals:
            for category in self:
                children_to_sync = category.child_id.filtered(
                    lambda child, category=category: child.is_published
                    != category.is_published
                )
                children_to_sync.write({"is_published": category.is_published})
        return res
