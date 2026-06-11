from odoo import models


class ResUsers(models.Model):
    _inherit = "res.users"

    def _load_pos_data(self, data):
        res = super()._load_pos_data(data)
        domain = self._load_pos_data_domain(data)
        user = self.search(domain, limit=1)
        user_groups = user.groups_id.ids

        access_ctrl_buttons_group = self.env.ref(
            "coop_pos_access.pos_access_control_buttons_group"
        )
        res["data"][0].update(
            hasGroupAccessControlButtons=access_ctrl_buttons_group.id in user_groups,
        )
        return res
