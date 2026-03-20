from odoo import fields, models


class BankStatementLineReconcileWizard(models.TransientModel):
    _name = "bank.statement.line.reconcile.wizard"
    _description = "Bank Statement Line Reconcile Wizard"

    account_id = fields.Many2one(
        "account.account",
        string="Account",
        required=True,
    )

    def bank_statement_line_reconcile(self):
        self.ensure_one()
        line_ids = self._context.get("line_ids", False)
        active_model = self._context.get("active_model", False)
        if active_model == "account.bank.statement.line":
            stmt_lines = self.env["account.bank.statement.line"].browse(line_ids)
            for stmt_line in stmt_lines:
                amount = stmt_line.amount
                debit = amount < 0 and -amount or 0.0
                credit = amount > 0 and amount or 0.0
                other_line = {
                    "account_id": [
                        self.account_id.id,
                        self.account_id.display_name,
                    ],
                    "debit": debit,
                    "credit": credit,
                    "amount": -(credit + debit),
                    "kind": "other",
                    "currency_amount": amount,
                }

                new_data = stmt_line.reconcile_data_info["data"]
                new_data.append(other_line)
                stmt_line.reconcile_data_info = stmt_line._recompute_suspense_line(
                    new_data,
                    stmt_line.reconcile_data_info["reconcile_auxiliary_id"],
                    stmt_line.manual_reference,
                )
                stmt_line.reconcile_bank_line()
        return True
