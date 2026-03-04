# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockInventory(models.Model):
    _inherit = "stock.inventory"

    category_group_line_id = fields.Many2one(
        "stock.inventory.category.group.line",
        string="Category Group",
    )

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
