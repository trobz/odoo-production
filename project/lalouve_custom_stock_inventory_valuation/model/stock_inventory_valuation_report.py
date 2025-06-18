# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from odoo import api, fields, models, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF


class ReportStockInventoryValuationReportXlsx(models.TransientModel):
    _inherit = 'report.s_i_v_r.report_stock_inventory_valuation_report_xlsx'

    def _get_wanted_list(self):
        return {
            '1_number': {
                'header': {
                    'value': '#',
                },
                'data': {
                    'value': self._render('n'),
                },
                'width': 20,
            },
            '2_reference': {
                'header': {
                    'value': _('Reference'),
                },
                'data': {
                    'value': self._render('reference'),
                },
                'width': 15,
            },
            '3_name': {
                'header': {
                    'value': _('Name'),
                },
                'data': {
                    'value': self._render('name'),
                },
                'width': 36,
            },
            '4_categ_name': {
                'header': {
                    'value': _('Internal Category'),
                },
                'data': {
                    'value': self._render('categ_name'),
                },
                'width': 36,
            },
            '5_barcode': {
                'header': {
                    'value': _('Barcode'),
                },
                'data': {
                    'value': self._render('barcode'),
                },
                'width': 15,
            },
            '5_c_income_analytic_account': {
                'header': {
                    'value': _('Income Analytic Account'),
                },
                'data': {
                    'value': self._render('income_analytic_account'),
                },
                'width': 25,
            },
            '6_qty_at_date': {
                'header': {
                    'value': _('Quantity'),
                },
                'data': {
                    'value': self._render('qty_at_date'),
                    'format': self.format_tcell_amount_conditional_right,
                },
                'width': 18,
            },
            '7_standard_price': {
                'header': {
                    'value': _('Cost'),
                },
                'data': {
                    'value': self._render('standard_price'),
                    'format': self.format_tcell_amount_conditional_right,
                },
                'width': 18,
            },
            '8_stock_value': {
                'header': {
                    'value': _('Value'),
                },
                'data': {
                    'value': self._render('stock_value'),
                    'format': self.format_tcell_amount_conditional_right,
                },
                'width': 18,
            },
        }

    def _get_column_total_index(self):
        return 8

    def _get_render_space(self, row_pos, line):
        render_space = {
            'n': row_pos-5,
            'name': line.name or '',
            'reference': line.reference or '',
            'barcode': line.barcode or '',
            'income_analytic_account': line.income_analytic_account or '',
            'qty_at_date': line.qty_at_date or 0.000,
            'standard_price': line.standard_price or 0.00,
            'stock_value': line.stock_value or 0.00,
            'categ_name': line.categ_name
        }
        return render_space
