from odoo import models


class ReportGrossMarginXlsx(models.AbstractModel):
    _inherit = "report.report_xlsx.abstract"
    _name = "report.report_gross_margin_xlsx"
    _description = "Gross Margin XLSX Report"

    def generate_xlsx_report(self, workbook, data, objects):
        wizard = objects[0]
        report_data = {
            "workbook": workbook,
            "sheet": workbook.add_worksheet(),
            "row_pos": 0,
            "formats": {},
        }
        self._define_formats(report_data)
        self._write_report_header(report_data, wizard)
        self._write_report_content(report_data, wizard)

    def _define_formats(self, report_data):
        workbook = report_data["workbook"]
        currency = self.env.company.currency_id
        currency_format = f"#,##0.00 {'{symbol}'}".format(symbol=currency.symbol)
        percent_format = "#,##0.00%"

        report_data["formats"]["default"] = workbook.add_format(
            {"font_size": 11, "valign": "vcenter", "text_wrap": True}
        )
        report_data["formats"]["bold"] = workbook.add_format(
            {"font_size": 11, "bold": True, "valign": "vcenter"}
        )
        report_data["formats"]["title"] = workbook.add_format(
            {"font_size": 14, "bold": True, "bg_color": "#5b9bd5", "valign": "vcenter"}
        )
        report_data["formats"]["period"] = workbook.add_format(
            {"font_size": 12, "bold": True, "bg_color": "#00b0f0", "valign": "vcenter"}
        )
        report_data["formats"]["number"] = workbook.add_format(
            {"font_size": 11, "valign": "vcenter"}
        )
        report_data["formats"]["number"].set_num_format(currency_format)
        report_data["formats"]["percent"] = workbook.add_format(
            {"font_size": 11, "valign": "vcenter"}
        )
        report_data["formats"]["percent"].set_num_format(percent_format)

        sheet = report_data["sheet"]
        sheet.set_default_row(20)
        sheet.set_column("A:A", 40)
        sheet.set_column("B:C", 20)

    def _write_report_header(self, report_data, wizard):
        sheet = report_data["sheet"]
        formats = report_data["formats"]

        sheet.merge_range(
            0, 0, 0, 2, self.env._("GROSS MARGIN REPORT"), formats["title"]
        )

        from_date = wizard.from_date.strftime("%d/%m/%Y %H:%M:%S")
        to_date = wizard.to_date.strftime("%d/%m/%Y %H:%M:%S")
        sheet.merge_range(1, 0, 1, 2, f"{from_date} - {to_date}", formats["period"])
        report_data["row_pos"] = 3

    def _write_report_content(self, report_data, wizard):
        sheet = report_data["sheet"]
        formats = report_data["formats"]
        r = report_data["row_pos"]
        datas = wizard.get_datas()
        totals = self._compute_totals(datas)

        row_sales = r
        sheet.write(r, 0, self.env._("Sales"), formats["bold"])
        sheet.write(r, 1, totals["pre_tax_net_sales"], formats["number"])
        sheet.write_formula(r, 2, f"=B{r + 1}/B{r + 1}", formats["percent"])
        r += 2

        sheet.write(r, 0, self.env._("Beginning inventory"), formats["bold"])
        sheet.write(r, 1, totals["inventory_value_beginning"], formats["number"])
        r += 1

        sheet.write(r, 0, self.env._("Purchases"), formats["bold"])
        sheet.write(r, 1, totals["net_purchases"], formats["number"])
        r += 1

        sheet.write(r, 0, self.env._("Goods available for sale"), formats["bold"])
        sheet.write(r, 1, totals["total_available"], formats["number"])
        r += 1

        sheet.write(r, 0, self.env._("End inventory"), formats["bold"])
        sheet.write(r, 1, totals["inventory_value_ending"], formats["number"])
        r += 1

        sheet.write(r, 0, self.env._("Cost of goods sold"), formats["bold"])
        sheet.write(r, 1, totals["cogs"], formats["number"])
        sheet.write_formula(r, 2, f"=B{r + 1}/B{row_sales + 1}", formats["percent"])
        r += 2

        sheet.write(r, 0, self.env._("Gross margin"), formats["bold"])
        sheet.write(r, 1, totals["gross_margin"], formats["number"])
        sheet.write_formula(r, 2, f"=B{r + 1}/B{row_sales + 1}", formats["percent"])
        r += 2

        sheet.write(r, 0, self.env._("Product categories:"), formats["default"])
        r += 1

        for line in datas:
            sheet.write(r, 0, line["category"], formats["default"])
            r += 1

    def _compute_totals(self, datas):
        return {
            "pre_tax_net_sales": sum(d.get("pre_tax_net_sales", 0) for d in datas),
            "inventory_value_beginning": sum(
                d.get("inventory_value_beginning", 0) for d in datas
            ),
            "net_purchases": sum(d.get("net_purchases", 0) for d in datas),
            "total_available": sum(d.get("total_available", 0) for d in datas),
            "inventory_value_ending": sum(
                d.get("inventory_value_ending", 0) for d in datas
            ),
            "cogs": sum(d.get("cogs", 0) for d in datas),
            "gross_margin": sum(d.get("gross_margin", 0) for d in datas),
        }
