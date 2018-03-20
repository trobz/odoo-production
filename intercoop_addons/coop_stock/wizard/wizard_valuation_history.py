# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp import models, api
from openerp.tools.safe_eval import safe_eval


class WizardValuationHistory(models.TransientModel):
    _inherit = 'wizard.valuation.history'

    @api.v7
    def open_table(self, cr, uid, ids, context=None):
        res = super(WizardValuationHistory, self).open_table(
            cr, uid, ids, context=None)
        if context is None:
            context = {}
        domain = safe_eval(res['domain'])
        if domain:
            domain.append(('product_id.type', '!=', 'consu'))
            res['domain'] = str(domain)
        return res
