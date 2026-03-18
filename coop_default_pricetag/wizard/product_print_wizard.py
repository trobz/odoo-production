# Copyright (C) 2012-Today GRAP (http://www.grap.coop)
# Copyright (C) 2020-Today: Druidoo (<https://www.druidoo.io>)
# @author Julien WESTE
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class ProductPrintWizard(models.TransientModel):
    _inherit = "product.print.wizard"

    def _get_pricetag_report(self):
        report_xmlid = "product_print_category.pricetag"
        report = self.env.ref(report_xmlid)
        if self.line_ids:
            print_category = self.line_ids[0].print_category_id
            report_name = print_category.pricetag_model_id.report_model
            if report_name:
                report2 = self.env["ir.actions.report"].search(
                    [("report_name", "=", report_name)], limit=1
                )
                if report2:
                    report = report2
        return report

    def print_report(self):
        self.ensure_one()
        data = self._prepare_data()
        report = self._get_pricetag_report()
        # Mark products as printed
        self.line_ids.mapped("product_id").write({"to_print": False})
        return report.report_action(self, data=data)
