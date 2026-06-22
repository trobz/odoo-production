# Copyright 2019 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models
from odoo.osv import expression
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF

from odoo.addons.report_xlsx_helper.report.report_xlsx_format import (
    FORMATS,
    XLS_HEADERS,
)

_logger = logging.getLogger(__name__)


class StockInventoryValuationReport(models.TransientModel):
    _inherit = "report.stock.inventory.valuation.report"

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
                "standard_price": product.avg_cost,
                "stock_value": product.value_svl,
                "cost_method": product.cost_method,
                "categ_name": product.categ_id.name,
            }
            results |= results.new(vals)
        self.results = results

    def get_date_context(self):
        self.ensure_one()
        res = self.inventory_datetime
        if res:
            res = fields.Datetime.context_timestamp(self, res).strftime(DTF)
        return res


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
        return 7

    def _get_ws_params(self, wb, data, objects):
        stock_inventory_valuation_template = self._get_wanted_list()

        ws_params = {
            "ws_name": self.env._("Inventory Valuation Report"),
            "generate_ws_method": "_inventory_valuation_report",
            "title": self.env._("Inventory Valuation Report"),
            "wanted_list": [
                k for k in sorted(stock_inventory_valuation_template.keys())
            ],
            "col_specs": stock_inventory_valuation_template,
        }
        return [ws_params]

    def _get_render_space(self, row_pos, line):
        render_space = {
            "n": row_pos - 5,
            "name": line.name or "",
            "reference": line.reference or "",
            "barcode": line.barcode or "",
            "qty_at_date": line.qty_at_date or 0.000,
            "standard_price": line.standard_price or 0.00,
            "stock_value": line.stock_value or 0.00,
            "categ_name": line.categ_name,
        }
        return render_space

    def _inventory_valuation_report(self, wb, ws, ws_params, data, objects):
        ws.set_portrait()
        ws.fit_to_pages(1, 0)
        ws.set_header(XLS_HEADERS["xls_headers"]["standard"])
        ws.set_footer(XLS_HEADERS["xls_footers"]["standard"])
        self._set_column_width(ws, ws_params)

        row_pos = 0
        row_pos = self._write_ws_title(ws, row_pos, ws_params, True)

        for o in objects:
            ws.write_row(
                row_pos,
                0,
                [self.env._("Date"), self.env._("Partner"), self.env._("Tax ID")],
                FORMATS["format_theader_blue_center"],
            )
            report_date = o.get_date_context()
            ws.write_row(row_pos + 1, 0, [report_date or ""])
            ws.write_row(
                row_pos + 1,
                1,
                [o.company_id.name or "", o.company_id.vat or ""],
                FORMATS["format_tcell_center"],
            )

            row_pos += 3
            row_pos = self._write_line(
                ws,
                row_pos,
                ws_params,
                col_specs_section="header",
                default_format=FORMATS["format_theader_blue_center"],
            )
            ws.freeze_panes(row_pos, 0)

            total = 0.00
            for line in o.results:
                row_pos = self._write_line(
                    ws,
                    row_pos,
                    ws_params,
                    col_specs_section="data",
                    render_space=self._get_render_space(row_pos, line),
                    default_format=FORMATS["format_tcell_left"],
                )
                total += line.stock_value

            ws.write(
                row_pos,
                self._get_column_total_index(),
                total,
                FORMATS["format_theader_blue_amount_right"],
            )
