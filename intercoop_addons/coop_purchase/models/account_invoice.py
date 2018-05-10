# -*- coding: utf-8 -*-

from openerp import api, models
from lxml import etree
from openerp.osv.orm import setup_modifiers


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.onchange('purchase_id')
    def purchase_order_change(self):

        # Get invocie line involved to generate
        if self.type == 'in_refund':
            self.adding_po_line_vendor_refund()

        res = super(AccountInvoice, self).purchase_order_change()
        for line in self.invoice_line_ids:
            suppliers = line.product_id.seller_ids.filtered(
                lambda x: x.name == self.partner_id)
            if suppliers:
                line.base_price = suppliers[0].base_price
        return res

    def fields_view_get(self, cr, uid, view_id=None, view_type='form',
                        context=None, toolbar=False, submenu=False):
        if context is None:
            context = {}

        res = super(AccountInvoice, self).fields_view_get(cr, uid,
                                                          view_id=view_id,
                                                          view_type=view_type,
                                                          context=context,
                                                          toolbar=toolbar,
                                                          submenu=submenu)

        # Read only field contact base specific groups
        account_advise = self.user_has_groups(cr, uid,
                                              'account.group_account_manager')
        doc = etree.fromstring(res['arch'])
        if not account_advise:
            if view_type == 'form':
                list_readonly_field = ['journal_id', 'account_id', 'user_id',
                                       'payment_term_id', 'fiscal_position_id',
                                       'move_id', 'date',
                                       'company_id']
                for node in doc.xpath("//field"):
                    if node.get('name') in list_readonly_field:
                        node.set('readonly', '1')
                        setup_modifiers(node)
            res['arch'] = etree.tostring(doc)

        return res

    @api.multi
    def adding_po_line_vendor_refund(self):
        self.ensure_one()
        new_lines = self.env['account.invoice.line']

        # Get all invoiced line involved this purchase
        invoice_lines = self.purchase_id.order_line.mapped('invoice_lines').filtered(
            lambda i: i.invoice_id.state == 'paid'
        )

        # Get po lines have invoiced
        po_line_related = invoice_lines.mapped('purchase_line_id')

        for line in po_line_related -\
                self.invoice_line_ids.mapped('purchase_line_id'):
            data = self._prepare_invoice_line_from_po_line(line)
            new_line = new_lines.new(data)
            new_line._set_additional_fields(self)
            new_lines += new_line
        self.invoice_line_ids += new_lines
        self.purchase_id = False
