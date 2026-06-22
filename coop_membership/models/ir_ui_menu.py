from odoo import models


class IrUiMenu(models.Model):
    _inherit = "ir.ui.menu"

    def _load_menus_blacklist(self):
        res = super()._load_menus_blacklist()
        if self.env.user.has_group("coop_membership.group_membership_bdm_lecture"):
            hidden_refs = [
                "coop_membership.menu_res_partner_former_member",
                "coop_membership.menu_res_partner_former_associated_people",
                "coop_membership.menu_shift_attendance_entry",
                "coop_membership.menu_shift_seats_available",
            ]
            for xml_id in hidden_refs:
                menu = self.env.ref(xml_id, raise_if_not_found=False)
                if menu:
                    res.append(menu.id)
        return res
