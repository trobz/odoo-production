from odoo import api, fields, models


class AccountCheckDeposit(models.Model):
    _inherit = "account.check.deposit"

    is_reconcile = fields.Boolean(
        compute="_compute_is_reconcile", store=True, string="Reconciled"
    )

    @api.depends("bank_journal_id", "move_id")
    def _compute_is_reconcile(self):
        for rec in self:
            reconcile = False
            for line in rec.move_id.line_ids:
                if (
                    line.account_id.id != rec.bank_journal_id.default_account_id.id
                    and line.reconciled
                ):
                    reconcile = True
                    break
            rec.is_reconcile = reconcile
