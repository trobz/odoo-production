# -*- coding: utf-8 -*-

from openerp import models, fields, api


class MemberSpaceConversation(models.Model):
    _name = 'memberspace.conversation'
    _inherit = ['mail.thread']

    name = fields.Char("Name", required=True)
    memberspace_alias_id = fields.Many2one(
        "memberspace.alias", "Shift Alias", required=True)

    @api.model
    def create(self, vals):
        res = super(MemberSpaceConversation, self).create(vals)
        res.message_follower_ids = \
            res.memberspace_alias_id.message_follower_ids
        return res
