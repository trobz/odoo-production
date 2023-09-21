# Copyright (C) Nguyen Minh Chien (chien@trobz.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

from odoo import models, fields, api


class PosConfig(models.Model):
    _inherit = 'pos.config'

    scrap_order_option = fields.Selection([
        ("no", "No Scrap Order"),
        ("onhand", "Create and validate Scrap Order for product has stock only"),
        ("always", "Always create Scrap Order, validate if has stock")
    ], default="onhand")
