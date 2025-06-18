# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockInventoryValuationView(models.TransientModel):
    _inherit = 'stock.inventory.valuation.view'

    income_analytic_account = fields.Char()


class StockInventoryValuationReport(models.TransientModel):
    _inherit = 'report.stock.inventory.valuation.report'

    def _get_result_line(self, product, standard_price):
        """Override to add the analytic account from product or product category."""
        line = super()._get_result_line(product, standard_price)
        line['income_analytic_account'] = (
            product.income_analytic_account_id.name or
            product.categ_id.income_analytic_account_id.name
        )
        return line
