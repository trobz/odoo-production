from odoo import api, models
from odoo.addons.base_user_role.models.user import ResUsers as BURUsers


class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.multi
    def check_access_buttons(self, res_model):
        """
        Check group current user to hide buttons
        """
        res = super(ResUsers, self).check_access_buttons(res_model)
        # F#T59241 - Add "Print Badge" function to "Member Manager" role
        if res == 'saisie_group_partner' and self.has_group(
                'foodcoop_data_role.group_Member_Manager'):
            res = False
        return res

    @api.multi
    def set_groups_from_roles(self, force=False):
        """Set (replace) the groups following the roles defined on users.
        If no role is defined on the user, its groups are let untouched unless
        the `force` parameter is `True`.
        """
        user_types_category = self.env.ref('base.module_category_user_type', raise_if_not_found=False)
        user_types_groups = self.env['res.groups'].search(
            [('category_id', '=', user_types_category.id)]) if user_types_category else False
        role_groups = {}
        # We obtain all the groups associated to each role first, so that
        # it is faster to compare later with each user's groups.
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
            for role_line in user._get_applicable_roles():
                role = role_line.role_id
                if role:
                    group_ids += role_groups[role]
            group_ids = list(set(group_ids))  # Remove duplicates IDs
            groups_to_add = list(set(group_ids) - set(user.groups_id.ids))
            groups_to_remove = list(set(user.groups_id.ids) - set(group_ids) - set(user_types_groups.ids))
            to_add = [(4, gr) for gr in groups_to_add]
            to_remove = [(3, gr) for gr in groups_to_remove]
            groups = to_remove + to_add
            if groups:
                vals = {
                    "groups_id": groups,
                }
                super(BURUsers, user).write(vals)
        return True
