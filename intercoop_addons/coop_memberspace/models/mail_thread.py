# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Lorenzo Battistini <lorenzo.battistini@agilebg.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, api

import logging
import re
import socket
from email.message import Message

from openerp import tools
from openerp.addons.mail.models.mail_message import decode
from openerp.tools.safe_eval import safe_eval as eval


_logger = logging.getLogger(__name__)


mail_header_msgid_re = re.compile('<[^<>]+>')


def decode_header(message, header, separator=' '):
    return separator.join(map(decode, filter(None, message.get_all(header, []))))


class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    @api.model
    def verify_memberspace_alias(self, message, header, partner):
        if not message.has_key(header):
            return []
        MemberSpaceAlias = self.env['memberspace.alias']
        alias_error = MemberSpaceAlias
        alias_pass = MemberSpaceAlias
        email_pass = []
        mail_tmpl = self.env.ref(
            'coop_memberspace.email_inform_cannot_send_to_memberspace_alias')
        rcpt_tos = ','.join([decode_header(message, header)])
        for e in tools.email_split(rcpt_tos):
            local_part = e.split('@')[0].lower()
            memberspace_alias = MemberSpaceAlias.search([
                ('alias_name', '=', local_part)], limit=1)
            if not memberspace_alias:
                email_pass.append(e)
                continue
            coordinators = memberspace_alias.shift_id.user_ids
            members = coordinators | memberspace_alias.shift_id.registration_ids.filtered(
                lambda r: r.is_current_participant).mapped('partner_id')
            if memberspace_alias.type == 'team' and \
                partner not in coordinators:
                alias_error |= memberspace_alias
                if partner in members and mail_tmpl:
                    email_add = memberspace_alias.alias_name + '@' + \
                        memberspace_alias.alias_domain
                    template_values = {
                        'email_to': partner.email,
                        'email_from': self.env.user.company_id.email,
                        'email_cc': False,
                        'lang': partner.lang,
                        'auto_delete': True,
                        'partner_to': False,
                    }
                    mail_tmpl.write(template_values)
                    mail_tmpl.with_context(email_add=email_add).send_mail(
                        self.env.user.id, force_send=True)
                continue
            elif memberspace_alias.type == 'coordinator' and \
                partner not in members:
                alias_error |= memberspace_alias
                continue
            alias_pass |= memberspace_alias
        email_pass.extend([ma.alias_name + '@' + ma.alias_domain
                for ma in alias_pass])
        if alias_error:
            new_header = ','.join(email_pass)
            message.replace_header(header, new_header)
        return email_pass

    @api.model
    def message_route(self, message, message_dict, model=None,
            thread_id=None, custom_values=None):
        if not isinstance(message, Message):
            raise TypeError('message must be an email.message.Message at this point')
        email_from = decode_header(message, 'From')
        # Memberspace workflow
        if '<' in email_from:
            email_from = email_from.split('<')[1][:-1]
        partner = self.env['res.partner'].search([
            ('email', '=', email_from)
        ], limit=1)
        if not partner:
            return super(MailThread, self).message_route(
                message, message_dict, model=model, thread_id=thread_id,
                custom_values=custom_values)
        emails_pass = []
        # Check header with key = To
        email_pass = self.verify_memberspace_alias(
            message, 'To', partner)
        emails_pass.extend(email_pass)
        # Check header with key = Delivered-To
        email_pass = self.verify_memberspace_alias(
            message, 'Delivered-To', partner)
        emails_pass.extend(email_pass)
        # Check header with key = Cc
        email_pass = self.verify_memberspace_alias(
            message, 'Cc', partner)
        emails_pass.extend(email_pass)
        # Check header with key = Resent-To
        email_pass = self.verify_memberspace_alias(
            message, 'Resent-To', partner)
        emails_pass.extend(email_pass)
        # Check header with key = Resent-Cc
        email_pass = self.verify_memberspace_alias(
            message, 'Resent-Cc', partner)
        emails_pass.extend(email_pass)
        
        if not emails_pass:
            return []
        return super(MailThread, self).message_route(
            message, message_dict, model=model, thread_id=thread_id,
            custom_values=custom_values)
