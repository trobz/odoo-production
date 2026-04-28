# Copyright (C) Trobz (<https://trobz.com/>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class PosConfig(models.Model):
    _inherit = "pos.config"

    scrap_reason_tag_ids = fields.Many2many(
        comodel_name="stock.scrap.reason.tag",
        string="Scrap Reason Tags",
    )
