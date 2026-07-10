from odoo import models

GROUP_PURCHASE_MANAGER = "foodcoop_data_role.group_Purchase_Manager"

PURCHASE_MANAGER_HIDDEN_MENUS = (
    "purchase.menu_product_in_config_purchase",
    "purchase.menu_unit_of_measure_in_config_purchase",
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
