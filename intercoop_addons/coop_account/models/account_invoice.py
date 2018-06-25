# -*- coding: utf-8 -*-

from openerp import api, models, fields


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def action_date_assign(self):
        for inv in self:
            if not inv.date_due:
                inv._onchange_payment_term_date_invoice()
        return True

    @api.onchange('invoice_line_ids')
    def _onchange_invoice_line_ids(self):
        """
        disable this function because it raised an issue when
        saving invoice second time when modifing many invoice_line (has tax)
        tax_line_ids will be computed in
        create and write function as work-around
        see issue onchange with one2many fields:
        https://github.com/odoo/odoo/issues/11236
        https://github.com/odoo/odoo/issues/2693
        """
        if self._context.get('called_by_method', False):
            return super(AccountInvoice, self)._onchange_invoice_line_ids()
        return

    @api.multi
    def _compute_tax_line(self):
        """
        Compute tax line and convert value into writable format
        """
        self.ensure_one()
        taxes_grouped = self.get_taxes_values()
        tax_lines = self.tax_line_ids.filtered('manual')
        res = [[5, 0, 0]]
        # res.append([6, 0, tax_lines.ids])
        for tax_line in tax_lines:
            res.append([4, tax_line.id, 0])
        for tax in taxes_grouped.values():
            # tax_lines += tax_lines.new(tax)
            res.append([0, 0, tax])
        return res

    @api.model
    def create(self, vals):
        invoice = super(AccountInvoice, self).create(vals)
        # recompute tax_line_ids because
        # we don't use _onchange_invoice_line_ids anymore
        invoice.tax_line_ids = invoice._compute_tax_line()
        return invoice

    @api.multi
    def write(self, vals):
        res = super(AccountInvoice, self).write(vals)
        if 'invoice_line_ids' in vals:
            for invoice in self:
                tax_line_vals = invoice._compute_tax_line()
                invoice.tax_line_ids = tax_line_vals
        return res
