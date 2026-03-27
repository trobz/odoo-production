# Copyright 2019 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockInventoryValuationView(models.TransientModel):
    _inherit = "stock.inventory.valuation.view"

    categ_name = fields.Char()
