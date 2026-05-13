from odoo import api, fields, models


class MemberSpaceConversation(models.Model):
    _name = "memberspace.conversation"
    _description = "Memberspace Conversation"
    _inherit = ["mail.thread"]

    name = fields.Char(required=True)
    memberspace_alias_id = fields.Many2one(
        "memberspace.alias", "Shift Alias", required=True
    )

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        alias = res.memberspace_alias_id
        partners = alias.shift_id.user_ids
        if alias.type == "team":
            partners |= alias.shift_id.registration_ids.filtered(
                lambda r: r.is_current_participant
            ).mapped("partner_id")
        res.message_subscribe(partner_ids=partners.ids)
        return res
