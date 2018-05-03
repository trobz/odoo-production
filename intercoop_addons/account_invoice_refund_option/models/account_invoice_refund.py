# -*- coding: utf-8 -*-

from openerp import api, fields, models


class AccountInvoiceRefund(models.TransientModel):
    _inherit = "account.invoice.refund"

    @api.model
    def _get_domain_invoice_line(self):
        invoice_id = self._context.get('active_id', False)
        return [('invoice_id', '=', invoice_id)]

    invoice_line_ids = fields.Many2many(
        'account.invoice.line', domain=_get_domain_invoice_line)
    select_product = fields.Boolean('Select Product')

    @api.multi
    def compute_refund(self, mode='refund'):
        res = super(AccountInvoiceRefund, self.with_context(
            invoice_line_ids=self.invoice_line_ids or [])).compute_refund(mode)
        return res

    @api.onchange('filter_refund', 'select_product')
    def onchange_select_product(self):
        if self.filter_refund != 'refund':
            self.select_product = False
            self.invoice_line_ids = []
        if not self.select_product:
            self.invoice_line_ids = []
