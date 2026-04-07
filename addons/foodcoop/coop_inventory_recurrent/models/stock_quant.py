# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockQuant(models.Model):
    _inherit = "stock.quant"

    category_group_line_id = fields.Many2one(
        "stock.inventory.category.group.line",
        string="Category Group",
        compute="_compute_category_group_line_id",
    )

    @api.depends("product_id.categ_id", "current_inventory_id")
    def _compute_category_group_line_id(self):
        GroupLine = self.env["stock.inventory.category.group.line"]
        for quant in self:
            inv_line = quant.current_inventory_id.category_group_line_id
            if inv_line:
                quant.category_group_line_id = inv_line
            else:
                quant.category_group_line_id = GroupLine.search(
                    [("category_id", "=", quant.product_id.categ_id.id)], limit=1
                )

    def get_copi_variants(self):
        res0 = []
        res1 = []
        res2 = []
        lines_seen = []
        for quant in self:
            line = quant.category_group_line_id
            if line not in lines_seen:
                lines_seen.append(line)
                quants_for_line = self.filtered(
                    lambda q, line=line: q.category_group_line_id == line
                )
                if line and line.copies in ("1", "2"):
                    res1.append(
                        {
                            "obj": quants_for_line,
                            "extra_title": self.env._("First List"),
                            "color": "",
                        }
                    )
                if line and line.copies == "2":
                    res2.append(
                        {
                            "obj": quants_for_line,
                            "extra_title": self.env._("Second List"),
                            "color": "green",
                        }
                    )
                if not line or not line.copies:
                    res0.append({"obj": quants_for_line})
        return res0 + res1 + res2

    def check_duplex(self):
        first_page_nb = int(
            self.env["ir.config_parameter"].sudo().get_param("report.first_page_nb", 35)
        )
        est_line_nb = int(
            self.env["ir.config_parameter"].sudo().get_param("report.est_line_nb", 39)
        )
        page_nb = 1
        line_nb = len(self) - first_page_nb
        if line_nb > 0:
            page_nb += int(line_nb / est_line_nb)
            if line_nb % est_line_nb > 0:
                page_nb += 1
        return page_nb % 2 != 0
