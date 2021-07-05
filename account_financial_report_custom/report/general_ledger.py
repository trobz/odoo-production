
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class GeneralLedgerReportMoveLine(models.TransientModel):

    _inherit = 'report_general_ledger_move_line'

    def group_by_move_partner(self):
        """
        Group line by date, entry, account, taxes, partner, cost center
        """
        class DataLine(object):
            def __init__(self, date, entry, account, taxes_description,
                    partner, label, cost_center, tags, matching_number,
                    currency_id, debit, credit,
                    cumul_balance, amount_currency, data_dict={}):
                self.date = date
                self.entry = entry
                self.account = account
                self.taxes_description = taxes_description
                self.partner = partner
                self.label = label
                self.cost_center = cost_center
                self.tags = tags
                self.matching_number = matching_number
                self.currency_id = currency_id
                self.debit = 0
                self.credit = 0
                self.cumul_balance = 0
                self.amount_currency = 0
                self.dict = data_dict

            def __getattr__(self, attr):
                return attr in self.dict and self.dict.__getitem__(attr) or 0.0

        def get_k(line):
            return '{a}_{b}_{c}_{d}_{e}_{f}_{g}_{h}_{i}'.format(
                a=line.date,
                b=line.entry,
                c=line.account,
                d=line.taxes_description,
                e=line.partner,
                f=line.move_line_id.ref, # By reference of account move
                g=line.cost_center,
                h=line.matching_number,
                i=line.currency_id,
            )
        data_dict = {}

        for line in self:
            k = get_k(line)
            if k not in data_dict:
                data_dict[k] = DataLine(
                    line.date,
                    line.entry,
                    line.account,
                    line.taxes_description,
                    line.partner,
                    line.move_line_id.ref,
                    line.cost_center,
                    line.tags,
                    line.matching_number,
                    line.currency_id,
                    0,
                    0,
                    0,
                    0,
                )
            data_dict[k].debit += line.debit
            data_dict[k].credit += line.credit
            data_dict[k].cumul_balance += line.cumul_balance
            data_dict[k].amount_currency += line.amount_currency
        return data_dict.values()
