# Copyright (C) 2012-Today GRAP (http://www.grap.coop)
# Copyright (C) 2020-Today: Druidoo (<https://www.druidoo.io>)
# @author Julien WESTE
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class ReportPricetagBase(models.AbstractModel):
    _name = "report.coop_default_pricetag.report_pricetag_base"
    _description = "Pricetag Report"

    @api.model
    def _get_report_values(self, docids, data=None):
        if not docids:
            docids = self.env.context.get("active_ids") or []
        return self.render_html(docids)

    @api.model
    def _get_products(self, lines):
        result = []
        line_ids = self.env["product.print.wizard.line"].browse(lines)
        for line in line_ids:
            val = {}
            val["line"] = line
            val["product"] = line.product_id
            result.append(val)
        return result

    def render_html(self, docids):
        wizard = self.env["product.print.wizard"].browse(docids)
        line_ids = wizard.line_ids.ids
        product_res = self._get_products(line_ids)
        return {
            "partner_id": self.env.user.partner_id,
            "Products": product_res,
        }


class ReportPricetag(models.AbstractModel):
    _name = "report.coop_default_pricetag.report_pricetag"
    _inherit = "report.coop_default_pricetag.report_pricetag_base"
    _description = "Pricetag Report"


class ReportPricetagBarcode(models.AbstractModel):
    _name = "report.coop_default_pricetag.report_pricetag_barcode"
    _inherit = "report.coop_default_pricetag.report_pricetag_base"
    _description = "Pricetag Report (Barcode)"


class ReportPricetagVegetables(models.AbstractModel):
    _name = "report.coop_default_pricetag.report_pricetag_vegetables"
    _inherit = "report.coop_default_pricetag.report_pricetag"
    _description = "Pricetag Report (Vegetables)"


class ReportPricetagSimpleBarcode(models.AbstractModel):
    _name = "report.coop_default_pricetag.report_pricetag_simple_barcode"
    _inherit = "report.coop_default_pricetag.report_pricetag_base"
    _description = "Pricetag Report (Simple Barcode)"
