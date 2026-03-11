from odoo import models


class AccountPaymentRegister(models.TransientModel):
    _inherit = "account.payment.register"

    def _create_payments(self):
        # Override to generate capital entries for all reconciled lines
        payments = super()._create_payments()
        full_reconciles = payments.mapped("move_id.line_ids.full_reconcile_id")
        if full_reconciles:
            full_reconciles.generate_capital_entries()
        return payments
