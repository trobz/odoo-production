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
        lines_in_form = {line.category_id.id: line.copies for line in self.line_ids}
        lines_in_origin = {
            line.category_id.id: line.copies for line in self._origin.line_ids
        }
        GroupLine = self.env["stock.inventory.category.group.line"]
        new_lines = self.env["stock.inventory.category.group.line"]
        for categ in self.category_ids:
            cat_id = categ._origin.id
            if cat_id in lines_in_form:
                copies = lines_in_form[cat_id]
            elif cat_id in lines_in_origin:
                copies = lines_in_origin[cat_id]
            else:
                copies = "2"
            new_lines |= GroupLine.new({"category_id": categ.id, "copies": copies})
        self.line_ids = new_lines
