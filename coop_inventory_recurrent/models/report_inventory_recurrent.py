# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class ReportInventoryRecurrent(models.AbstractModel):
    _name = "report.coop_inventory_recurrent.report_inventory_new_layout"
    _description = "Recurrent Inventory Report"

    def _get_report_values(self, docids, data=None):
        inventories = self.env["stock.inventory"].browse(docids)
        quants = inventories.mapped("stock_quant_ids").sorted(
            lambda q: q.product_id.name
        )
        variants = quants.get_copi_variants()
        return {
            "docs": inventories,
            "doc_ids": inventories.ids,
            "doc_model": "stock.inventory",
            "quants": quants,
            "variants": variants,
        }
