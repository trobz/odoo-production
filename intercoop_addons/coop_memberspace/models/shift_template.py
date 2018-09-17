# -*- coding: utf-8 -*-

from openerp import models, api, fields


class ShiftTemplate(models.Model):
    _inherit = 'shift.template'

    memberspace_alias_ids = fields.One2many(
        'memberspace.alias', 'shift_id', "Memberspace Alias")

    @api.model
    def create(self, vals):
        res = super(ShiftTemplate, self).create(vals)
        # generate automatically an alias
        name = res.name + (res.start_datetime and
            (' ' + res.start_datetime) or '')
        alias_prefix = "_".join(
            name.replace('-', '').replace('.', '').split(' '))
                # 1. for the coordinators of the team
        memberspace_alias_leader = self.env['memberspace.alias'].create({
            'name': name + ' - Leader',
            'shift_id': res.id,
            'alias_name': '%s_leader' % (alias_prefix),
            'type': 'coordinator'
        })
        memberspace_alias_leader.message_subscribe(
            partner_ids=res.user_ids.ids)
                # 2. for the members of the team (include coordinators))
        members = res.registration_ids.filtered(
            lambda r: r.is_current_participant).mapped('partner_id')
        members |= res.user_ids
        memberspace_alias_team = self.env['memberspace.alias'].create({
            'name': name + ' - Team',
            'shift_id': res.id,
            'alias_name': '%s_team' % (alias_prefix),
            'type': 'team'
        })
        memberspace_alias_team.message_subscribe(partner_ids=members.ids)
        return res

    @api.multi
    def write(self, vals):
        if 'user_ids' in vals:
            for record in self:
                record.message_unsubscribe(partner_ids=record.user_ids.ids)
        res = super(ShiftTemplate, self).write(vals)
        if 'user_ids' in vals:
            self.message_subscribe(partner_ids=res.user_ids.ids)
        return res
