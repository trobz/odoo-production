# Copyright (C) 2024-Today: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ReportStockInventoryGroup(models.AbstractModel):
    _name = "report.coop_inventory.report_stock_inventory_group"
    _description = "Inventory Count Sheet Report"

    @api.model
    def _get_report_values(self, docids, data=None):
        inventories = self.env["stock.inventory"].browse(docids)
        quants = inventories.mapped("stock_quant_ids")
        return {
            "doc_ids": quants.ids,
            "doc_model": "stock.quant",
            "docs": quants,
            "report_date": inventories[0].date or fields.Datetime.now(),
        }
