from odoo import api, models
from odoo.exceptions import UserError


class SaleReport(models.Model):
    _inherit = "sale.report"

    def _check_report_date_filter(self, domain):
        if not self.env.context.get("sale_report_require_date"):
            return
        has_date = any(
            isinstance(leaf, list | tuple) and len(leaf) == 3 and leaf[0] == "date"
            for leaf in (domain or [])
        )
        if not has_date:
            raise UserError(
                self.env._(
                    "Loading this report without a date filter can cause a high "
                    "server load. Please filter the data by date, ideally within "
                    "the last year or two."
                )
            )

    @api.model
    def read_group(self, domain, *args, **kwargs):
        self._check_report_date_filter(domain)
        return super().read_group(domain, *args, **kwargs)

    @api.model
    def web_search_read(self, domain, *args, **kwargs):
        self._check_report_date_filter(domain)
        return super().web_search_read(domain, *args, **kwargs)
