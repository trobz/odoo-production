# -*- coding: utf-8 -*-

from openerp import api, models, fields


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.onchange('payment_term_id', 'date_invoice')
    def _onchange_payment_term_date_invoice(self):
        date_due = self.date_due
        super(AccountInvoice, self)._onchange_payment_term_date_invoice()
        if date_due:
            self.date_due = date_due
