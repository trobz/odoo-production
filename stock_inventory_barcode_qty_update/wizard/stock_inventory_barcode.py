from odoo import api, fields, models
from odoo.exceptions import UserError


class StockInventoryBarcode(models.TransientModel):
    _inherit = "stock.inventory.barcode"

    prev_product_id = fields.Many2one("product.product", string="Prev Product")
    new_change_qty = fields.Float(digits="Product Unit of Measure")
    use_latest_qty = fields.Boolean(default=True)
    # Friendly selection mapped to/from the base boolean zero_count field.
    scan_barcode_mode = fields.Selection(
        [("add", "Add Qty"), ("change", "Change Qty")],
        compute="_compute_scan_barcode_mode",
        inverse="_inverse_scan_barcode_mode",
    )

    @api.depends("zero_count")
    def _compute_scan_barcode_mode(self):
        for wiz in self:
            wiz.scan_barcode_mode = "add" if wiz.zero_count else "change"

    def _inverse_scan_barcode_mode(self):
        for wiz in self:
            wiz.zero_count = wiz.scan_barcode_mode == "add"

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if "product_tracking" not in vals and vals.get("product_id"):
                product = self.env["product.product"].browse(vals["product_id"])
                vals["product_tracking"] = product.tracking or "none"
        return super().create(vals_list)

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        if self._context.get("active_model") == "stock.inventory":
            inv_id = self._context.get("active_id")
            if inv_id:
                inv = self.env["stock.inventory"].browse(inv_id)
                if inv.exists():
                    res["zero_count"] = inv.scan_barcode_mode == "add"
                    res["use_latest_qty"] = inv.use_latest_qty
        return res

    def _get_current_inventory_qty(self):
        domain = [
            ("current_inventory_id", "=", self.inventory_id.id),
            ("product_id", "=", self.product_id.id),
            ("location_id", "=", self.location_id.id),
            ("lot_id", "=", self.lot_id.id if self.lot_id else False),
        ]
        quant = self.env["stock.quant"].search(domain, limit=1)
        return quant.inventory_quantity if quant else 0.0

    @api.onchange("product_id")
    def product_id_change(self):
        res = super().product_id_change()
        if not self.product_id or self.scan_barcode_mode != "add":
            return res
        current_qty = self._get_current_inventory_qty()
        # Mirrors foodcoop12 logic: initialise new_change_qty on the very first
        # scan, then increment for same-product re-scans or reset on product change.
        if not self.prev_product_id and self.use_latest_qty:
            # First scan in the session: seed from existing DB inventory qty.
            self.new_change_qty = current_qty
            self.prev_product_id = self.product_id
        if self.prev_product_id != self.product_id:
            self.new_change_qty = 1.0
            self.prev_product_id = self.product_id
            if self.use_latest_qty:
                self.new_change_qty += current_qty
        else:
            self.new_change_qty += 1.0
        return res

    @api.onchange("product_code")
    def product_code_change(self):
        if not self.product_code:
            return
        code = self.product_code
        result = super().product_code_change()
        if not self.product_code:
            # Base found a product and cleared product_code. If this is a
            # re-scan of the same product in add mode, increment our counter
            # (product_id_change will handle new-product scans via the chain).
            if (
                self.scan_barcode_mode == "add"
                and self.prev_product_id == self.product_id
            ):
                self.new_change_qty += 1.0
            return result
        # No product matched — fall back to lot/serial search.
        if self.product_id and self.product_id.tracking != "none" and not self.lot_id:
            lot = self.env["stock.lot"].search(
                [("name", "=", code), ("product_id", "=", self.product_id.id)],
                limit=1,
            )
            if lot:
                self.lot_id = lot
                self.product_code = False
                return
        return result

    def save(self):
        # Ensure quant_id is populated when save is called directly (e.g., tests).
        if not self.quant_id and self.product_id and self.location_id:
            self.update_wiz_screen({})
        if self.zero_count:
            if not self.quant_id:
                raise UserError(self.env._("No related quant"))
            # SET absolute quantity (same approach as foodcoop12).
            # new_change_qty already includes the starting qty (when use_latest_qty)
            # plus the number of scans, so we write it directly.
            qty = self.new_change_qty if self.new_change_qty else self.add_qty
            self.quant_id.inventory_quantity = qty
            return {
                "name": self.env._("Stock Inventory Barcode Wizard"),
                "type": "ir.actions.act_window",
                "res_model": "stock.inventory.barcode",
                "view_mode": "form",
                "nodestroy": True,
                "target": "new",
                "context": self._context,
            }
        # Change mode: delegate to base (sets inventory_quantity = change_qty).
        return super().save()
