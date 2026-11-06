# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


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

    def action_print_report_inventory(self):
        self.ensure_one()
        if self.category_group_line_id:
            return self.env.ref(
                "coop_inventory_recurrent.action_report_inventory_recurrent"
            ).report_action(self)
        return super().action_print_report_inventory()

    def action_state_to_in_progress(self):
        res = super().action_state_to_in_progress()
        if (
            self.product_selection != "category"
            or not self.category_id
            or not self.exhausted
        ):
            return res

        quants = self.stock_quant_ids
        new_quants = self._create_zero_qty_quants(quants)
        new_quants.write(
            {
                "to_do": True,
                "user_id": self.responsible_id or self.env.user,
                "inventory_date": self.date,
                "current_inventory_id": self.id,
            }
        )
        self.stock_quant_ids |= new_quants
        return res

    def _create_zero_qty_quants(self, existing_quants):
        """Create quants with qty=0 for active products in the category
        that have no quants in the inventory locations."""
        self.ensure_one()
        existing_product_ids = existing_quants.mapped("product_id").ids
        missing_products = self.env["product.product"].search(
            [
                ("categ_id", "=", self.category_id.id),
                ("id", "not in", existing_product_ids),
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
