from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    pos_discount_by_category = fields.Boolean(
        related="pos_config_id.discount_by_category",
        readonly=False,
    )
    pos_discount_category_ids = fields.Many2many(
        related="pos_config_id.discount_category_ids",
        readonly=False,
    )
