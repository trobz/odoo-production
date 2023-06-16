# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

from odoo import api, fields, models, tools

from odoo.http import request
from odoo.addons.website.models import ir_http

_logger = logging.getLogger(__name__)


class Website(models.Model):
    _inherit = 'website'

    payment_term_id = fields.Many2one(
        "account.payment.term",
        string="Default Payment Term")

    @api.model
    def sale_get_payment_term(self, partner):
        return (
            partner.property_payment_term_id or
            (self and self[0].payment_term_id) or
            self.env.ref('account.account_payment_term_immediate', False) or
            self.env['account.payment.term'].sudo().search([('company_id', '=', self.company_id.id)], limit=1)
        ).id
