from odoo import api, fields, models


class AccountAccount(models.Model):
    _inherit = "account.account"

    reconciled_account = fields.Boolean(
        compute="_compute_field_reconciled_account",
        string="Bank Reconciliation",
        store=True,
        help="If true, account moves will be able to have at most only one "
        + "account move line linked to this account (or to another account "
        + "with 'Bank reconciliation' is true)",
    )
    journal_ids = fields.One2many(
        "account.journal",
        "default_account_id",
    )

    @api.depends(
        "journal_ids",
        "journal_ids.type",
    )
    def _compute_field_reconciled_account(self):
        for account in self:
            account_journal = account.journal_ids
            if account_journal.filtered(lambda journal: journal.bank_account_id):
                if any(journal.type == "bank" for journal in account_journal):
                    account.reconciled_account = True
                else:
                    account.reconciled_account = False
            else:
                account.reconciled_account = False
