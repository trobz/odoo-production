# Copyright 2019 Coop IT Easy SCRLfs
# @author Pierrick Brun <pierrick.brun@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.model
    def get_views(self, views, options=None):
        res = super().get_views(views, options)
        user = self.env.user
        if user.has_group("foodcoop_data_role.group_member_accountant_restrict"):
            for _view_type, view_data in res.get("views", {}).items():
                if view_data.get("toolbar", {}).get("action"):
                    del view_data["toolbar"]["action"]
        return res
