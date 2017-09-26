# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: La Louve (<http://www.lalouve.net/>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp import fields, models, api, tools, _


class BaseConfigSettings(models.TransientModel):
    _inherit = 'base.config.settings'

    validate_email = fields.Boolean("Enable verification of domain when" +
                                    " checking an email address",
                                    default=False)

    @api.multi
    def set_validate_email(self):
        self.ensure_one()
        value = getattr(self, 'validate_email', False)
        self.env['ir.config_parameter'].set_param('validate_email', value)

    @api.multi
    def get_default_validate_email(self):
        config_param_env = self.env['ir.config_parameter']
        avail_check = config_param_env.get_param('validate_email', False)
        avail_check = avail_check and eval(avail_check) or False
        return {'validate_email': avail_check}
