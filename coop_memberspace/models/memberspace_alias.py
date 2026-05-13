from odoo import api, fields, models


class MemberSpaceAlias(models.Model):
    _name = "memberspace.alias"
    _description = "Memberspace Alias"
    _inherit = ["mail.thread"]
    _inherits = {"mail.alias": "alias_id"}

    name = fields.Char(required=True)
    shift_id = fields.Many2one("shift.template", "Shift Template", required=True)
    alias_id = fields.Many2one(
        "mail.alias",
        "Alias",
        ondelete="restrict",
        required=True,
        help="The email address associated with this alias.\
            New emails received will automatically \
            create new conversation assigned to the alias.",
    )
    type = fields.Selection(
        selection=[("coordinator", "Coordinators"), ("team", "Team")],
        default="coordinator",
    )

    @api.model_create_multi
    def create(self, vals_list):
        alias_model_id = self.env["ir.model"]._get("memberspace.conversation").id
        alias_parent_model_id = self.env["ir.model"]._get(self._name).id
        for vals in vals_list:
            vals.setdefault("alias_model_id", alias_model_id)
            vals.setdefault("alias_parent_model_id", alias_parent_model_id)
        memberspace_alias = super(
            MemberSpaceAlias,
            self.with_context(mail_create_nolog=True),
        ).create(vals_list)
        memberspace_alias.alias_id.write(
            {
                "alias_parent_thread_id": memberspace_alias.id,
                "alias_defaults": {"memberspace_alias_id": memberspace_alias.id},
            }
        )
        return memberspace_alias

    def unlink(self):
        # Cascade-delete mail aliases as well
        # as they should not exist without the memberspace alias.
        aliases = self.mapped("alias_id")
        res = super().unlink()
        aliases.unlink()
        return res
