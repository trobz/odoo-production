from odoo import fields, models


class ProductCategory(models.Model):
    _inherit = "product.category"

    type = fields.Selection(
        [("view", "View"), ("normal", "Normal")],
        string="Category Type",
        default="normal",
    )
