from odoo import api, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    @api.onchange('partner_id')
    def onchange_partner_id(self):
        super().onchange_partner_id()
        if not self.payment_term_id and self.website_id.payment_term_id:
            self.payment_term_id = self.website_id.payment_term_id
