# -*- coding: utf-8 -*-


from openerp import models, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.model
    def _prepare_refund(
            self, invoice, date_invoice=None,
            date=None, description=None, journal_id=None):
        context = dict(self._context or {})
        res = super(AccountInvoice, self)._prepare_refund(
            invoice, date_invoice=date_invoice,
            date=date, description=description, journal_id=journal_id)
        invoice_line_ids = context.get('invoice_line_ids', [])
        if invoice_line_ids:
            res['invoice_line_ids'] = self._refund_cleanup_lines(
                invoice_line_ids)
        return res
