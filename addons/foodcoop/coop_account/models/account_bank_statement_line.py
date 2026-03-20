from odoo import models
from odoo.exceptions import UserError


class AccountBankStatementLine(models.Model):
    _inherit = "account.bank.statement.line"

    def get_statement_line_reconcile(self):
        if any(line.is_reconciled for line in self):
            raise UserError(
                self.env._(
                    "This wizard is only available on non reconcilled"
                    + " bank statement lines. Please unselect already"
                    + " reconcilled lines."
                )
            )
        view_id = self.env.ref(
            "coop_account.view_bank_statement_line_reconcile_wizard_form"
        )
        line_ids = self._context.get("active_ids", [])
        active_model = self._context.get("active_model")

        return {
            "name": self.env._("Reconcile"),
            "type": "ir.actions.act_window",
            "view_id": view_id.id,
            "view_mode": "form",
            "res_model": "bank.statement.line.reconcile.wizard",
            "target": "new",
            "context": {
                "line_ids": line_ids,
                "active_model": active_model,
            },
        }

    def reconcile_bank_line(self):
        self.ensure_one()
        move_lines = self.mapped("move_id.line_ids")
        if not self.check_payment_aml_date_month(move_lines):
            raise UserError(
                self.env._(
                    "You cannot reconcile with an account.move posterior "
                    + "to the transaction date except if you reconcile the "
                    + "transaction with only one account move."
                )
            ) from None
        return super().reconcile_bank_line()

    def check_payment_aml_date_month(self, payment_aml_rec):
        """
        Make sure all payment account move lines month
        less than or equal to the current month of bank statement line
        """
        self.ensure_one()
        result = True
        if payment_aml_rec and len(payment_aml_rec) > 1:
            stmt_line_date = self.date
            for payment_aml in payment_aml_rec:
                pmt_aml_date = payment_aml.date
                if (pmt_aml_date.year, pmt_aml_date.month) > (
                    stmt_line_date.year,
                    stmt_line_date.month,
                ):
                    result = False
                    break
        return result
