# Copyright 2016-Today: La Louve (<http://www.lalouve.net/>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    def _search_default_journal(self):
        if self.partner_id.default_purchase_journal_id:
            return self.partner_id.default_purchase_journal_id
        return super()._search_default_journal()
