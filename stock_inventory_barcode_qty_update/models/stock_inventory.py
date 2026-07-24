from odoo import fields, models


class StockInventory(models.Model):
    _inherit = "stock.inventory"

    scan_barcode_mode = fields.Selection(
        [("add", "Add Qty"), ("change", "Change Qty")],
        default="add",
    )
    use_latest_qty = fields.Boolean(default=True)
