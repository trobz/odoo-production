from odoo import models


class PosSession(models.Model):
    _inherit = "pos.session"

    def try_cash_in_out(self, _type, amount, reason, extras):
        if self.config_id.suspense_account_id:
            extras = extras or {}
            extras["counterpart_account_id"] = self.config_id.suspense_account_id.id
        return super().try_cash_in_out(_type, amount, reason, extras)

    def _prepare_account_bank_statement_line_vals(
        self, session, sign, amount, reason, extras
    ):
        res = super()._prepare_account_bank_statement_line_vals(
            session, sign, amount, reason, extras
        )
        if extras.get("counterpart_account_id"):
            res["counterpart_account_id"] = extras["counterpart_account_id"]
        return res
