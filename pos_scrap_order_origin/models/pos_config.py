# Copyright (C) Nguyen Minh Chien (chien@trobz.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

from odoo import models, fields, api


class PosConfig(models.Model):
    _inherit = 'pos.config'

    scrap_origin_ids = fields.Many2many(
        comodel_name="stock.scrap.origin"
    )
