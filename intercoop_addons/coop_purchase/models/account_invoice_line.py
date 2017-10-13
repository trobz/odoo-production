# -*- coding: utf-8 -*-
# Copyright (C) 2015-Today: Smile (<http://www.smile.fr>)
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api, fields


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    base_price = fields.Monetary("Base Price", readonly=True)

    @api.onchange('product_id')
    def _onchange_product_id(self):
        ret = super(AccountInvoiceLine, self)._onchange_product_id()
        if self.invoice_id.type in ('in_invoice', 'in_refund') and \
                self.product_id:
            suppliers = self.product_id.seller_ids.filtered(
                lambda x: x.name == self.partner_id)
            if suppliers:
                self.package_qty = suppliers[0].package_qty
                self.discount = suppliers[0].discount
                self.base_price = suppliers[0].base_price
        return ret
