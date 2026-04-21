from odoo import Command, api, models

from odoo.addons.base_user_role.models.user import ResUsers as BURUsers


class ResUsers(models.Model):
    _inherit = "res.users"

    @api.model
    def check_access_ui_super_groups(self, resp):
        super().check_access_ui_super_groups(resp)
        if resp.get("result") == "saisie_group_partner":
            resp["actionMenuItems"] = True
            if self.has_group("foodcoop_data_role.group_Member_Manager"):
                resp["result"] = False
                resp["o_mail_Chatter_top"] = True
        if self.has_group("coop_membership.group_membership_action_sidebar"):
            resp["result"] = False
        return resp

    @api.model
    def set_groups_from_roles(self, force=False):
        user_types_category = self.env.ref(
            "base.module_category_user_type", raise_if_not_found=False
        )
        user_types_groups = (
            self.env["res.groups"].search(
                [("category_id", "=", user_types_category.id)]
            )
            if user_types_category
            else False
        )
        role_groups = {}
        for role in self.mapped("role_line_ids.role_id"):
            role_groups[role] = list(
                set(
                    role.group_id.ids
                    + role.implied_ids.ids
                    + role.trans_implied_ids.ids
                )
            )
        for user in self:
            if not user.role_line_ids and not force:
                continue
            group_ids = []
            for role_line in user.role_line_ids:
                role = role_line.role_id
                if role:
                    group_ids += role_groups[role]
            group_ids = list(set(group_ids))
            groups_to_add = list(set(group_ids) - set(user.groups_id.ids))
            if set(groups_to_add) & set(user_types_groups.ids):
                groups_to_remove = list(set(user.groups_id.ids) - set(group_ids))
            else:
                groups_to_remove = list(
                    set(user.groups_id.ids)
                    - set(group_ids)
                    - set(user_types_groups.ids)
                )
            to_add = [Command.link(gr) for gr in groups_to_add]
            to_remove = [Command.unlink(gr) for gr in groups_to_remove]
            groups = to_remove + to_add
            if groups:
                vals = {
                    "groups_id": groups,
                }
                _res = super(BURUsers, user).write(vals)
        return True
