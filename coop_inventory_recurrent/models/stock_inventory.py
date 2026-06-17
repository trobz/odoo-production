# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models
from odoo.exceptions import ValidationError


class StockInventory(models.Model):
    _inherit = "stock.inventory"

    category_group_line_id = fields.Many2one(
        "stock.inventory.category.group.line",
        string="Category Group",
    )
    exhausted = fields.Boolean(
        string="Include Exhausted Products",
        default=True,
        help="If enabled, products in the category with no stock will also be "
        "included in the inventory adjustment.",
    )

    def action_state_to_in_progress(self):
        if self.product_selection != "category" or not self.category_id:
            return super().action_state_to_in_progress()

        self.ensure_one()
        location_op = "child_of" if not self.exclude_sublocation else "in"
        search_filter = [
            ("location_id", location_op, self.location_ids.ids),
            ("to_do", "=", True),
            "|",
            ("product_id.categ_id", "=", self.category_id.id),
            ("product_id.categ_id", "in", self.category_id.child_id.ids),
        ]
        quants = self.env["stock.quant"].search(search_filter)
        if quants:
            inventory_ids = self.env["stock.inventory"].search(
                [("stock_quant_ids", "in", quants.ids), ("state", "=", "in_progress")]
            )
            if inventory_ids:
                blocking_names = ", ".join(inventory_ids.mapped("name"))
                names = self._get_quant_joined_names(quants, "location_id")
                raise ValidationError(
                    self.env._(
                        "There's already an Adjustment in Process "
                        "using one requested Location: %(names)s. "
                        "Blocking adjustments: %(blocking_names)s",
                        names=names,
                        blocking_names=blocking_names,
                    )
                )

        quants = self._get_quants(self.location_ids)
        if self.exhausted:
            quants |= self._create_zero_qty_quants(quants)
        self.write(
            {
                "state": "in_progress",
                "stock_quant_ids": [(6, 0, quants.ids)],
            }
        )
        quants.write(
            {
                "to_do": True,
                "user_id": self.responsible_id or self.env.user,
                "inventory_date": self.date,
                "current_inventory_id": self.id,
            }
        )

    def _create_zero_qty_quants(self, existing_quants):
        """Create quants with qty=0 for active products in the category
        that have no quants in the inventory locations."""
        self.ensure_one()
        existing_product_ids = existing_quants.mapped("product_id").ids
        missing_products = self.env["product.product"].search(
            [
                ("categ_id", "=", self.category_id.id),
                ("id", "not in", existing_product_ids),
                ("is_storable", "=", "True"),
            ]
        )
        if not missing_products:
            return self.env["stock.quant"]
        location = self.location_ids[0]
        new_quants = self.env["stock.quant"]
        for product in missing_products:
            quant = (
                self.env["stock.quant"]
                .sudo()
                .create(
                    {
                        "product_id": product.id,
                        "location_id": location.id,
                        "quantity": 0,
                    }
                )
            )
            new_quants |= quant
        return new_quants

    def get_copi_variants(self):
        res0 = []
        res1 = []
        res2 = []
        for inventory in self:
            line = inventory.category_group_line_id
            if line and line.copies in ("1", "2"):
                res1.append(
                    {
                        "obj": inventory,
                        "extra_title": self.env._("First List"),
                        "color": "",
                    }
                )
            if line and line.copies == "2":
                res2.append(
                    {
                        "obj": inventory,
                        "extra_title": self.env._("Second List"),
                        "color": "green",
                    }
                )
            if not line or not line.copies:
                res0.append({"obj": inventory})
        return res0 + res1 + res2

    def check_duplex(self):
        self.ensure_one()
        first_page_nb = int(
            self.env["ir.config_parameter"].sudo().get_param("report.first_page_nb", 35)
        )
        est_line_nb = int(
            self.env["ir.config_parameter"].sudo().get_param("report.est_line_nb", 39)
        )
        page_nb = 1
        line_nb = len(self.stock_quant_ids) - first_page_nb
        if line_nb > 0:
            page_nb += int(line_nb / est_line_nb)
            if line_nb % est_line_nb > 0:
                page_nb += 1
        return page_nb % 2 != 0
