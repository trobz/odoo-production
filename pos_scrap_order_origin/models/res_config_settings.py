# Copyright (C) Trobz (<https://trobz.com/>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    scrap_reason_tag_ids = fields.Many2many(
        related="pos_config_id.scrap_reason_tag_ids",
        readonly=False,
    )
