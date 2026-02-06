# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class GeneralLedgerXslx(models.AbstractModel):
    _inherit = 'report.a_f_r.report_general_ledger_xlsx'

    def _generate_report_content(self, workbook, report):
        # For each account
        for account in report.account_ids:
            # Write account title
            self.write_array_title(account.code + ' - ' + account.name)

            if not account.partner_ids:
                # Display array header for move lines
                self.write_array_header()

                # Display initial balance line for account
                self.write_initial_balance(account)

                # Display account move lines
                data_lines = account.move_line_ids.group_by_move_partner()
                for line in data_lines:
                    self.write_line(line)

            else:
                # For each partner
                for partner in account.partner_ids:
                    # Write partner title
                    self.write_array_title(partner.name)

                    # Display array header for move lines
                    self.write_array_header()

                    # Display initial balance line for partner
                    self.write_initial_balance(partner)

                    # Display account move lines
                    data_lines = partner.move_line_ids.group_by_move_partner()
                    for line in data_lines:
                        self.write_line(line)

                    # Display ending balance line for partner
                    self.write_ending_balance(partner)

                    # Line break
                    self.row_pos += 1

            # Display ending balance line for account
            if not report.filter_partner_ids:
                self.write_ending_balance(account)

            # 2 lines break
            self.row_pos += 2
