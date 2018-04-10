# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.fr/>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html


from datetime import datetime
from openerp.addons.report_xlsx.report.report_xlsx import ReportXlsx
from openerp.api import Environment
from openerp import SUPERUSER_ID
from openerp import _
FORMAT_BOLD = '00'
FORMAT_NORMAL = '01'
FORMAT_RIGHT = '02'


class ReportBankReconciliationSummary(ReportXlsx):

    def create_xlsx_report(self, ids, data, report):
        self.env = Environment(self.env.cr, SUPERUSER_ID, self.env.context)
        return super(
            ReportBankReconciliationSummary, self
        ).create_xlsx_report(ids, data, report)

    def generate_xlsx_report(self, workbook, data, objects):
        self.object = objects[0]
        self._define_formats(workbook)
        self.sheet = workbook.add_worksheet()
        self.setup_config()
        # generate main content
        self.generate_report_title()
        # generate data table
        datas = objects.get_data()
        self.generate_title_bank_reconciliation()
        total_credit, total_debit = self.generate_data_bank_reconciliation(
            datas)
        self.load_data_blance(total_credit, total_debit)

    def _define_formats(self, workbook):
        # ---------------------------------------------------------------------
        # Common
        # ---------------------------------------------------------------------
        format_config = {
            'font_name': 'Calibri',
            'font_size': 11,
            'valign': 'vcenter',
            'text_wrap': True,
        }
        self.format_default = workbook.add_format(format_config)

        format_bold = format_config.copy()
        format_bold.update({
            'bold': True,
        })
        self.format_bold = workbook.add_format(format_bold)

        format_bold_balance = format_bold.copy()
        format_bold_balance.update({
            'align': 'right',
        })
        self.format_bold_balance = workbook.add_format(format_bold_balance)

        format_bold_center = format_bold.copy()
        format_bold_center.update({
            'align': 'center',
        })
        self.format_bold_center = workbook.add_format(format_bold_center)

        format_right = format_config.copy()
        format_right.update({
            'align': 'right',
        })
        self.format_right = workbook.add_format(format_right)

        format_center = format_config.copy()
        format_center.update({
            'align': 'center',
        })
        self.format_center = workbook.add_format(format_center)

        # ---------------------------------------------------------------------
        # Report Template
        # ---------------------------------------------------------------------
        format_template_title = format_config.copy()
        format_template_title.update({
            'bold': True,
            'align': 'center',
        })
        self.format_template_title = workbook.add_format(format_template_title)

        # ---------------------------------------------------------------------
        # Report Title
        # ---------------------------------------------------------------------
        format_report_title = format_config.copy()
        format_report_title.update({
            'bold': True,
            'align': 'center',
            'font_size': 24,
        })
        self.format_report_title = workbook.add_format(format_report_title)

        format_uom = format_config.copy()
        format_uom.update({
            'italic': True,
            'align': 'right',
        })
        self.format_uom = workbook.add_format(format_uom)
        # ---------------------------------------------------------------------
        # Table format
        # ---------------------------------------------------------------------
        format_table = format_config.copy()
        format_table.update({
            'bold': True,
            'align': 'vcenter',
            'font_size': 14,
        })
        self.format_table = workbook.add_format(format_table)
        self.format_table.set_bg_color('#3399FF')
        self.format_table.set_font_color('#ffffff')

        format_table_date = format_config.copy()
        format_table_date.update({
            'border': True,
            'align': 'vcenter',
            'num_format': 'dd/mm/yyyy',
            'font_size': 11
        })
        self.format_table_date = workbook.add_format(format_table_date)
        self.format_table_date.set_bg_color('#3399FF')
        self.format_table_date.set_font_color('#ffffff')

        format_table_date_default = format_config.copy()
        format_table_date_default.update({
            'align': 'vcenter',
            'num_format': 'dd/mm/yyyy',
            'font_size': 11
        })
        self.format_table_date_default = workbook.add_format(
            format_table_date_default)

        format_table_center = format_table.copy()
        format_table_center.update({
            'border': True,
            'align': 'vcenter',
            'font_size': 11,
        })
        self.format_table_center = workbook.add_format(format_table_center)
        self.format_table_center.set_bg_color('#3399FF')
        self.format_table_center.set_font_color('#ffffff')

        format_table_bold = format_table.copy()
        format_table_bold.update({
            'bold': False,
            'font_size': 11,
            'align': 'vcenter',
        })
        self.format_table_bold = workbook.add_format(format_table_bold)

        format_table_bold_total = format_table.copy()
        format_table_bold_total.update({
            'font_size': 11,
            'align': 'right',
        })
        self.format_table_bold_total = workbook.add_format(
            format_table_bold_total)
        self.format_table_bold_total.set_bg_color('#808080')

        format_table_bold_total_number = format_table.copy()
        format_table_bold_total_number.update({
            'font_size': 11,
            'align': 'vcenter',
        })
        self.format_table_bold_total_number = workbook.add_format(
            format_table_bold_total_number)
        self.format_table_bold_total_number.set_font_color('#f90606')

        format_table_bold_total_number_balance = format_table.copy()
        format_table_bold_total_number_balance.update({
            'font_size': 11,
            'align': 'right',
        })
        self.format_table_bold_total_number_balance = workbook.add_format(
            format_table_bold_total_number_balance)
        self.format_table_bold_total_number_balance.set_font_color('#f90606')

    def setup_config(self):
        self.row_pos = 0
        self.account_data = {}
        self._set_default_format()

    def _set_default_format(self):
        self.sheet.set_column('A:Z', None, self.format_default)
        self.sheet.set_row(4, 20)

        self.sheet.set_column('A:A', 30)
        self.sheet.set_column('B:B', 20)
        self.sheet.set_column('C:C', 20)
        self.sheet.set_column('D:D', 60)
        self.sheet.set_column('E:E', 30)
        self.sheet.set_column('F:F', 20)
        self.sheet.set_column('G:G', 15)

    def generate_report_title(self):
        self.sheet.merge_range(
            'A3:G4',
            _(u'Bank Reconciliation Summary'),
            self.format_report_title)

        self.sheet.write(
            "A8",
            _(u"Report Date"),
            self.format_bold
        )
        self.sheet.write(
            "A9",
            _(u"Printed by"),
            self.format_bold
        )
        self.sheet.write(
            "A10",
            _(u"Printed Date"),
            self.format_bold
        )
        self.sheet.write(
            "E8",
            _(u"Account"),
            self.format_bold
        )
        self.sheet.write(
            "E9",
            _(u"Currency"),
            self.format_bold
        )
        self.sheet.write(
            "C13",
            _(u"Account Balance"),
            self.format_bold
        )
        self.sheet.write(
            "C14",
            _(u"Bank Balance"),
            self.format_bold
        )
        self.sheet.write(
            "C15",
            _(u"Control"),
            self.format_bold
        )

        self.sheet.write(
            "B8",
            u"%s" % self.object.analysis_date or '',
            self.format_table_date_default
        )

        self.sheet.write(
            "B9",
            u"%s" % self.object.env.user.name or '',
            self.format_table_bold
        )

        self.sheet.write(
            "B10",
            u"%s" % datetime.now().strftime("%Y-%m-%d %H:%M:%S") or '',
            self.format_table_date_default
        )

        self.sheet.write(
            "F8",
            u"%s" % self.object.journal_id.name or '',
            self.format_table_bold
        )

        self.sheet.write(
            "F9",
            u"%s" % self.object.journal_id.currency_id and
            self.object.journal_id.currency_id.name or '',
            self.format_table_bold
        )

    def generate_title_bank_reconciliation(self):
        self.sheet.merge_range(
            'A18:G18',
            _(u'Outstanding Journal Items'),
            self.format_table)
        self.sheet.write(
            "A19",
            _(u"Date"),
            self.format_table_date
        )
        self.sheet.write(
            "B19",
            _(u"Journal Entry"),
            self.format_table_center
        )
        self.sheet.write(
            "C19",
            _(u"Partner"),
            self.format_table_center
        )
        self.sheet.write(
            "D19",
            _(u"Partner Reference"),
            self.format_table_center
        )
        self.sheet.write(
            "E19",
            _(u"Label"),
            self.format_table_center
        )
        self.sheet.write(
            "F19",
            _(u"Debit"),
            self.format_table_center
        )
        self.sheet.write(
            "G19",
            _(u"Credit"),
            self.format_table_center
        )

    def generate_outstanding_bank(self, row):
        self.sheet.merge_range(
            'A%s:G%s' % (row, row),
            _(u'Outstanding Bank Transactions'),
            self.format_table)
        self.sheet.write(
            "A%s" % (row + 1),
            _(u"Date"),
            self.format_table_date
        )
        self.sheet.write(
            "B%s" % (row + 1),
            _(u"Reference"),
            self.format_table_center
        )
        self.sheet.write(
            "C%s" % (row + 1),
            _(u"Partner"),
            self.format_table_center
        )
        self.sheet.write(
            "D%s" % (row + 1),
            _(u"Memo"),
            self.format_table_center
        )
        self.sheet.write(
            "E%s" % (row + 1),
            u"",
            self.format_table_center
        )
        self.sheet.write(
            "F%s" % (row + 1),
            _(u"Debit"),
            self.format_table_center
        )
        self.sheet.write(
            "G%s" % (row + 1),
            _(u"Credit"),
            self.format_table_center
        )

    def generate_data_bank_reconciliation(self, datas):
        row = 20
        total_credit = 0
        total_debit = 0
        if datas:
            move_line_ids = datas.get('move_line_ids', False)
            if move_line_ids:
                move_lines = self.env['account.move.line'].browse(
                    move_line_ids)
                for move_line in move_lines:
                    self.sheet.write(
                        "A%s" % row,
                        u"%s" % move_line.date,
                        self.format_table_date_default)
                    self.sheet.write(
                        "B%s" % row,
                        u"%s" % move_line.move_id and
                        move_line.move_id.name or '',
                        self.format_table_bold)
                    self.sheet.write(
                        "C%s" % row,
                        u"%s" % move_line.partner_id and
                        move_line.partner_id.name or '',
                        self.format_table_bold)
                    self.sheet.write(
                        "D%s" % row,
                        u"%s" % move_line.ref or '',
                        self.format_table_bold)
                    self.sheet.write(
                        "E%s" % row,
                        u"%s" % move_line.name or '',
                        self.format_table_bold)
                    self.sheet.write(
                        "F%s" % row,
                        u"%s" % str(move_line.debit) or '0.00',
                        self.format_table_bold)
                    self.sheet.write(
                        "G%s" % row,
                        u"%s" % str(move_line.credit) or '0.00',
                        self.format_table_bold)
                    total_credit += move_line.credit
                    row += 1
                self.sheet.merge_range(
                    'A%s:E%s' % (row, row),
                    _(u'Total Journal Items'),
                    self.format_table_bold_total)
                self.sheet.write(
                    "G%s" % row,
                    u"%s" % str(total_credit),
                    self.format_table_bold_total_number)
            row += 5
            self.generate_outstanding_bank(row)
            row += 2
            bank_statement_line_ids = datas.get(
                'bank_statement_line_ids', False)
            if bank_statement_line_ids:
                bank_statement_lines = \
                    self.env['account.bank.statement.line'].browse(
                        bank_statement_line_ids)
                for bank_statement_line in bank_statement_lines:
                    self.sheet.write(
                        "A%s" % row,
                        u"%s" % bank_statement_line.date,
                        self.format_table_date_default)
                    self.sheet.write(
                        "B%s" % row,
                        u"%s" % bank_statement_line.ref or '',
                        self.format_table_bold)
                    self.sheet.write(
                        "C%s" % row,
                        u"%s" % bank_statement_line.partner_id and
                        bank_statement_line.partner_id.name or '',
                        self.format_table_bold)
                    self.sheet.write(
                        "D%s" % row,
                        u"%s" % bank_statement_line.name or '',
                        self.format_table_bold)
                    self.sheet.write(
                        "E%s" % row,
                        u"%s" % '',
                        self.format_table_bold)
                    self.sheet.write(
                        "F%s" % row,
                        u"%s" % str(bank_statement_line.amount) or '0.00',
                        self.format_table_bold)
                    self.sheet.write(
                        "G%s" % row,
                        u"%s" % '',
                        self.format_table_bold)
                    total_debit += bank_statement_line.amount
                    row += 1
                self.sheet.merge_range(
                    'A%s:E%s' % (row, row),
                    _(u'Total Bank Transactions'),
                    self.format_table_bold_total)
                self.sheet.write(
                    "F%s" % row,
                    u"%s" % str(total_debit),
                    self.format_table_bold_total_number)
        return total_credit, total_debit

    def load_data_blance(self, total_credit, total_debit):
        self.sheet.write(
            "D13",
            u"%s" % total_credit,
            self.format_bold_balance)
        self.sheet.write(
            "D14",
            u"%s" % total_debit,
            self.format_bold_balance)
        self.sheet.write(
            "D15",
            u"%s" % (total_credit + total_debit),
            self.format_table_bold_total_number_balance)


ReportBankReconciliationSummary(
    'report.bank_reconciliation_summary_xlsx',
    'bank.reconciliation.summary.wizard')
