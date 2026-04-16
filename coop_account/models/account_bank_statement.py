from odoo import models
from odoo.exceptions import UserError


class AccountBankStatement(models.Model):
    _inherit = "account.bank.statement"

    def _compute_journal_id(self):
        for statement in self:
            if len(statement.line_ids.journal_id) > 1:
                raise UserError(
                    self.env._(
                        "The bank statement '%s' has multiple journals on its lines. ",
                        statement.name,
                    )
                )
            statement.journal_id = statement.line_ids.journal_id
