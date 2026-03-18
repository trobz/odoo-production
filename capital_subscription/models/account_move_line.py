from odoo import models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def _compute_account_id(self):
        # Override to update the account_id of the payment line with the one
        # defined on the fundraising category.
        res = super()._compute_account_id()
        term_lines = self.filtered(
            lambda line: line.display_type == "payment_term"
            and line.move_id.is_sale_document(include_receipts=True)
            and line.move_id.fundraising_category_id.partner_account_id
        )
        for line in term_lines:
            line.account_id = line.move_id.fundraising_category_id.partner_account_id

        return res
