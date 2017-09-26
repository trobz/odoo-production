# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: La Louve (<http://www.lalouve.net/>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import re
from openerp import api, fields, models, tools, _
from openerp.exceptions import Warning
import logging

try:
    from validate_email import validate_email
    from DNS import TimeoutError
except ImportError:
    validate_email = None

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def validate_and_update_email(self, email, disable_validate_email=False):
        '''
        @Function validate email.
            - Validate email format with regex.
            - Use library validate_email to check email exist or not.
        '''
        config_param_env = self.env['ir.config_parameter']
        if disable_validate_email:
            return email
        email_temp = email and re.sub('\s', '', email)
        valid = True
        message = ""
        if tools.single_email_re.match(email_temp):
            message = _("Email format correct.\n")
            avail_check = config_param_env.get_param('validate_email',
                                                     False)
            avail_check = avail_check and eval(avail_check) or False
            if not validate_email or not avail_check:
                return email_temp
            else:
                try:
                    valid = validate_email(email,
                                           check_mx=True,
                                           verify=True)
                except TimeoutError as toe:
                    # time out when checking validating email domain.
                    # but the format of email still be correct.
                    # so pass this case.
                    valid = True
                    _logger.warn("[TimeoutError] - time out when checking " +
                                 "email '%s' - partner_id=" % (email, self.id))
        else:
            valid = False
        if valid:
            return email_temp
        else:
            if not message:
                raise Warning(_("Email format is incorrect."))
            else:
                message = _("Email format is correct but domain "
                            "doesn't seem to have any mail server.")
                raise Warning(message)

    @api.model
    def create(self, vals):
        disable = self._context.get('disable_validate_email', False)
        email = vals.get('email', False)
        if email:
            vals.update({'email': self.validate_and_update_email(email,
                                                                 disable)})
        return super(ResPartner, self).create(vals)

    @api.multi
    def write(self, vals):
        disable = self._context.get('disable_validate_email', False)
        for rec in self:
            email = vals.get('email', False)
            if email:
                vals.update({'email': rec.validate_and_update_email(email,
                                                                    disable)})
        return super(ResPartner, self).write(vals)