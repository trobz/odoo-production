# -*- coding: utf-8 -*-

from openerp import models, api, fields


class ShiftTemplateRegistrationLine(models.Model):
    _inherit = 'shift.template.registration.line'

    @api.model
    def create(self, vals):
        res = super(ShiftTemplateRegistrationLine, self).create(vals)
        alias_team = self.env['memberspace.alias'].search([
            ('shift_id', '=', res.shift_template_id.id),
            ('type', '=', 'team')
        ], limit=1)
        if alias_team and res.registration_id.is_current_participant:
            alias_team.message_subscribe(
                partner_ids=[res.registration_id.partner_id.id])
        return res

    @api.multi
    def write(self, vals):
        res = super(ShiftTemplateRegistrationLine, self).write(vals)
        for record in self:
            alias_team = self.env['memberspace.alias'].search([
                ('shift_id', '=', record.shift_template_id.id),
                ('type', '=', 'team')
            ], limit=1)
            if alias_team and record.registration_id.is_current_participant:
                alias_team.message_subscribe(
                    partner_ids=[record.registration_id.partner_id.id])
            else:
                alias_team.message_subscribe(
                    partner_ids=[record.registration_id.partner_id.id])
        return res
