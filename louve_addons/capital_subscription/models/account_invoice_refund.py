# -*- coding: utf-8 -*-

from openerp import api, fields, models, _


class AccountInvoiceRefund(models.TransientModel):

    _inherit = "account.invoice.refund"

    @api.model
    def _get_reason(self):
        context = dict(self._context or {})
        active_id = context.get('active_id', False)
        if active_id:
            inv = self.env['account.invoice'].browse(active_id)
            if inv.is_capital_fundraising:
                return _('Redemption %s - %d') % \
                    (inv.number, inv.partner_id.barcode_base)
        return super(AccountInvoiceRefund, self)._get_reason()

    description = fields.Char(default=_get_reason)
    refund_quantity = fields.Integer(string="Quantity Of Shares To Refund",
                                     default=0, required=True)

    @api.multi
    def compute_refund(self, mode='refund'):
        AccountInvoice = self.env['account.invoice']
        res = super(AccountInvoiceRefund, self).compute_refund(mode)
        if mode == 'refund':
            domain = 'domain' in res and res.get('domain', [])
            if domain:
                for record in self:
                    if record.refund_quantity and record.refund_quantity > 0:
                        invs = AccountInvoice.search(domain)
                        if invs:
                            invs.invoice_line_ids.write(
                                {'quantity': record.refund_quantity})
                            invs.apply_refund_deficit_share()
        return res

