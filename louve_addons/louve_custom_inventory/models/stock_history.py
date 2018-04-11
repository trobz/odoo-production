# -*- coding: utf-8 -*-

from openerp import models, api, _
from openerp.exceptions import Warning


class StockHistory(models.Model):
    _inherit = 'stock.history'

    @api.model
    def create(self, vals):
        raise Warning(_('You cannot create Stock History record.'))
        return super(StockHistory, self).create(vals)


class ir_import(models.TransientModel):
    _inherit = 'base_import.import'

    @api.model
    def create(self, vals):
        active_model = vals.get('res_model', False)
        if active_model == 'stock.history':
            raise Warning(_('You cannot import Stock History record.'))
        return super(ir_import, self).create(vals)
