from odoo import Command, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    def create_memberspace_user(self):
        """
        Assign new users to Member role
        """
        users = super().create_memberspace_user()
        role = self.env.ref(
            "foodcoop_data_role_memberspace.res_users_role_Member",
            raise_if_not_found=False,
        )
        if not role:
            return users
        for user in users:
            user.role_line_ids = [Command.create({"role_id": role.id})]
        return users
