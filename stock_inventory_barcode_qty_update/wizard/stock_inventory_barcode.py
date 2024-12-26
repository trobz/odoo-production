# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import api, fields, models
import odoo.addons.decimal_precision as dp

class StockInventoryBarcode(models.TransientModel):
    _inherit = 'stock.inventory.barcode'

    prev_product_id = fields.Many2one(
        'product.product', string='Prev Product'
    )
    scan_barcode_mode = fields.Selection([
        ("add", "Add Qty"),
        ("change", "Change Qty")
    ], related="inventory_id.scan_barcode_mode")

    new_change_qty = fields.Float(
        digits=dp.get_precision('Product Unit of Measure')
    )
    use_latest_qty = fields.Boolean(default=True)

    @api.onchange('product_id')
    def product_id_change(self):
        # Could not override `def update_wiz_screen()` (and re-update change_qty)
        # Because def update_wiz_screen() is called twice when changing
        # product_id and uom_id
        res = super().product_id_change()
        if not self.product_id or self.scan_barcode_mode != "add":
            return res
        silo = self.env['stock.inventory.line']
        ilines = silo.search([
            ('inventory_id', '=', self.inventory_id.id),
            ('product_id', '=', self.product_id.id),
            ('location_id', '=', self.location_id.id),
            ('prod_lot_id', '=', self.lot_id and self.lot_id.id or False),
        ])
        if not self.prev_product_id and self.use_latest_qty and len(ilines) == 1:
            self.new_change_qty = ilines[0].product_qty
            self.prev_product_id = self.product_id

        if self.prev_product_id != self.product_id:
            self.new_change_qty = 1
            self.prev_product_id = self.product_id
            if self.use_latest_qty and len(ilines) == 1:
                self.new_change_qty += ilines[0].product_qty
        else:
            self.new_change_qty += 1
        self.product_code = False
        return res

    @api.onchange('product_code')
    def product_code_change(self):
        res = super().product_code_change()
        # Only handle the case of scanning the same product twice
        # Because `def product_id_change(self)` does not handle this case.
        if not self.product_id or self.prev_product_id != self.product_id:
            return res
        self.new_change_qty += 1
        self.product_code = False
        return res

    def save(self):
        # Update change_qty by new_change_qty
        self.ensure_one()
        if self.scan_barcode_mode == "add":
            self.change_qty = self.new_change_qty
        return super().save()
