from odoo import api, models


class ReportPricetag(models.AbstractModel):
    _inherit = "report.product_print_category.report_pricetag"

    @api.model
    def _get_report_values(self, docids, data=None):
        return super(ReportPricetag, self.sudo())._get_report_values(docids, data=data)
