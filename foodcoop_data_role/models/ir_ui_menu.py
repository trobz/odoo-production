from odoo import models

GROUP_PURCHASE_MANAGER = "foodcoop_data_role.group_Purchase_Manager"
PURCHASE_MANAGER_HIDDEN_MENUS = (
    "purchase.menu_product_in_config_purchase",
    "purchase.menu_unit_of_measure_in_config_purchase",
)

# These foodcoop_data_role roles combine the BDM Saisie group with access to
# other apps (POS, Project, Maintenance, ...). coop_membership's
# _is_bdm_profile() restricts any user holding group_membership_bdm_lecture
# (implied by group_membership_bdm_saisie) to the single "Members" root menu,
# which is only meant for the plain BDMLecture/BDMPresence/BDMSaisie/
# BadgeReader roles, not for these composite roles.
NON_BDM_PROFILE_GROUP_XMLIDS = (
    "foodcoop_data_role.group_Member_Manager",
    "foodcoop_data_role.group_Foodcoop_Admin",
)


class IrUiMenu(models.Model):
    _inherit = "ir.ui.menu"

    def _load_menus_blacklist(self):
        blacklist = super()._load_menus_blacklist()
        user = self.env.user
        if not user._is_admin() and user.has_group(GROUP_PURCHASE_MANAGER):
            for xmlid in PURCHASE_MANAGER_HIDDEN_MENUS:
                menu = self.env.ref(xmlid, raise_if_not_found=False)
                if menu:
                    blacklist.append(menu.id)
        return blacklist

    def _is_bdm_profile(self):
        user = self.env.user
        if any(user.has_group(xmlid) for xmlid in NON_BDM_PROFILE_GROUP_XMLIDS):
            return False
        return super()._is_bdm_profile()
