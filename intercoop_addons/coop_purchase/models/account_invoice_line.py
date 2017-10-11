# -*- coding: utf-8 -*-
# Copyright (C) 2015-Today: Smile (<http://www.smile.fr>)
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api, fields


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    price_total = fields.Float("Total", compute="_compute_price_total",
                               readonly=True)

    @api.onchange('product_id')
    def _onchange_product_id(self):
        ret = super(AccountInvoiceLine, self)._onchange_product_id()
        if self.product_id:
            seller = self.product_id._select_seller(self.product_id)
            if seller:
                self.package_qty = seller.package_qty
                self.discount = seller.discount
        return ret

    @api.multi
    @api.depends('quantity', 'price_unit')
    def _compute_price_total(self):
        for rec in self:
            rec.price_total = rec.quantity * rec.price_unit
