# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models
from odoo.addons.report_xlsx_helper.report.report_xlsx_format import FORMATS
from odoo.osv import expression


class StockInventoryValuationReport(models.TransientModel):
    _inherit = "report.stock.inventory.valuation.report"

    def _get_product_analytic_distribution(self, product):
        dist_models = (
            product.analytic_distribution_model_ids
            or product.categ_id.analytic_distribution_model_ids
        )
        analytic_distribution = {}
        for model in dist_models:
            analytic_distribution.update(model.analytic_distribution or {})
        return analytic_distribution or False

    @api.depends("inventory_datetime")
    def _compute_results(self):
        self.ensure_one()
        domain = [("type", "=", "consu")]
        product_id = self.env.context.get("product_id")
        product_tmpl_id = self.env.context.get("product_tmpl_id")
        if product_id:
            domain = expression.AND([domain, [("id", "=", product_id)]])
        elif product_tmpl_id:
            domain = expression.AND(
                [domain, [("product_tmpl_id", "=", product_tmpl_id)]]
            )

        products = (
            self.env["product.product"]
            .with_context(
                to_date=self.inventory_datetime,
                company_owned=True,
                create=False,
                edit=False,
            )
            .search(domain)
        ).filtered(lambda pp: pp.quantity_svl != 0)

        results = self.env["stock.inventory.valuation.view"]
        for product in products:
            vals = {
                "name": product.with_context(display_default_code=False).display_name,
                "reference": product.default_code,
                "barcode": product.barcode,
                "qty_at_date": product.quantity_svl,
                "uom_id": product.uom_id,
                "currency_id": product.currency_id,
                "cost_currency_id": product.cost_currency_id,
                "standard_price": product.standard_price,
                "stock_value": product.value_svl,
                "cost_method": product.cost_method,
                "categ_name": product.categ_id.name,
                "analytic_distribution": self._get_product_analytic_distribution(
                    product
                ),
            }
            results |= results.new(vals)
        self.results = results


class ReportStockInventoryValuationReportXlsx(models.TransientModel):
    _inherit = "report.s_i_v_r.report_stock_inventory_valuation_report_xlsx"

    def _get_wanted_list(self):
        return {
            "1_number": {
                "header": {
                    "value": "#",
                },
                "data": {
                    "value": self._render("n"),
                },
                "width": 20,
            },
            "2_reference": {
                "header": {
                    "value": self.env._("Reference"),
                },
                "data": {
                    "value": self._render("reference"),
                },
                "width": 15,
            },
            "3_name": {
                "header": {
                    "value": self.env._("Name"),
                },
                "data": {
                    "value": self._render("name"),
                },
                "width": 36,
            },
            "4_categ_name": {
                "header": {
                    "value": self.env._("Internal Category"),
                },
                "data": {
                    "value": self._render("categ_name"),
                },
                "width": 36,
            },
            "5_barcode": {
                "header": {
                    "value": self.env._("Barcode"),
                },
                "data": {
                    "value": self._render("barcode"),
                },
                "width": 15,
            },
            "5_c_analytic_distribution": {
                "header": {
                    "value": self.env._("Analytic Distribution"),
                },
                "data": {
                    "value": self._render("analytic_distribution"),
                },
                "width": 25,
            },
            "6_qty_at_date": {
                "header": {
                    "value": self.env._("Quantity"),
                },
                "data": {
                    "value": self._render("qty_at_date"),
                    "format": FORMATS["format_tcell_amount_conditional_right"],
                },
                "width": 18,
            },
            "7_standard_price": {
                "header": {
                    "value": self.env._("Cost"),
                },
                "data": {
                    "value": self._render("standard_price"),
                    "format": FORMATS["format_tcell_amount_conditional_right"],
                },
                "width": 18,
            },
            "8_stock_value": {
                "header": {
                    "value": self.env._("Value"),
                },
                "data": {
                    "value": self._render("stock_value"),
                    "format": FORMATS["format_tcell_amount_conditional_right"],
                },
                "width": 18,
            },
        }

    def _get_column_total_index(self):
        return 8

    def _format_analytic_distribution(self, analytic_distribution):
        account_ids = [
            int(aid)
            for key in (analytic_distribution or {})
            for aid in key.split(",")
            if aid.isdigit()
        ]
        if not account_ids:
            return ""
        accounts = self.env["account.analytic.account"].browse(account_ids)
        return ", ".join(accounts.mapped("name"))

    def _get_render_space(self, row_pos, line):
        return {
            "n": row_pos - 5,
            "name": line.name or "",
            "reference": line.reference or "",
            "barcode": line.barcode or "",
            "analytic_distribution": self._format_analytic_distribution(
                line.analytic_distribution
            ),
            "qty_at_date": line.qty_at_date or 0.000,
            "standard_price": line.standard_price or 0.00,
            "stock_value": line.stock_value or 0.00,
            "categ_name": line.categ_name or "",
        }
