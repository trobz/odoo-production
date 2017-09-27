# -*- coding: utf-8 -*-

from openerp import api, fields, models, _
from openerp.tools.safe_eval import safe_eval


class PurchaseConfigSettings(models.TransientModel):
    _inherit = 'purchase.config.settings'

    auto_update_base_price = fields.Boolean(
        string='An update of Vendor Price updates Base Price automatically')
    auto_update_theorical_cost = fields.Boolean(
        string='An update of Theorical Cost updates Cost automatically')
    auto_update_theorical_price = fields.Boolean(
        string='An update of Theorical Price updates Price automatically')

    @api.multi
    def get_default_auto_update_base_price(self):
        param_env = self.env['ir.config_parameter']
        val = param_env.get_param('auto_update_base_price')
        return {'auto_update_base_price': val}

    @api.multi
    def set_auto_update_base_price(self):
        param_env = self.env['ir.config_parameter']
        for rec in self:
            config = rec.auto_update_base_price or False
            param_env.set_param('auto_update_base_price', config)

    @api.multi
    def get_default_auto_update_theorical_cost(self):
        param_env = self.env['ir.config_parameter']
        val = param_env.get_param('auto_update_theorical_cost')
        return {'auto_update_theorical_cost': val}

    @api.multi
    def set_auto_update_theorical_cost(self):
        param_env = self.env['ir.config_parameter']
        for rec in self:
            config = rec.auto_update_theorical_cost or False
            param_env.set_param('auto_update_theorical_cost', config)

    @api.multi
    def get_default_auto_update_theorical_price(self):
        param_env = self.env['ir.config_parameter']
        val = param_env.get_param('auto_update_theorical_price')
        return {'auto_update_theorical_price': val}

    @api.multi
    def set_auto_update_theorical_price(self):
        param_env = self.env['ir.config_parameter']
        for rec in self:
            config = rec.auto_update_theorical_price or False
            param_env.set_param('auto_update_theorical_price', config)
