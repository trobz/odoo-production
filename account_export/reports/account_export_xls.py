from odoo import fields, models


class AccountExportReportXLS(models.AbstractModel):
    _name = "report.account_export.report_xls"
    _inherit = "report.report_xlsx.abstract"
    _description = "Account Export XLS Report"

    def generate_xlsx_report(self, workbook, data, export):
        report_data = {
            "workbook": workbook,
            "sheet": workbook.add_worksheet(),
            "row_pos": 0,
            "formats": {},
        }
        self._define_formats(report_data, export)
        self._write_report_header(report_data, export)
        self._write_report_content(report_data, export)

    def _define_formats(self, report_data, export):
        workbook = report_data["workbook"]
        currency = self.env.company.currency_id
        currency_format = f"#,##0.00 {currency.symbol}"
        date_format = "dd/mm/yyyy"

        report_data["formats"]["default"] = workbook.add_format(
            {"font_size": 11, "valign": "vcenter", "text_wrap": True}
        )
        report_data["formats"]["bold"] = workbook.add_format(
            {"font_size": 11, "bold": True, "valign": "vcenter"}
        )
        report_data["formats"]["title"] = workbook.add_format(
            {"font_size": 14, "bold": True, "bg_color": "#5b9bd5", "valign": "vcenter"}
        )
        report_data["formats"]["header"] = workbook.add_format(
            {"font_size": 12, "bold": True, "bg_color": "#ffd966", "valign": "vcenter"}
        )
        report_data["formats"]["number"] = workbook.add_format(
            {"font_size": 11, "valign": "vcenter"}
        )
        report_data["formats"]["number"].set_num_format(currency_format)
        report_data["formats"]["date"] = workbook.add_format(
            {"font_size": 11, "valign": "vcenter"}
        )
        report_data["formats"]["date"].set_num_format(date_format)
        report_data["formats"]["right"] = workbook.add_format(
            {"font_size": 11, "valign": "vcenter", "align": "right"}
        )

        sheet = report_data["sheet"]
        sheet.set_landscape()
        sheet.fit_to_pages(1, 0)
        sheet.set_default_row(20)
        sheet.set_row(0, 30)
        sheet.set_column("A:A", 15)
        sheet.set_column("B:B", 18)
        sheet.set_column("C:C", 18)
        sheet.set_column("D:D", 12)
        sheet.set_column("E:E", 12)
        sheet.set_column("F:F", 25)
        sheet.set_column("G:G", 15)
        sheet.set_column("H:H", 15)
        sheet.set_column("I:I", 15)
        sheet.set_column("J:J", 15)
        sheet.set_column("K:K", 25)
        sheet.set_column("L:L", 15)

    def _write_report_header(self, report_data, export):
        sheet = report_data["sheet"]
        formats = report_data["formats"]

        sheet.merge_range(
            0, 0, 0, 11, self.env._("ACCOUNT EXPORT REPORT"), formats["title"]
        )

        sheet.write(1, 0, self.env._("Export Name:"), formats["bold"])
        sheet.write(1, 1, export.name, formats["default"])
        sheet.write(2, 0, self.env._("Company:"), formats["bold"])
        sheet.write(2, 1, export.company_id.name, formats["default"])
        sheet.write(3, 0, self.env._("Date:"), formats["bold"])
        sheet.write(3, 1, fields.Date.today(), formats["date"])

        report_data["row_pos"] = 5
        self._write_column_headers(report_data, export)

    def _write_column_headers(self, report_data, export):
        sheet = report_data["sheet"]
        formats = report_data["formats"]
        r = report_data["row_pos"]
        col_idx = 0
        for field in export.config_id.field_ids:
            sheet.write(r, col_idx, field.name, formats["header"])
            col_idx += 1
        report_data["row_pos"] = r + 1

    def _write_report_content(self, report_data, export):
        lines = export.get_account_move_line_data()
        r = report_data["row_pos"]

        for line in lines:
            self._write_line_data(report_data, export, line, r)
            r += 1
        report_data["row_pos"] = r

    def _write_line_data(self, report_data, export, line, row):
        sheet = report_data["sheet"]
        formats = report_data["formats"]
        columns = export.config_id._get_columns_dict()
        col_idx = 0

        for field in export.config_id.field_ids:
            col = columns.get(field.field_type)
            value = line.get(field.id, "")

            if field.field_type == "amount":
                sense_key = f"{field.id}_sense"
                sense = line.get(sense_key, "")
                if sense:
                    value = f"{sense}{value}"
                sheet.write(row, col_idx, value, formats["number"])
            elif col.get("type") == "datetime":
                sheet.write(row, col_idx, value, formats["date"])
            elif col.get("type") == "number":
                sheet.write(row, col_idx, value, formats["number"])
            else:
                sheet.write(row, col_idx, value, formats["default"])
            col_idx += 1
