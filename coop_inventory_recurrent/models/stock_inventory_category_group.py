# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

from odoo import api, fields, models


class StockInventoryCategoryGroup(models.Model):
    _name = "stock.inventory.category.group"
    _description = "Category Group"

    @api.model
    def _default_location_id(self):
        return self.env.ref("stock.stock_location_stock", raise_if_not_found=False)

    name = fields.Char(required=True)
    location_id = fields.Many2one(
        "stock.location",
        required=True,
        domain=[("usage", "=", "internal")],
        default=_default_location_id,
    )
    category_ids = fields.Many2many("product.category", string="Product categories")
    line_ids = fields.One2many("stock.inventory.category.group.line", "group_id")

    @api.onchange("category_ids")
    def onchange_category_ids(self):
        lines_by_categ = {line.category_id.id: line for line in self._origin.line_ids}
        lines_by_categ.update({line.category_id.id: line for line in self.line_ids})
        GroupLine = self.env["stock.inventory.category.group.line"]
        new_lines = self.env["stock.inventory.category.group.line"]
        for categ in self.category_ids:
            existing = lines_by_categ.get(categ.id)
            new_lines |= (
                existing
                if existing
                else GroupLine.new({"category_id": categ.id, "copies": "2"})
            )
        self.line_ids = new_lines
